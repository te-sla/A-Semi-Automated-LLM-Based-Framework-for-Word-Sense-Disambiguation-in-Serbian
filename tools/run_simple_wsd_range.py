from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import torch
from sentence_transformers import SentenceTransformer
from webanno_spacy_converter.parsers.tsv_parser_v3 import WebAnnoLEXISParser

from config import (
	ANNOTATION_CHUNKS,
	DATA_DIR,
	OUTPUT_DIR,
	SENSE_AINOTES_FIELD,
	SENSE_COUNT_FIELD,
	SENSE_ID_FIELD,
	SENSE_LIST_FIELD,
	SENSE_ORIGIN,
	SIMPLE_WSD_MODEL_PRESETS,
	STATS_DIR,
	S_ID,
)
from data_loader import load_sense_repo_by_round
from preprocessing import (
	get_mwe_filtered_senses,
	get_mwe_tokens,
	get_token_senses,
	mark_mwe,
	mark_token,
	token_is_content_word,
	token_is_not_in_mwe,
)
from simple_wsd import _candidate_text_from_sense, _format_similarity_note
from writers import CustomWebAnnoTSVWriter, InceptionWebAnnoTSVWriter


SUFFIX_RE = re.compile(r"\[\d+\]$")


@dataclass
class WsdTask:
	kind: str
	context: str
	candidate_texts: List[str]
	senses_records: List[Dict[str, Any]]
	tokens: List[Any]
	n: int | None = None


def load_first_n_sentences(limit: int):
	sentences = []
	for _chunk_begin, _chunk_end, filename in ANNOTATION_CHUNKS:
		if len(sentences) >= limit:
			break
		parser = WebAnnoLEXISParser(DATA_DIR / filename)
		available = parser.parse()
		needed = limit - len(sentences)
		for sentence in available[:needed]:
			new_sentence_index = len(sentences) + 1
			for token in sentence.tokens:
				token.sentence_index = new_sentence_index
			sentences.append(sentence)
	return sentences


def add_new_sense_for_mwe(tokens: Sequence[Any], n: int) -> None:
	for token in tokens:
		token.add_layer(SENSE_ID_FIELD, f"NEW_SENSE[{n}]")
		token.add_layer(SENSE_COUNT_FIELD, f"0[{n}]")
		token.add_layer(SENSE_ORIGIN, "None")


def add_new_sense_for_token(token: Any) -> None:
	token.add_layer(SENSE_ID_FIELD, "NEW_SENSE")
	token.add_layer(SENSE_COUNT_FIELD, "0")
	token.add_layer(SENSE_ORIGIN, "None")


def collect_tasks(sentences, senses_df) -> Tuple[List[WsdTask], Dict[str, int]]:
	tasks: List[WsdTask] = []
	stats = {
		"sentences": len(sentences),
		"mwe_tasks": 0,
		"token_tasks": 0,
		"new_mwe_senses": 0,
		"new_token_senses": 0,
	}
	n = 2000

	for sentence in sentences:
		for mwe in getattr(sentence, "mwes", []):
			senses_df_slice = get_mwe_filtered_senses(mwe, senses_df)
			mwe_tokens = get_mwe_tokens(sentence, mwe)
			if senses_df_slice is None or senses_df_slice.empty:
				add_new_sense_for_mwe(mwe_tokens, n)
				stats["new_mwe_senses"] += 1
				n += 1
				continue

			senses_records = senses_df_slice.to_dict(orient="records")
			if not senses_records:
				add_new_sense_for_mwe(mwe_tokens, n)
				stats["new_mwe_senses"] += 1
				n += 1
				continue

			tasks.append(
				WsdTask(
					kind="mwe",
					context=mark_mwe(mwe, sentence),
					candidate_texts=[_candidate_text_from_sense(sense) for sense in senses_records],
					senses_records=senses_records,
					tokens=mwe_tokens,
					n=n,
				)
			)
			stats["mwe_tasks"] += 1
			n += 1

		for token in sentence.tokens:
			if not (token_is_content_word(token) and token_is_not_in_mwe(token)):
				continue

			target_word = token.layers.get("value_4", "_")
			if target_word == "_" or not target_word:
				continue
			if str(target_word)[0].isdigit():
				continue

			senses_df_slice = get_token_senses(token, sentence, senses_df)
			if senses_df_slice is None or senses_df_slice.empty:
				add_new_sense_for_token(token)
				stats["new_token_senses"] += 1
				continue

			senses_records = senses_df_slice.to_dict(orient="records")
			if not senses_records:
				add_new_sense_for_token(token)
				stats["new_token_senses"] += 1
				continue

			tasks.append(
				WsdTask(
					kind="token",
					context=mark_token(token, sentence),
					candidate_texts=[_candidate_text_from_sense(sense) for sense in senses_records],
					senses_records=senses_records,
					tokens=[token],
				)
			)
			stats["token_tasks"] += 1

	return tasks, stats


