"""
process_senses.py

Reusable functions for processing and annotating sentences with sense information using a language model chain.
Intended for use across different model pipelines (ChatGPT, Gemini, Llama, etc.) for consistency and maintainability.

Usage:
    from process_senses import process_senses_with_chain, default_build_senses_block, parse_json_response_clean, parse_model_output
    annotated_sentences = process_senses_with_chain(sentences, senses_df, chain, origin_model)

Arguments:
    sentences: List of sentence objects (from WebAnnoLEXISParser or similar)
    senses_df: DataFrame with sense repository
    chain: LLM chain (e.g., LangChain pipeline)
    origin_model: String label for the model (e.g., 'ChatGPT', 'Gemini', etc.)
    build_senses_block: (optional) Function to format senses for the prompt
    parse_json_response_clean: (optional) Function to parse LLM output
    n: (optional) Starting index for multi-token entities (default 2000)

Returns:
    List of annotated sentence objects (with sense layers added)
"""

import re
import json
import time
from writers import CustomWebAnnoTSVWriter, IncetprionWebAnnoTSVWriter
from config import S_ID, SENSE_ID_FIELD, SENSE_COUNT_FIELD, SENSE_LIST_FIELD, SENSE_AINOTES_FIELD, SENSE_ORIGIN, L_LEMMA
from preprocessing import (
    get_mwe_tokens, mark_mwe, get_mwe_filtered_senses, get_token_senses,
    mark_token, token_is_content_word, token_is_not_in_ne_not_in_filter, token_is_not_in_mwe
)

MAX_HALLUCINATION_RETRIES = 3

# --- Helper Functions ---
def default_build_senses_block(senses):
    """
    Build a numbered list of senses for the prompt.
    Args:
        senses: List of sense dicts with 'senseID' and 'definition'.
    Returns:
        str: Numbered senses block for LLM prompt.
    """
    lines = [f"{i}. ID: {sense['senseID']} — {sense['definition']}" for i, sense in enumerate(senses, start=1)]
    return "\n".join(lines)

def parse_json_response_clean(text):
    """
    Parse and clean the LLM's JSON response for sense disambiguation.
    Args:
        text: Raw LLM output (JSON or fallback text).
    Returns:
        dict: { 'sense_id': ..., 'explanation': ... }
    """
    def clean(s):
        return " ".join(s.replace("\n", " ").replace("\r", " ").replace("\t", " ").split())
    try:
        parsed = json.loads(text)
        return {
            "sense_id": parsed.get("sense_id", "MISSING"),
            "explanation": clean(parsed.get("explanation", ""))
        }
    except json.JSONDecodeError:
        return {
            "sense_id": "PARSE_ERROR",
            "explanation": clean(text)
        }


def _normalize_sense_id(value):
    if value is None:
        return ""
    return str(value).strip()


def _normalize_notes(value):
    if value is None:
        return ""
    return str(value).strip()


def _invoke_chain_with_validation(chain, payload, parse_fn, valid_ids, *, time_delay=0, max_retries=MAX_HALLUCINATION_RETRIES):
    """Invoke the chain with retries, guarding against hallucinated sense IDs."""
    last_notes = ""
    for attempt in range(1, max_retries + 1):
        response = chain.invoke(payload)
        if time_delay > 0:
            time.sleep(time_delay)
        parsed = parse_fn(response)
        sense_id = _normalize_sense_id(parsed.get("sense_id"))
        notes = _normalize_notes(parsed.get("explanation"))
        if sense_id and (sense_id == "NEW_SENSE" or sense_id in valid_ids):
            return sense_id, notes, False
        last_notes = notes
    failure_message = f"Failed due to hallucination after {max_retries} attempts."
    combined_notes = f"{last_notes} | {failure_message}" if last_notes else failure_message
    return "NEW_SENSE", combined_notes, True

