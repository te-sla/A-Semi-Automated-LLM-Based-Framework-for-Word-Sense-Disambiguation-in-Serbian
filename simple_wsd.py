"""Minimal zero-shot word sense disambiguation using sentence-transformer similarities."""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sentence_transformers import SentenceTransformer, util

from config import (
	L_LEMMA,
	S_DEFINITION,
	S_ID,
	SENSE_AINOTES_FIELD,
	SENSE_COUNT_FIELD,
	SENSE_ID_FIELD,
	SENSE_LIST_FIELD,
	SENSE_ORIGIN,
)
from preprocessing import (
	get_mwe_filtered_senses,
	get_mwe_tokens,
	get_token_senses,
	mark_mwe,
	mark_token,
	token_is_content_word,
	token_is_not_in_mwe,
	token_is_not_in_ne_not_in_filter,
)


def _ensure_model(
	model: Optional[SentenceTransformer],
	model_name: str,
) -> SentenceTransformer:
	"""Return a ready-to-use sentence transformer model."""
	return model if model is not None else SentenceTransformer(model_name)


def _compute_similarity_scores(
	model: SentenceTransformer,
	sentence: str,
	candidate_texts: Sequence[str],
) -> List[Tuple[int, float]]:
	"""Compute cosine similarity scores for candidate glosses.

	Returns
	-------
	List of tuples `(candidate_index, similarity_score)` preserving original order.
	"""
	if not candidate_texts:
		return []

	sentence_embedding = model.encode(sentence, convert_to_tensor=True)
	gloss_embeddings = model.encode(list(candidate_texts), convert_to_tensor=True)

	similarity_tensor = util.cos_sim(sentence_embedding, gloss_embeddings).squeeze(0)
	if hasattr(similarity_tensor, "detach"):
		similarity_tensor = similarity_tensor.detach()
	if hasattr(similarity_tensor, "cpu"):
		similarity_tensor = similarity_tensor.cpu()
	scores = similarity_tensor.tolist()
	if isinstance(scores, float):
		scores = [scores]
	return list(enumerate(scores))


def _shorten(text: str, max_length: int = 120) -> str:
	"""Return a text trimmed to the requested length with ellipsis."""
	text = text.replace("\n", " ").strip()
	if len(text) <= max_length:
		return text
	return text[: max_length - 1] + "…"


def _candidate_text_from_sense(sense: Dict[str, Any]) -> str:
	"""Choose the best available textual representation of a sense."""
	for key in (S_DEFINITION, "definition", "gloss"):
		value = sense.get(key)
		if value:
			text = str(value).strip()
			if text:
				return text
	lemma = sense.get(L_LEMMA, "")
	if lemma:
		lemma_text = str(lemma).strip()
		if lemma_text:
			return lemma_text
	return str(sense.get(S_ID, "unspecified sense"))


def _format_similarity_note(
	scores: List[Tuple[int, float]],
	candidate_texts: Sequence[str],
	senses: Sequence[Dict[str, Any]],
	max_items: int = 3,
) -> str:
	"""Create a compact note summarizing top similarity scores."""
	if not scores:
		return "simple_wsd: no scored candidates"
	parts: List[str] = []
	for index, score in scores[:max_items]:
		sense_id = str(senses[index].get(S_ID, ""))
		description = _shorten(candidate_texts[index])
		parts.append(f"{sense_id}:{score:.4f}::{description}")
	return "simple_wsd - " + " - ".join(parts)