def with_text_prefix(text: str, text_prefix: str) -> str:
	if not text_prefix:
		return str(text)
	text = str(text)
	return text if text.startswith(text_prefix) else f"{text_prefix}{text}"


def encode_unique_texts(
	model: SentenceTransformer,
	tasks_by_round: Dict[int, List[WsdTask]],
	*,
	text_prefix: str,
	normalize_embeddings: bool,
	batch_size: int,
) -> Dict[str, torch.Tensor]:
	unique_texts = sorted(
		{
			text
			for tasks in tasks_by_round.values()
			for task in tasks
			for text in (task.context, *task.candidate_texts)
		}
	)
	print(f"Encoding {len(unique_texts)} unique texts with batch_size={batch_size}...", flush=True)
	prefixed_texts = [with_text_prefix(text, text_prefix) for text in unique_texts]
	embeddings = model.encode(
		prefixed_texts,
		batch_size=batch_size,
		convert_to_tensor=True,
		normalize_embeddings=normalize_embeddings,
		show_progress_bar=True,
	)
	if hasattr(embeddings, "detach"):
		embeddings = embeddings.detach()
	if hasattr(embeddings, "cpu"):
		embeddings = embeddings.cpu()
	return {text: embeddings[index] for index, text in enumerate(unique_texts)}


def score_candidates(context_embedding: torch.Tensor, candidate_embeddings: torch.Tensor, normalize_embeddings: bool):
	if normalize_embeddings:
		return (candidate_embeddings @ context_embedding).tolist()
	return torch.nn.functional.cosine_similarity(candidate_embeddings, context_embedding.unsqueeze(0)).tolist()


def apply_tasks(
	tasks: Sequence[WsdTask],
	embeddings_by_text: Dict[str, torch.Tensor],
	*,
	origin_model: str,
	normalize_embeddings: bool,
	notes_top_k: int,
) -> None:
	for task in tasks:
		context_embedding = embeddings_by_text[task.context]
		candidate_embeddings = torch.stack([embeddings_by_text[text] for text in task.candidate_texts])
		raw_scores = score_candidates(context_embedding, candidate_embeddings, normalize_embeddings)
		scores_sorted = sorted(enumerate(raw_scores), key=lambda item: item[1], reverse=True)
		best_index = scores_sorted[0][0]
		notes = _format_similarity_note(scores_sorted, task.candidate_texts, task.senses_records, notes_top_k)
		sense_ids = [
			str(record.get(S_ID, ""))
			for record in task.senses_records
			if record.get(S_ID) is not None
		]
		senses_candidates = ";".join(sense_ids)
		selected_sense = task.senses_records[best_index]
		sense_id_value = str(selected_sense.get(S_ID, "NEW_SENSE"))
		sense_count_value = str(len(task.senses_records))

		if task.kind == "mwe":
			assert task.n is not None
			for token in task.tokens:
				token.add_layer(SENSE_ID_FIELD, f"{sense_id_value}[{task.n}]")
				token.add_layer(SENSE_COUNT_FIELD, f"{sense_count_value}[{task.n}]")
				token.add_layer(SENSE_LIST_FIELD, f"{senses_candidates}[{task.n}]")
				token.add_layer(SENSE_AINOTES_FIELD, f"{notes}[{task.n}]")
				token.add_layer(SENSE_ORIGIN, origin_model)
			continue

		token = task.tokens[0]
		token.add_layer(SENSE_ID_FIELD, sense_id_value)
		token.add_layer(SENSE_AINOTES_FIELD, notes)
		token.add_layer(SENSE_COUNT_FIELD, sense_count_value)
		token.add_layer(SENSE_LIST_FIELD, senses_candidates)
		token.add_layer(SENSE_ORIGIN, origin_model)


