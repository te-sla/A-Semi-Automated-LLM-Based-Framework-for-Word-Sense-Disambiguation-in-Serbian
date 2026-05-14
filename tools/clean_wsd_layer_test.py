#!/usr/bin/env python
"""Small test script to clean WSD layer for a single TSV copy.

- Copies Data/sr-elexis-WSD_0001_0500.tsv to Data/sr-elexis-WSD_0001_0500_clean_test.tsv
- Blanks WSD columns (Comment, Explanation, KBid, NumberOfSenses, Origine, Possible)
- Prints a few before/after lines so you can manually inspect.
"""

from pathlib import Path
import shutil
import sys

# Allow running as a standalone script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DATA_DIR
SRC_NAME = "sr-elexis-WSD_0001_0500.tsv"
DST_NAME = "sr-elexis-WSD_0001_0500_clean_test.tsv"


def clean_wsd_layer_in_file(path: Path) -> None:
    print(f"Cleaning WSD layer in: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()

    cleaned_lines = []
    for line in lines:
        if not line or line.startswith("#"):
            cleaned_lines.append(line)
            continue
        if "\t" not in line:
            cleaned_lines.append(line)
            continue

        cols = line.split("\t")
        # Expect at least 17 columns based on your header
        # ID, span, token, POS, UPOS, NE1, NE2, Lemma,
        # MWEid, MWElemma, MWEtype,
        # WSD_Comment, WSD_Explanation, WSD_KBid, WSD_NumberOfSenses, WSD_Origine, WSD_Possible
        if len(cols) >= 17:
            # Blank last 6 (WSD) columns
            cols[-6:] = ["_"] * 6
            line = "\t".join(cols)
        cleaned_lines.append(line)

    path.write_text("\n".join(cleaned_lines) + "\n", encoding="utf-8")
    print("Done.")


def main() -> None:
    src = DATA_DIR / SRC_NAME
    dst = DATA_DIR / DST_NAME

    if not src.exists():
        raise SystemExit(f"Source file not found: {src}")

    # Create a fresh copy for testing
    shutil.copy2(src, dst)
    print(f"Test copy created: {dst}")

    # Show a few original lines for comparison
    print("\n--- ORIGINAL (from src) first 10 token lines ---")
    src_lines = src.read_text(encoding="utf-8").splitlines()
    shown = 0
    for line in src_lines:
        if line.startswith("#") or not line.strip():
            continue
        print(line)
        shown += 1
        if shown >= 10:
            break

    # Clean the test copy
    clean_wsd_layer_in_file(dst)

    # Show a few cleaned lines for comparison
    print("\n--- CLEANED (from dst) first 10 token lines ---")
    dst_lines = dst.read_text(encoding="utf-8").splitlines()
    shown = 0
    for line in dst_lines:
        if line.startswith("#") or not line.strip():
            continue
        print(line)
        shown += 1
        if shown >= 10:
            break


if __name__ == "__main__":
    main()
