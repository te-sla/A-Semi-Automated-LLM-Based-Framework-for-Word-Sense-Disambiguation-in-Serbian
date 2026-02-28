# preprocessing_refactored.py
# -*- coding: utf-8 -*-

from typing import List, Dict, Any, Optional
import logging

import pandas as pd

from webanno_spacy_converter.models.annotation_token import AnnotationToken
from webanno_spacy_converter.models.sentence_with_mwes import (
    AnnotatedSentenceWithMWEs,
    MultiWordExpression,
)
from config import (
    CONTENT_WORDS,
    EVENT_FILTER,
    L_LEMMA,
    L_MWE_ID,
    L_NAMED_ENT,
    L_UPOS,
    S_LEMMA,
    S_UPOS,
    S_TYPE,
)

# Configure module-level logger
logger = logging.getLogger(__name__)

# Default markers for highlighting
START_MARK: str = "**"
END_MARK: str = "**"


def get_mwe_tokens(
    sentence: AnnotatedSentenceWithMWEs,
    mwe: MultiWordExpression,
) -> List[AnnotationToken]:
    """
    Retrieve the tokens that compose a multi-word expression (MWE).

    Args:
        sentence: The annotated sentence containing tokens.
        mwe: The multi-word expression annotation.

    Returns:
        List of AnnotationToken objects for the MWE.
    """
    return [sentence.tokens[i] for i in mwe.token_indices]


def mark_tokens(
    tokens: List[AnnotationToken],
    sentence: AnnotatedSentenceWithMWEs,
    start_mark: str = START_MARK,
    end_mark: str = END_MARK,
) -> str:
    """
    Wrap multiple token spans in a sentence with start/end markers.

    Args:
        tokens: Tokens to mark.
        sentence: The annotated sentence.
        start_mark: Marker to insert before each token span.
        end_mark: Marker to insert after each token span.

    Returns:
        The sentence text with specified tokens highlighted.
    """
    text = sentence.text
    # Build pieces to avoid O(n^2) slicing
    sorted_tokens = sorted(tokens, key=lambda t: t.start)
    pieces: List[str] = []
    last_idx = 0

    for token in sorted_tokens:
        # Append text before token
        pieces.append(text[last_idx:token.start])
        # Append marked token text
        pieces.append(f"{start_mark}{text[token.start:token.end]}{end_mark}")
        last_idx = token.end

    # Append remaining text
    pieces.append(text[last_idx:])
    return "".join(pieces)


def mark_token(
    token: AnnotationToken,
    sentence: AnnotatedSentenceWithMWEs,
    start_mark: str = START_MARK,
    end_mark: str = END_MARK,
) -> str:
    """
    Mark a single token in a sentence with start/end markers.

    Args:
        token: The token to highlight.
        sentence: The annotated sentence.
        start_mark: Marker to insert before the token.
        end_mark: Marker to insert after the token.

    Returns:
        The sentence text with the specified token highlighted.
    """
    text = sentence.text
    return (
        text[: token.start]
        + start_mark
        + text[token.start : token.end]
        + end_mark
        + text[token.end :]
    )


def mark_mwe(
    mwe: MultiWordExpression,
    sentence: AnnotatedSentenceWithMWEs,
    start_mark: str = START_MARK,
    end_mark: str = END_MARK,
) -> str:
    """
    Highlight an entire multi-word expression (MWE) in the sentence.

    Args:
        mwe: The multi-word expression annotation.
        sentence: The annotated sentence.
        start_mark: Marker to insert at the beginning of the MWE.
        end_mark: Marker to insert at the end of the MWE.

    Returns:
        The sentence text with the MWE highlighted.
    """
    tokens = get_mwe_tokens(sentence, mwe)
    return mark_tokens(tokens, sentence, start_mark, end_mark)

def get_mwe_filtered_senses(
    mwe: MultiWordExpression,
    sense_repo_df: pd.DataFrame,
) -> Optional[pd.DataFrame]:
    """
    Filters the sense repository DataFrame based ONLY on the lemma of a
    MultiWordExpression (MWE). Type-based filtering was removed because it
    proved too restrictive for many MWEs.

    Args:
        mwe: The MultiWordExpression object.
        sentence: The AnnotatedSentenceWithMWEs object containing the MWE.
                  (Not directly used in the filtering but might be needed for context).
        sense_repo_df: The pandas DataFrame representing the sense repository.

    Returns:
        A pandas DataFrame containing the filtered rows from the sense repository
        that match the MWE's lemma and type.
        Returns None if the MWE is a placeholder (lemma is "*").
        Returns an empty DataFrame if no matching senses are found.
    """
    lemma = mwe.lemma
    # Keep original type for potential downstream metadata (not used in filtering)
    if lemma == "*":
        return None  # Return None for placeholder MWEs

    # Lemma-only filtering (type removed)
    filtered_df = sense_repo_df[(sense_repo_df[S_LEMMA] == lemma)]
    return filtered_df


