import argparse
from pathlib import Path

import pandas as pd

from config import (
    OUTPUT_DIR,
    SENSE_REPO,
    SENSE_ID_FIELD,
    SENSE_LIST_FIELD,
    SENSE_AINOTES_FIELD,
    SENSE_COUNT_FIELD,
    SENSE_ORIGIN,
)
from data_loader import load_sense_repo
from preprocessing import (
    token_is_content_word,
    token_is_not_in_mwe,
    token_is_not_in_ne_not_in_filter,
)
from webanno_spacy_converter.parsers.tsv_parser_v3 import WebAnnoLEXISParser
from writers import IncetprionWebAnnoTSVWriter


ROUND_MARKER = "IIIround"


def _blank_wsd_layers(token) -> None:
    """Blank WSD-related fields on a token.

    This mirrors the behavior inside `process_senses_with_chain` for skipped tokens.
    """
    token.annotations[SENSE_ID_FIELD] = "_"
    token.annotations[SENSE_COUNT_FIELD] = "0"
    token.annotations[SENSE_LIST_FIELD] = "_"
    token.annotations[SENSE_AINOTES_FIELD] = "_"
    token.annotations[SENSE_ORIGIN] = "_"


def should_keep_wsd(token, senses_df: pd.DataFrame) -> bool:
    """Return True if this token is allowed to keep WSD annotations.

    Logic mirrors the positive path in process_senses_with_chain:
    - Tokens that are part of an MWE keep their WSD.
    - Tokens that are content words and pass NE/filter checks keep their WSD.
    Everything else should have WSD blanked.
    """
    # If token is part of an MWE, always keep whatever WSD is present
    if not token_is_not_in_mwe(token):
        return True

    # Non-MWE tokens must be content words and pass NE/filter checks
    if not token_is_content_word(token):
        return False

    if not token_is_not_in_ne_not_in_filter(token):
        return False

    return True


def fix_file(path: Path, senses_df: pd.DataFrame, dry_run: bool = False) -> None:
    """Fix a single Inception/WebAnno TSV output file in-place.

    - Loads sentences via WebAnnoLEXISParser.
    - For each token, decides whether to keep or blank WSD.
    - Writes back using IncetprionWebAnnoTSVWriter.
    - Creates a .bak backup once when not in dry_run mode.
    """
    print(f"Processing file: {path}")

    parser = WebAnnoLEXISParser(path)
    sentences = parser.parse()

    total_tokens = 0
    blanked_tokens = 0

    for sent in sentences:
        for token in sent.tokens:
            total_tokens += 1

            # Skip if token has no WSD annotation map (very defensive)
            if not hasattr(token, "annotations"):
                continue

            if should_keep_wsd(token, senses_df):
                continue

            # Token should not carry WSD -> blank it
            _blank_wsd_layers(token)
            blanked_tokens += 1

    print(f"  Tokens seen: {total_tokens}, WSD blanked on: {blanked_tokens}")

    if dry_run:
        print("  Dry run: not writing changes.")
        return

    # Backup once
    backup_path = path.with_suffix(path.suffix + ".bak")
    if not backup_path.exists():
        path.replace(backup_path)
        print(f"  Backup created: {backup_path.name}")
    else:
        print(f"  Backup already exists: {backup_path.name}")

    # Write updated sentences back to the original path
    writer = IncetprionWebAnnoTSVWriter(sentences)
    writer.save(path)
    print(f"  Fixed file written: {path.name}\n")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Fix existing WSD annotations in output TSVs by blanking WSD on "
            "tokens that should not carry senses (non-content, NE/filtered, etc.). "
            "Only files whose name contains the round marker are processed."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory with TSV outputs to fix (default: OUTPUT_DIR from config)",
    )
    parser.add_argument(
        "--round-marker",
        type=str,
        default=ROUND_MARKER,
        help="Substring that must appear in filename to be processed (default: IIIround)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only report what would be changed, do not rewrite files.",
    )

    args = parser.parse_args()

    output_dir: Path = args.output_dir
    round_marker: str = args.round_marker

    if not output_dir.exists():
        raise SystemExit(f"Output directory does not exist: {output_dir}")

    print(f"Loading sense repository from: {SENSE_REPO}")
    senses_df = load_sense_repo()

    # Collect candidate files
    candidates = sorted(
        p
        for p in output_dir.glob("*.tsv")
        if round_marker in p.name
    )

    if not candidates:
        print(f"No TSV files in {output_dir} matched round marker '{round_marker}'.")
        return

    print("Candidate files:")
    for p in candidates:
        print(f"  - {p.name}")
    print()

    for path in candidates:
        fix_file(path, senses_df, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
