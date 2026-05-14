#!/usr/bin/env python
"""Clean WSD layer in all sr-elexis-WSD_*.tsv files.

- For each file in Data/sr-elexis-WSD_*.tsv:
  * Create a .bak backup next to it if it doesn't already exist
  * Blank the WSD columns (Comment, Explanation, KBid, NumberOfSenses, Origine, Possible)

This is the generalized version of clean_wsd_layer_test.py which you already
verified on sr-elexis-WSD_0001_0500.tsv.
"""

from pathlib import Path
import shutil
import sys

# Allow running as a standalone script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DATA_DIR


def clean_wsd_layer_in_file(path: Path) -> None:
    print(f"Cleaning WSD layer in: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()

    cleaned_lines = []
    for line in lines:
        # Keep comments, headers, empty lines as-is
        if not line or line.startswith("#"):
            cleaned_lines.append(line)
            continue
        if "\t" not in line:
            cleaned_lines.append(line)
            continue

        cols = line.split("\t")
        # Expect at least 17 columns based on your header:
        # ID, span, token, POS, UPOS, NE1, NE2, Lemma,
        # MWEid, MWElemma, MWEtype,
        # WSD_Comment, WSD_Explanation, WSD_KBid, WSD_NumberOfSenses,
        # WSD_Origine, WSD_Possible
        if len(cols) >= 17:
            cols[-6:] = ["_"] * 6
            line = "\t".join(cols)
        cleaned_lines.append(line)

    path.write_text("\n".join(cleaned_lines) + "\n", encoding="utf-8")
    print("  Done.")


def main() -> None:
    for path in DATA_DIR.glob("sr-elexis-WSD_*.tsv"):
        backup = path.with_suffix(path.suffix + ".bak")
        if not backup.exists():
            shutil.copy2(path, backup)
            print(f"Backup created: {backup}")
        else:
            print(f"Backup already exists: {backup}")
        clean_wsd_layer_in_file(path)


if __name__ == "__main__":
    main()
