import os
from pathlib import Path

import pandas as pd

from data_loader import (
    load_sense_repo,
    list_group_tsvs,
    get_group_tsv_path,
    get_next_group_path,
)
from config import DATA_DIR, SENSE_REPO, S_ID, S_DEFINITION, S_TYPE, S_POS, S_LEMMA, S_UPOS


def test_list_group_tsvs_discovers_chunks():
    groups = list_group_tsvs(DATA_DIR)
    # Should find at least the provided 0001_0500 file
    assert any(start == 1 and end == 500 for start, end, _ in groups), groups
    # Sorted ascending by start
    starts = [s for s, _, _ in groups]
    assert starts == sorted(starts)


def test_get_group_tsv_path_points_to_existing_first_chunk():
    p = get_group_tsv_path(1, 500, DATA_DIR)
    assert p.exists(), f"Missing chunk file: {p}"


def test_get_next_group_path_when_exists():
    groups = list_group_tsvs(DATA_DIR)
    # If more than one group exists, next should resolve
    if len(groups) > 1:
        _, __, cur = groups[0]
        nxt = get_next_group_path(cur, DATA_DIR)
        assert nxt is not None and nxt.exists()
    else:
        # Only one group present; next should be None
        _, __, cur = groups[0]
        nxt = get_next_group_path(cur, DATA_DIR)
        assert nxt is None


def test_load_sense_repo_first_sheet_and_columns():
    df = load_sense_repo(SENSE_REPO)
    assert isinstance(df, pd.DataFrame)
    for col in (S_ID, S_DEFINITION, S_TYPE, S_POS, S_LEMMA, S_UPOS):
        assert col in df.columns


def test_load_sense_repo_deduplicate_true_matches_manual():
    manual = pd.read_excel(SENSE_REPO, sheet_name=0, engine="openpyxl")
    cols = [c for c in (S_ID, S_DEFINITION, S_TYPE, S_POS, S_LEMMA, S_UPOS) if c in manual.columns]
    manual = manual[cols].copy()
    # Deduplicate manually excluding S_ID
    manual_dedup = manual.drop_duplicates(subset=[c for c in cols if c != S_ID]).reset_index(drop=True)

    loaded_dedup = load_sense_repo(SENSE_REPO, deduplicate=True)
    assert list(loaded_dedup.columns) == cols
    assert len(loaded_dedup) == len(manual_dedup)
    pd.testing.assert_frame_equal(loaded_dedup.reset_index(drop=True), manual_dedup.reset_index(drop=True))