def save_outputs(sentences, *, origin_model: str, round_number: int, limit: int) -> Dict[str, str]:
	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
	base = OUTPUT_DIR / f"LexiSense_0001_{limit:04d}_{origin_model}_round{round_number}.tsv"
	inception = OUTPUT_DIR / f"LexiSense_Inception_0001_{limit:04d}_{origin_model}_round{round_number}.tsv"
	CustomWebAnnoTSVWriter(sentences).save(base)
	InceptionWebAnnoTSVWriter(sentences).save(inception)
	return {"base": str(base), "inception": str(inception)}


def clean_sense_id(value: str) -> str:
	return SUFFIX_RE.sub("", str(value or ""))


def extract_predictions(sentences) -> Dict[Tuple[Any, ...], Dict[str, Any]]:
	predictions: Dict[Tuple[Any, ...], Dict[str, Any]] = {}
	for sentence_index, sentence in enumerate(sentences, start=1):
		in_mwe = {token_index for mwe in getattr(sentence, "mwes", []) for token_index in mwe.token_indices}
		for mwe in getattr(sentence, "mwes", []):
			first_token = sentence.tokens[mwe.token_indices[0]]
			sense_id = clean_sense_id(first_token.layers.get(SENSE_ID_FIELD, ""))
			key = (sentence_index, "mwe", tuple(mwe.token_indices))
			predictions[key] = {
				"sentence_index": sentence_index,
				"kind": "mwe",
				"target": " ".join(sentence.tokens[index].text for index in mwe.token_indices),
				"sense_id": sense_id,
			}
		for token in sentence.tokens:
			if token.token_index in in_mwe:
				continue
			sense_id = clean_sense_id(token.layers.get(SENSE_ID_FIELD, ""))
			if not sense_id or sense_id in {"_", "*"}:
				continue
			key = (sentence_index, "token", token.token_index)
			predictions[key] = {
				"sentence_index": sentence_index,
				"kind": "token",
				"target": token.text,
				"sense_id": sense_id,
			}
	return predictions


def write_round_comparison(round_predictions: Dict[int, Dict[Tuple[Any, ...], Dict[str, Any]]], *, origin_model: str, limit: int):
	pred1 = round_predictions[1]
	pred2 = round_predictions[2]
	keys1 = set(pred1)
	keys2 = set(pred2)
	shared = sorted(keys1 & keys2)
	differences = []
	same_count = 0
	for key in shared:
		row1 = pred1[key]
		row2 = pred2[key]
		if row1["sense_id"] == row2["sense_id"]:
			same_count += 1
			continue
		differences.append(
			{
				"sentence_index": row1["sentence_index"],
				"kind": row1["kind"],
				"target": row1["target"],
				"round1_sense_id": row1["sense_id"],
				"round2_sense_id": row2["sense_id"],
			}
		)

	STATS_DIR.mkdir(parents=True, exist_ok=True)
	summary_path = STATS_DIR / f"{origin_model}_0001_{limit:04d}_round_comparison_summary.json"
	diff_path = STATS_DIR / f"{origin_model}_0001_{limit:04d}_round_differences.csv"
	summary = {
		"origin_model": origin_model,
		"limit": limit,
		"round1_target_count": len(pred1),
		"round2_target_count": len(pred2),
		"shared_target_count": len(shared),
		"same_sense_count": same_count,
		"different_sense_count": len(differences),
		"only_round1_count": len(keys1 - keys2),
		"only_round2_count": len(keys2 - keys1),
		"difference_examples": differences[:25],
	}
	summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
	with diff_path.open("w", encoding="utf-8", newline="") as handle:
		writer = csv.DictWriter(
			handle,
			fieldnames=["sentence_index", "kind", "target", "round1_sense_id", "round2_sense_id"],
		)
		writer.writeheader()
		writer.writerows(differences)
	return {"summary": str(summary_path), "differences": str(diff_path), "payload": summary}


