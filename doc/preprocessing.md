# preprocessing.py

> Part of the companion repository for *A Semi-Automated LLM-Based Framework
> for Word Sense Disambiguation in Serbian* (accepted for publication; DOI and final citation pending).

Helper routines that operate on `webanno_spacy_converter` sentence objects prior
to (or during) LLM-based disambiguation. Core capabilities:

- **Highlighting helpers** – `mark_token`, `mark_tokens`, and `mark_mwe`
	decorate text with Markdown markers, making prompts easier for models to
	parse.
- **MWE utilities** – `get_mwe_tokens` resolves the token span behind a
	`MultiWordExpression`, while `get_mwe_filtered_senses` fetches candidate
	senses from the repository using lemma-only matching.
- **Token filters** – `token_is_not_in_mwe`,
	`token_is_not_in_ne_not_in_filter`, and `token_is_content_word` encapsulate
	the heuristics for choosing which tokens to send to the model.
- **Sense collection** – `collect_mwe_senses` and
	`collect_simple_word_senses` gather candidate sense lists (with counts and
	highlighted sentences) for reporting or prompt construction. These functions
	expect a pandas DataFrame with the schema defined in `config.py`.

The module relies on constants from `config.py` and logs warnings for missing
annotation layers, helping spot data quality issues ahead of the LLM step.
