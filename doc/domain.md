# domain.py

> Part of the companion repository for *A Semi-Automated LLM-Based Framework
> for Word Sense Disambiguation in Serbian* (submitted to SAGE Journal).

Provides a lightweight mapping between the English domain labels present in the
sense inventory and their Serbian equivalents. The module exposes:

- `DOMAIN_MAP`: dictionary keyed by the English domain slug (e.g.,
	`"chemistry"`, `"computer_science"`) with translated Serbian strings.
- `UNKNOWN_DOMAIN`: fallback string (`"nepoznato"`) used when no mapping is
	available or the source value is missing/`NaN`.
- `translate_domain(domain)`: helper that normalises the input and returns the
	Serbian translation, defaulting to `UNKNOWN_DOMAIN` when the key is absent.

This file does **not** define broader data models; instead, it keeps
presentation-ready domain labels centralised for reuse in reporting notebooks
and export scripts.