def disambiguate_sentence(
	sentence: str,
	glosses: Sequence[str],
	model: Optional[SentenceTransformer] = None,
	model_name: str = "all-MiniLM-L6-v2",
) -> List[Tuple[str, float]]:
	"""Return glosses scored by cosine similarity to the sentence embedding.

	Parameters
	----------
	sentence:
		Sentence containing the ambiguous target word.
	glosses:
		Candidate sense definitions.
	model:
		Optional pre-loaded SentenceTransformer instance.
	model_name:
		Sentence transformer checkpoint to load (used only when *model* is None).

	Returns
	-------
	List of (gloss, similarity score) pairs sorted from highest to lowest score.
	"""
	if not sentence.strip():
		raise ValueError("Sentence must not be empty.")
	if not glosses:
		raise ValueError("At least one gloss definition is required.")

	model_instance = _ensure_model(model, model_name)
	scores = _compute_similarity_scores(model_instance, sentence, list(glosses))

	# Sort in descending order of similarity
	ordered = sorted(scores, key=lambda item: item[1], reverse=True)
	return [(list(glosses)[idx], score) for idx, score in ordered]


def process_senses_with_simple_wsd(
	sentences,
	senses_df,
	*,
	model: Optional[SentenceTransformer] = None,
	model_name: str = "all-MiniLM-L6-v2",
	origin_model: str = "simple_wsd",
	n: int = 2000,
	progress: bool = True,
	notes_top_k: int = 3,
):
	"""Annotate sentences using cosine similarity between sentence and gloss embeddings."""
	model_instance = _ensure_model(model, model_name)
	origin_first = "FIRST"
	sentence_total = len(sentences)
	processed_count = 0

	def _blank_wsd_layers(token):
		"""Blank WSD-related layers for tokens we skip."""
		token.add_layer(SENSE_ID_FIELD, "_")
		token.add_layer(SENSE_COUNT_FIELD, "0")
		token.add_layer(SENSE_LIST_FIELD, "_")
		token.add_layer(SENSE_AINOTES_FIELD, "_")
		token.add_layer(SENSE_ORIGIN, "_")

	for sentence in sentences:
		# --- Multiword expressions ---
		for mwe in getattr(sentence, "mwes", []):
			senses_df_slice = get_mwe_filtered_senses(mwe, senses_df)
			if senses_df_slice is None or senses_df_slice.empty:
				mwe_tokens = get_mwe_tokens(sentence, mwe)
				for token in mwe_tokens:
					token.add_layer(SENSE_ID_FIELD, f"NEW_SENSE[{n}]")
					token.add_layer(SENSE_COUNT_FIELD, f"0[{n}]")
					token.add_layer(SENSE_ORIGIN, "None")
				n += 1
				continue

			senses_records = senses_df_slice.to_dict(orient="records")
			if not senses_records:
				mwe_tokens = get_mwe_tokens(sentence, mwe)
				for token in mwe_tokens:
					token.add_layer(SENSE_ID_FIELD, f"NEW_SENSE[{n}]")
					token.add_layer(SENSE_COUNT_FIELD, f"0[{n}]")
					token.add_layer(SENSE_ORIGIN, "None")
				n += 1
				continue

			candidate_texts = [_candidate_text_from_sense(sense) for sense in senses_records]
			scores = _compute_similarity_scores(model_instance, mark_mwe(mwe, sentence), candidate_texts)
			scores_sorted = sorted(scores, key=lambda item: item[1], reverse=True)
			if not scores_sorted:
				best_index = 0
				notes = "simple_wsd: fallback to first sense (no text to score)"
				origin = origin_first
			else:
				best_index = scores_sorted[0][0]
				notes = _format_similarity_note(scores_sorted, candidate_texts, senses_records, notes_top_k)
				origin = origin_model

			sense_ids = [str(record.get(S_ID, "")) for record in senses_records if record.get(S_ID) is not None]
			senses_candidates = ";".join(sense_ids)
			mwe_tokens = get_mwe_tokens(sentence, mwe)
			selected_sense = senses_records[best_index] if senses_records else {}
			sense_id_value = str(selected_sense.get(S_ID, "NEW_SENSE")) if senses_records else "NEW_SENSE"
			sense_count_value = str(len(senses_records))
			for token in mwe_tokens:
				token.add_layer(SENSE_ID_FIELD, f"{sense_id_value}[{n}]")
				token.add_layer(SENSE_COUNT_FIELD, f"{sense_count_value}[{n}]")
				token.add_layer(SENSE_LIST_FIELD, f"{senses_candidates}[{n}]")
				token.add_layer(SENSE_AINOTES_FIELD, f"{notes}[{n}]")
				token.add_layer(SENSE_ORIGIN, origin)
			n += 1

		# --- Single tokens ---
		for token in sentence.tokens:
			if not token_is_not_in_mwe(token):
				continue

			# Tokens that are not content words or are filtered out / in NE
			# should explicitly get blank WSD layers so old annotations do not linger.
			if not token_is_content_word(token) or not token_is_not_in_ne_not_in_filter(token):
				_blank_wsd_layers(token)
				continue

			target_word = token.layers.get(L_LEMMA, "_")
			if target_word == "_" or not target_word:
				_blank_wsd_layers(token)
				continue
			if target_word[0].isdigit():
				_blank_wsd_layers(token)
				continue

			senses_df_slice = get_token_senses(token, sentence, senses_df)
			senses_records = senses_df_slice.to_dict(orient="records")
			if not senses_records:
				token.add_layer(SENSE_ID_FIELD, "NEW_SENSE")
				token.add_layer(SENSE_COUNT_FIELD, "0")
				token.add_layer(SENSE_ORIGIN, "None")
				continue

			candidate_texts = [_candidate_text_from_sense(sense) for sense in senses_records]
			scores = _compute_similarity_scores(model_instance, mark_token(token, sentence), candidate_texts)
			scores_sorted = sorted(scores, key=lambda item: item[1], reverse=True)
			if not scores_sorted:
				best_index = 0
				notes = "simple_wsd: fallback to first sense (no text to score)"
				origin = origin_first
			else:
				best_index = scores_sorted[0][0]
				notes = _format_similarity_note(scores_sorted, candidate_texts, senses_records, notes_top_k)
				origin = origin_model

			sense_ids = [str(record.get(S_ID, "")) for record in senses_records if record.get(S_ID) is not None]
			senses_candidates = ";".join(sense_ids)
			selected_sense = senses_records[best_index]
			sense_id_value = str(selected_sense.get(S_ID, "NEW_SENSE"))
			token.add_layer(SENSE_ID_FIELD, sense_id_value)
			token.add_layer(SENSE_AINOTES_FIELD, notes)
			token.add_layer(SENSE_COUNT_FIELD, str(len(senses_records)))
			token.add_layer(SENSE_LIST_FIELD, senses_candidates)
			token.add_layer(SENSE_ORIGIN, origin)

		processed_count += 1
		if progress:
			print(f"\rProcessed {processed_count}/{sentence_total} sentences (simple_wsd).", end="")

	return sentences


