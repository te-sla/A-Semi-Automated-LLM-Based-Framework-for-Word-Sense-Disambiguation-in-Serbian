# data_loader.py

Utility module that centralises loading and discovery of LexiSense data
artifacts.

## Sense repository helpers

- `load_sense_repo(path=SENSE_REPO, sheet_name=0, keep_columns=..., deduplicate=False)` –
  reads the ELEXIS Excel file via `pandas`, keeps only the requested columns
  (defaulting to the schema in `config.py`), and optionally deduplicates on the
  non-ID columns.

## Chunked TSV helpers

- `list_group_tsvs(data_dir=DATA_DIR)` – scans the `Data/` directory for
  `sr-elexis-WSD_XXXX_YYYY.tsv` files and returns a sorted list of
  `(start, end, Path)` tuples.
- `get_group_tsv_path(start, end, data_dir=DATA_DIR)` – constructs the expected
  path for a given chunk without hitting the filesystem.
- `load_annotations_group(start, end, data_dir=DATA_DIR)` – parses a single
  chunk with `webanno_spacy_converter.parsers.tsv_parser_v3.WebAnnoLEXISParser`
  and returns the sentence objects. Raises informative errors when the optional
  dependency is missing or the chunk file is absent.
- `load_annotations_all_groups(data_dir=DATA_DIR)` – iterates through all
  discovered chunk files and returns a concatenated sentence list.
- `get_next_group_path(current_path, data_dir=DATA_DIR)` – given the current
  chunk path, finds the next chunk in sorted order.
- `iter_annotations_groups(data_dir=DATA_DIR)` – yields `(start, end, sentences)`
  lazily for each chunk, suitable for streaming or progress reporting.

## Notes

- The WebAnno parser import is wrapped in a try/except so callers that only need
  the DataFrame loader do not need the extra dependency.
- All path defaults and column identifiers are sourced from `config.py` to keep
  code and documentation consistent.