def parse_model_output(text):
    """
    Parse the model output containing JSON-formatted WSD decisions, even if extra text is present.
    Returns a dict with 'sense_id' and 'explanation', or fallback values.
    """
    def clean(s):
        return " ".join(s.replace("\n", " ").replace("\r", " ").replace("\t", " ").split())
    try:
        # Extract the JSON block using a permissive regex
        json_match = re.search(r'\{.*?\}', text, re.DOTALL)
        if not json_match:
            raise ValueError("No valid JSON found")
        json_text = json_match.group(0)
        parsed = json.loads(json_text)
        return {
            "sense_id": parsed.get("sense_id", "MISSING").strip(),
            "explanation": clean(parsed.get("explanation", ""))
        }
    except Exception:
        return {
            "sense_id": "PARSE_ERROR",
            "explanation": clean(text)
        }

# --- Main Processing Function ---
def process_senses_with_chain(
    sentences,
    senses_df,
    chain,
    origin_model,
    build_senses_block=default_build_senses_block,
    parse_json_response_clean=parse_model_output,
    n=2000,
    time_delay=0
):
    """
    Annotate sentences with sense information using a language model chain.
    Handles both multiword expressions (MWEs) and single tokens, adding sense layers to each token.

    Args:
        sentences: List of sentence objects to annotate.
        senses_df: DataFrame with sense repository.
        chain: LLM chain for sense disambiguation.
        origin_model: String label for the model (e.g., 'ChatGPT', 'Gemini', etc.)
        build_senses_block: Function to format senses for the prompt (default: default_build_senses_block).
        parse_json_response_clean: Function to parse LLM output (default: parse_model_output).
        n: Starting index for multi-token entities (default 2000)
        time_delay: Time delay in seconds between requests (default 0s) - Note this importnat whan model is limited in the number of tokens or requests per  minute, like free tier of Gemini.
    
    Returns:
        List of annotated sentence objects (with sense layers added).
    """
    origin_first = "FIRST"
    nuber_of_sentences = len(sentences)
    current_sentence = 0

    def _blank_wsd_layers(token):
        """Explicitly blank WSD-related layers for tokens we skip.

        This ensures that non-content / filtered / non-MWE tokens do not
        accidentally keep stale WSD annotations from previous runs.
        """
        token.add_layer(SENSE_ID_FIELD, "_")
        token.add_layer(SENSE_COUNT_FIELD, "0")
        token.add_layer(SENSE_LIST_FIELD, "_")
        token.add_layer(SENSE_AINOTES_FIELD, "_")
        token.add_layer(SENSE_ORIGIN, "_")
    for sentence in sentences:
        # Process multiword expressions (MWEs)
        for mwe in sentence.mwes:
            marked_sentence = mark_mwe(mwe, sentence)
            target_word = mwe.lemma
            senses_df_slice = get_mwe_filtered_senses(mwe, senses_df)
            senses_list = senses_df_slice[S_ID].tolist()
            senses_candidates = ";".join(senses_list)
            valid_sense_ids = {_normalize_sense_id(sid) for sid in senses_list}
            senses = senses_df_slice.to_dict(orient="records")
            mwe_tokens = get_mwe_tokens(sentence, mwe)
            if len(senses) == 0:
                for token in mwe_tokens:
                    token.add_layer(SENSE_ID_FIELD, f"NEW_SENSE[{n}]")
                    token.add_layer(SENSE_COUNT_FIELD, f"0[{n}]")
                    token.add_layer(SENSE_ORIGIN, "None")
                n += 1
                continue
            sense_id, notes, hallucinated = _invoke_chain_with_validation(
                chain,
                {
                    "sentence": marked_sentence,
                    "word": target_word,
                    "senses_block": build_senses_block(senses)
                },
                parse_json_response_clean,
                valid_sense_ids,
                time_delay=time_delay
            )
            origin = origin_model
            if sense_id == "NEW_SENSE":
                if not hallucinated:
                    # If the sense_id is "NEW_SENSE" returned by the model, assign first sense and mark origin as "FIRST"
                    sense_id = senses[0][S_ID]
                    origin = origin_first
                else:
                    origin = "None"
            for token in mwe_tokens:
                token.add_layer(SENSE_ID_FIELD, f"{sense_id}[{n}]")
                token.add_layer(SENSE_COUNT_FIELD, f"{len(senses)}[{n}]")
                token.add_layer(SENSE_LIST_FIELD, f"{senses_candidates}[{n}]")
                token.add_layer(SENSE_AINOTES_FIELD, f"{notes}[{n}]")
                token.add_layer(SENSE_ORIGIN, origin)
            n += 1
        # Process single tokens
        for token in sentence.tokens:
            # If token is part of an MWE, it is already handled in the MWE loop
            if not token_is_not_in_mwe(token):
                continue

            # Tokens that are not content words or are filtered out / in NE
            # should explicitly get blank WSD layers so old annotations do not linger.
            if (not token_is_content_word(token)) or (not token_is_not_in_ne_not_in_filter(token)):
                _blank_wsd_layers(token)
                continue

            # From here on, token is a simple content word we want to send to LLM
            marked_sentence = mark_token(token, sentence)
            target_word = token.layers.get(L_LEMMA, "_")
            if target_word == "_":
                # Skip tokens that do not have a lemma, but blank WSD to be explicit
                _blank_wsd_layers(token)
                continue
            if target_word[0].isdigit():
                # Skip numeric tokens, but blank WSD to be explicit
                _blank_wsd_layers(token)
                continue

            senses = get_token_senses(token, sentence, senses_df)
            senses_list = senses[S_ID].tolist()
            senses_candidates = ";".join(senses_list)
            valid_sense_ids = {_normalize_sense_id(sid) for sid in senses_list}
            senses = senses.to_dict(orient="records")
            if len(senses) == 0:
                token.add_layer(SENSE_ID_FIELD, "NEW_SENSE")
                token.add_layer(SENSE_COUNT_FIELD, "0")
                token.add_layer(SENSE_ORIGIN, "None")
                token.add_layer(SENSE_LIST_FIELD, "")
                token.add_layer(SENSE_AINOTES_FIELD, "")
                continue
            sense_id, notes, hallucinated = _invoke_chain_with_validation(
                chain,
                {
                    "sentence": marked_sentence,
                    "word": target_word,
                    "senses_block": build_senses_block(senses)
                },
                parse_json_response_clean,
                valid_sense_ids,
                time_delay=time_delay
            )
            origin = origin_model
            if sense_id == "NEW_SENSE":
                if not hallucinated:
                    sense_id = senses[0][S_ID]
                    origin = origin_first
                else:
                    origin = "None"
            token.add_layer(SENSE_ID_FIELD, sense_id)
            token.add_layer(SENSE_AINOTES_FIELD, notes)
            token.add_layer(SENSE_COUNT_FIELD, str(len(senses)))
            token.add_layer(SENSE_LIST_FIELD, senses_candidates)
            token.add_layer(SENSE_ORIGIN, origin)
        # Update progress
        current_sentence += 1
        print(f"\rProcessed {current_sentence}/{nuber_of_sentences} sentences.", end="")
    return sentences