def pretty_print_results(sentence: str, scored_glosses: Iterable[Tuple[str, float]]) -> None:
	"""Display similarity scores and the predicted sense."""
	print(f"Sentence: {sentence}")
	print("\nSimilarity scores (higher is better):")
	for gloss, score in scored_glosses:
		print(f"  {score:.4f} :: {gloss}")

	if scored_glosses:
		best_gloss, best_score = next(iter(scored_glosses))
		print(f"\nPredicted sense: {best_gloss} (score={best_score:.4f})")


if __name__ == "__main__":
	try:
		sentence_input = input("Enter a sentence containing the ambiguous word (leave blank to use example): ").strip()
		glosses_input = input(
			"Enter glosses separated by '|' (leave blank to use example glosses): "
		).strip()
	except EOFError:
		sentence_input = ""
		glosses_input = ""

	if sentence_input and glosses_input:
		candidate_glosses = [g.strip() for g in glosses_input.split("|") if g.strip()]
	else:
		print("\nUsing built-in example for the word 'bank'.")
		sentence_input = "The fisherman rested on the bank and watched the river flow by."
		candidate_glosses = [
			"A financial institution that deals with money and investments.",
			"The land alongside or sloping down to a river or lake.",
			"To tilt an aircraft laterally when turning.",
		]

	scored = disambiguate_sentence(sentence_input, candidate_glosses)
	pretty_print_results(sentence_input, scored)