def collect_mwe_senses(
    sentences: List[AnnotatedSentenceWithMWEs],
    sense_repo_df: pd.DataFrame,
) -> List[Dict[str, Any]]:
    """
    For each MWE in the given sentences, look up exact lemma matches in the sense repository.

    Args:
        sentences: List of annotated sentences containing MWEs.
        sense_repo_df: DataFrame with a column named by S_LEMMA as lemma.

    Returns:
        A list of dicts, each containing lemma, senses DataFrame, count, and highlighted sentence.
    """

    results: List[Dict[str, Any]] = []
    for sentence in sentences:
        for mwe in sentence.mwes:
            lemma = mwe.lemma
            if lemma == "*":  # skip placeholders
                continue
            type = mwe.type.split("[")[0].strip()
            # Lemma-only filtering (type constraint removed)
            filtered = sense_repo_df[(sense_repo_df[S_LEMMA] == lemma)]
            results.append({
                "lemma": lemma,
                "type": mwe.type,
                "senses": filtered,
                "num_senses": len(filtered),
                "marked_sentence": mark_mwe(mwe, sentence),
                "sentence": sentence.text,
            })
    return results


def token_is_not_in_mwe(token: AnnotationToken) -> bool:
    """
    Check whether a token is NOT part of a multi-word expression (MWE).

    Args:
        token: The token to check.

    Returns:
        True if token is not in an MWE, False otherwise.
    """
    mwe_id = token.layers.get(L_MWE_ID, "")
    return mwe_id in {"*", "", "_", "0"}

def token_is_not_in_ne_not_in_filter(token: AnnotationToken) -> bool:
    """
    Check whether a token is NOT part of a named entity and not in the event filter.

    Args:
        token: The token to check.

    Returns:
        True if token is not in a named entity and not in the event filter, False otherwise.
    """
    label = token.layers.get(L_NAMED_ENT, "*").split("[")[0].strip()
    return label == "*" or label in EVENT_FILTER

def token_is_content_word(token: AnnotationToken) -> bool:
    """
    Check whether a token is a content word based on its UPOS tag.

    Args:
        token: The token to check.

    Returns:
        True if the token is a content word, False otherwise.
    """
    upos = token.layers.get(L_UPOS, "")
    return upos in CONTENT_WORDS

def get_token_senses(
    token: AnnotationToken, sentence: AnnotatedSentenceWithMWEs, sense_repo_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Retrieve senses for a token based on its lemma and UPOS tag.

    Args:
        token: The token to check.
        sentence: The annotated sentence containing the token.
        sense_repo_df: DataFrame with a column named by S_LEMMA as lemma.

    Returns:
        A DataFrame of senses for the token.
    """
    lemma = token.layers.get(L_LEMMA, "")
    upos = token.layers.get(L_UPOS, "")
    filtered = sense_repo_df[(sense_repo_df[S_LEMMA] == lemma) & (sense_repo_df[S_UPOS] == upos)]
    return filtered


def collect_simple_word_senses(
    sentences: List[AnnotatedSentenceWithMWEs],
    sense_repo_df: pd.DataFrame,
) -> List[Dict[str, Any]]:
    """
    For each simple word (not part of an MWE) in sentences, look up senses and record count.

    A token qualifies if:
      - Not in an MWE
      - Has lemma layer L_LEMMA
      - UPOS tag L_UPOS in CONTENT_WORDS
      - Named-entity label L_NAMED_ENT in EVENT_FILTER

    Args:
        sentences: List of annotated sentences.
        sense_repo_df: DataFrame with a column named by S_LEMMA.

    Returns:
        A list of dicts for each qualifying token with lemma, senses, origin sentence, and marked sentence.
    """
    results: List[Dict[str, Any]] = []
    for sentence in sentences:
        for token in sentence.tokens:
            if not token_is_not_in_mwe(token):
                continue

            label = token.layers.get(L_NAMED_ENT, "ROLE").split("[")[0].strip()
            if label not in EVENT_FILTER:
                continue

            if L_LEMMA not in token.layers:
                logger.warning("Token %r missing layer %s", token.text, L_LEMMA)
                continue

            lemma = token.layers[L_LEMMA]
            # Skip tokens with lema that start with a number (e.g., "1945.")
            if lemma[0].isnumeric():
                continue
            #skip lemma that start with uppercase (aka those possessive form of presonal name aka Anderson's)
            if lemma[0].isupper():
                continue
            upos = token.layers.get(L_UPOS, "")
            if upos not in CONTENT_WORDS:
                continue

            filtered = sense_repo_df[(sense_repo_df[S_LEMMA] == lemma) & (sense_repo_df[S_UPOS] == upos)]
            results.append({
                "lemma": lemma,
                "upos": upos,
                "senses": filtered,
                "num_senses": len(filtered),
                "originating_sentence": sentence.text,
                "marked_sentence": mark_token(token, sentence),
            })
    return results
