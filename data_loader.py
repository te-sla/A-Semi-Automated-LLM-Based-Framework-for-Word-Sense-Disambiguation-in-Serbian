"""
data_loader.py

Centralized utilities for loading the Sense Repository (Excel) and
annotation TSV files (WebAnno LEXIS), including second-round chunked inputs.

Usage examples:
    from data_loader import load_sense_repo, load_annotations_group, list_group_tsvs
    senses_df = load_sense_repo()
    sentences = load_annotations_group(1, 500)
"""
from __future__ import annotations

from pathlib import Path
import re
from typing import Iterable, List, Tuple

import pandas as pd

from config import (
    DATA_DIR,
    SENSE_REPO,
    SENSE_REPO_OLD,
    S_ID,
    S_DEFINITION,
    S_TYPE,
    S_POS,
    S_LEMMA,
    S_UPOS,
    S_LITERALS,
)

# Lazy import to avoid unnecessary dependency cost when only DataFrame loading is needed
try:
    from webanno_spacy_converter.parsers.tsv_parser_v3 import WebAnnoLEXISParser
except Exception:  # pragma: no cover - optional at import time
    WebAnnoLEXISParser = None  # type: ignore


GROUP_FILE_REGEX = re.compile(r"sr-elexis-WSD_(\d{4})_(\d{4})\.tsv$")


def load_sense_repo(
        path: Path | str = SENSE_REPO,
        sheet_name: int | str = 0,
    # Added S_LITERALS so downstream code (e.g. exporting senses with literals) has access by default
    keep_columns: Iterable[str] = (S_ID, S_DEFINITION, S_TYPE, S_POS, S_LEMMA, S_UPOS, S_LITERALS),
        deduplicate: bool = False,
) -> pd.DataFrame:
        """Load the Sense Repository Excel (first sheet by default).

        Notes:
                - Include lemma & upos columns by default because filtering functions
                    (e.g., get_mwe_filtered_senses, get_token_senses) require them.
        - Added literals column (S_LITERALS) to default selection so that sense
          exports including literals no longer raise KeyError when the source
          Excel provides it.
                - Deduplication is disabled by default to preserve multiple lemma
                    mappings for the same definition. If enabled, duplicates are removed
                    across all non-ID columns provided.
        """
        path = Path(path)
        df = pd.read_excel(path, sheet_name=sheet_name, engine="openpyxl")
        # Keep requested columns that actually exist
        cols = [c for c in keep_columns if c in df.columns]
        df = df[cols].copy()
        if deduplicate and len(cols) > 1:
                # Exclude the sense ID from dedup criteria if present
                dedup_keys = [c for c in cols if c != S_ID]
                df = df.drop_duplicates(subset=dedup_keys).reset_index(drop=True)
        return df


def load_sense_repo_by_round(
    round: int = 2,
    sheet_name: int | str = 0,
    keep_columns: Iterable[str] = (S_ID, S_DEFINITION, S_TYPE, S_POS, S_LEMMA, S_UPOS, S_LITERALS),
    deduplicate: bool = False,
    **kwargs,
) -> pd.DataFrame:
    """Load the Sense Repository for a specific annotation round.

    Args:
        round: The annotation round (1 for old/first round, 2 for current/second round).
        round_number: Backward-compatible keyword alias accepted via kwargs.
        sheet_name: Sheet name or index to load from the Excel file.
        keep_columns: Columns to keep in the resulting DataFrame.
        deduplicate: Whether to remove duplicate rows.

    Returns:
        DataFrame containing the sense repository for the specified round.

    Raises:
        ValueError: If an invalid round number is provided.
    """
    if "round_number" in kwargs:
        round = kwargs.pop("round_number")
    if kwargs:
        unexpected = ", ".join(sorted(kwargs))
        raise TypeError(f"Unexpected keyword argument(s): {unexpected}")

    if round == 1:
        path = SENSE_REPO_OLD
    elif round == 2:
        path = SENSE_REPO
    else:
        raise ValueError(f"Invalid round: {round}. Must be 1 or 2.")
    
    return load_sense_repo(
        path=path,
        sheet_name=sheet_name,
        keep_columns=keep_columns,
        deduplicate=deduplicate,
    )


def list_group_tsvs(data_dir: Path | str = DATA_DIR) -> List[Tuple[int, int, Path]]:
    """Return a sorted list of available chunked TSVs as (start, end, path)."""
    data_dir = Path(data_dir)
    results: List[Tuple[int, int, Path]] = []
    for p in data_dir.glob("sr-elexis-WSD_*.tsv"):
        m = GROUP_FILE_REGEX.search(p.name)
        if not m:
            continue
        start, end = int(m.group(1)), int(m.group(2))
        results.append((start, end, p))
    # Sort by start, then end
    results.sort(key=lambda t: (t[0], t[1]))
    return results


def get_group_tsv_path(start: int, end: int, data_dir: Path | str = DATA_DIR) -> Path:
    """Build the expected path for a given chunk (start,end)."""
    data_dir = Path(data_dir)
    fname = f"sr-elexis-WSD_{start:04d}_{end:04d}.tsv"
    return data_dir / fname


def load_annotations_group(start: int, end: int, data_dir: Path | str = DATA_DIR):
    """Load a specific chunked TSV using WebAnnoLEXISParser and return sentences list."""
    if WebAnnoLEXISParser is None:
        raise ImportError("webanno_spacy_converter is required to parse TSVs. Ensure it's installed.")
    path = get_group_tsv_path(start, end, data_dir=data_dir)
    if not path.exists():
        raise FileNotFoundError(f"Chunk file not found: {path}")
    parser = WebAnnoLEXISParser(path)
    return parser.parse()


def load_annotations_all_groups(data_dir: Path | str = DATA_DIR):
    """Load and concatenate sentences from all available chunked TSVs in order."""
    if WebAnnoLEXISParser is None:
        raise ImportError("webanno_spacy_converter is required to parse TSVs. Ensure it's installed.")
    sentences_all = []
    for start, end, p in list_group_tsvs(data_dir=data_dir):
        parser = WebAnnoLEXISParser(p)
        sentences_all.extend(parser.parse())
    return sentences_all


def get_next_group_path(current_path: Path | str, data_dir: Path | str = DATA_DIR) -> Path | None:
    """Given a current chunk path, return the next chunk path in sorted order (or None)."""
    current_path = Path(current_path)
    groups = list_group_tsvs(data_dir=data_dir)
    for idx, (_, __, p) in enumerate(groups):
        if p.resolve() == current_path.resolve():
            if idx + 1 < len(groups):
                return groups[idx + 1][2]
            return None
    return None


def iter_annotations_groups(data_dir: Path | str = DATA_DIR):
    """Yield (start, end, sentences) for each chunk in sorted order."""
    if WebAnnoLEXISParser is None:
        raise ImportError("webanno_spacy_converter is required to parse TSVs. Ensure it's installed.")
    for start, end, p in list_group_tsvs(data_dir=data_dir):
        parser = WebAnnoLEXISParser(p)
        yield start, end, parser.parse()