def main() -> int:
	for stream in (sys.stdout, sys.stderr):
		if hasattr(stream, "reconfigure"):
			stream.reconfigure(encoding="utf-8", errors="replace")

	parser = argparse.ArgumentParser(description="Run SimpleWSD for the first N sentences across both sense-repo rounds.")
	parser.add_argument("--tag", default="mling", choices=sorted(SIMPLE_WSD_MODEL_PRESETS))
	parser.add_argument("--limit", type=int, default=600)
	parser.add_argument("--round", dest="rounds", type=int, action="append", choices=[1, 2])
	parser.add_argument("--batch-size", type=int, default=16)
	parser.add_argument("--notes-top-k", type=int, default=3)
	args = parser.parse_args()

	rounds = args.rounds or [1, 2]
	preset = SIMPLE_WSD_MODEL_PRESETS[args.tag]
	model_name = preset["model_name"]
	origin_model = preset["origin"]
	text_prefix = preset.get("text_prefix", "")
	normalize_embeddings = preset.get("normalize_embeddings", False)

	start_time = time.time()
	print(f"Running SimpleWSD tag={args.tag} origin={origin_model} model={model_name}", flush=True)
	print(f"Sentence range: 0001-{args.limit:04d}; rounds={rounds}", flush=True)
	print(f"Torch CUDA available: {torch.cuda.is_available()}", flush=True)

	jobs = {}
	tasks_by_round = {}
	for round_number in rounds:
		print(f"Preparing round {round_number}...", flush=True)
		sentences = load_first_n_sentences(args.limit)
		senses_df = load_sense_repo_by_round(round_number=round_number)
		tasks, stats = collect_tasks(sentences, senses_df)
		jobs[round_number] = {"sentences": sentences, "stats": stats}
		tasks_by_round[round_number] = tasks
		print(f"Round {round_number} task stats: {stats}", flush=True)

	model = SentenceTransformer(model_name)
	embeddings_by_text = encode_unique_texts(
		model,
		tasks_by_round,
		text_prefix=text_prefix,
		normalize_embeddings=normalize_embeddings,
		batch_size=args.batch_size,
	)

	outputs = {}
	round_predictions = {}
	for round_number in rounds:
		print(f"Scoring and writing round {round_number}...", flush=True)
		apply_tasks(
			tasks_by_round[round_number],
			embeddings_by_text,
			origin_model=origin_model,
			normalize_embeddings=normalize_embeddings,
			notes_top_k=args.notes_top_k,
		)
		sentences = jobs[round_number]["sentences"]
		outputs[round_number] = save_outputs(
			sentences,
			origin_model=origin_model,
			round_number=round_number,
			limit=args.limit,
		)
		round_predictions[round_number] = extract_predictions(sentences)
		print(f"Round {round_number} outputs: {outputs[round_number]}", flush=True)

	comparison = None
	if 1 in round_predictions and 2 in round_predictions:
		comparison = write_round_comparison(round_predictions, origin_model=origin_model, limit=args.limit)
		print(f"Comparison summary: {comparison['payload']}", flush=True)
		print(f"Comparison files: summary={comparison['summary']} differences={comparison['differences']}", flush=True)

	print(
		json.dumps(
			{
				"elapsed_seconds": round(time.time() - start_time, 2),
				"outputs": outputs,
				"comparison": comparison,
			},
			ensure_ascii=False,
			indent=2,
		),
		flush=True,
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
