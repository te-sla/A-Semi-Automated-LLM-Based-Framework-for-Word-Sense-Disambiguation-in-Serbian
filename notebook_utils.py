"""
notebook_utils.py

Shared helper utilities for interactive Jupyter notebooks in the LexiSense-SR pipeline.
Keeps common notebook-only logic (e.g. debug previews) in one place so that changes
propagate to all notebooks without duplication.
"""

from preprocessing import (
    get_token_senses, mark_token, token_is_content_word,
    token_is_not_in_ne_not_in_filter, token_is_not_in_mwe,
)
from config import L_LEMMA


def debug_preview_chain(sentences, senses_df, chain, build_senses_block, n_items=3, sentence_lookback=10):
    """
    Invoke *chain* on the first ``n_items`` eligible candidate tokens found in
    ``sentences[:sentence_lookback]`` and print the raw model output.

    Intended to be called from ablation notebooks before the full processing run
    so the user can quickly verify that the model is responding in the expected
    format.

    Args:
        sentences:          List of sentence objects (from WebAnnoLEXISParser).
        senses_df:          DataFrame with sense repository.
        chain:              LangChain chain (prompt | llm | parser) to invoke.
        build_senses_block: Callable that formats a list of sense dicts into a
                            string for the prompt (e.g. default_build_senses_block).
        n_items:            Number of preview items to collect (default 3).
        sentence_lookback:  How many sentences to search through when collecting
                            preview items (default 10).
    """
    preview_items = []
    for _sent in sentences[:sentence_lookback]:
        for _tok in _sent.tokens:
            if not token_is_not_in_mwe(_tok):
                continue
            if not token_is_content_word(_tok) or not token_is_not_in_ne_not_in_filter(_tok):
                continue
            _lemma = _tok.layers.get(L_LEMMA, "_")
            if _lemma == "_" or _lemma[0].isdigit():
                continue
            _senses = get_token_senses(_tok, _sent, senses_df)
            _senses_dict = _senses.to_dict(orient="records")
            if not _senses_dict:
                continue
            _marked = mark_token(_tok, _sent)
            preview_items.append({
                "sentence": _marked,
                "word": _lemma,
                "senses_block": build_senses_block(_senses_dict),
            })
            if len(preview_items) >= n_items:
                break
        if len(preview_items) >= n_items:
            break

    print(f"=== DEBUG PREVIEW: {len(preview_items)} raw model output(s) ===")
    for _i, _payload in enumerate(preview_items, 1):
        print(f"\n--- Item {_i} ---")
        print(f"Word: {_payload['word']}")
        print(f"Sentence snippet: {_payload['sentence'][:120]}")
        _raw = chain.invoke(_payload)
        print(f"Raw model output:\n{_raw}")
