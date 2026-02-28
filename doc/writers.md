# writers.py

Extends `webanno_spacy_converter`'s `BaseWebAnnoTSVWriter` to emit TSV exports
with the exact layer structure required by LexiSense.

- `CustomWebAnnoTSVWriter` – generic export matching the project’s custom
	sense layer (`SenseID`, `Number_of_candidate_senses`, etc.). It rewrites plain
	Wikidata IDs as full IRIs and preserves the original sense strings.
- `IncetprionWebAnnoTSVWriter` – adapts the header and layer order to
	Inception-compatible naming (`webanno.custom.WSD`). Also rewrites sense IDs to
	the `http://llod.jerteh.rs/WSD/` namespace expected by that platform.

Both writers retrieve layer keys from `config.py`, ensuring the exported TSVs
stay aligned with annotation constants and the structure populated by
`process_senses.py`.