def process_senses_with_chain_with_time_delay(
    sentences,
    senses_df,
    chain,
    origin_model,
    build_senses_block=default_build_senses_block,
    parse_json_response_clean=parse_model_output,
    n=2000,
    time_delay=4
):
    """
    Annotate sentences with sense information using a language model chain, with a time delay between requests.
    Handles both multiword expressions (MWEs) and single tokens, adding sense layers to each token.

    Args:
        sentences: List of sentence objects to annotate.
        senses_df: DataFrame with sense repository.
        chain: LLM chain for sense disambiguation.
        origin_model: String label for the model (e.g., 'ChatGPT', 'Gemini', etc.)
        build_senses_block: Function to format senses for the prompt (default: default_build_senses_block).
        parse_json_response_clean: Function to parse LLM output (default: parse_model_output).
        n: Starting index for multi-token entities (default 2000)
        time_delay: Time delay in seconds between requests (default 4)
    Returns:
        List of annotated sentence objects (with sense layers added).
    """
    import time
    processed_sentences = []
    # Initialize the index for multi-token entities
    j = n
    for sentence in sentences:
        # Process each sentence individually with a delay between requests
        processed = process_senses_with_chain(
            [sentence],
            senses_df,
            chain,
            origin_model,
            build_senses_block=build_senses_block,
            parse_json_response_clean=parse_json_response_clean,
            n=j
        )[0]
        processed_sentences.append(processed)
        # Update the index for multi-token entities
        # It very unlikely that thre more thne 5 mwe in a sentence
        j += 5
        time.sleep(time_delay)
    return processed_sentences
    