# Llama_sense.ipynb

> Part of the companion repository for *A Semi-Automated LLM-Based Framework
> for Word Sense Disambiguation in Serbian* (accepted for publication; DOI and final citation pending).

WSD notebook using Llama 3.3 locally via Ollama. Uses Markdown-bold target-word
highlighting (`**word**`) and Llama-specific prompt tokens.

> **Note:** Llama 3.3 was not used in the paper's evaluation because local
> inference was too slow on the available hardware for full-scale annotation.
> A 10-sample test confirmed the pipeline works correctly. The notebook is
> included for completeness and reproducibility.

1. Load annotation chunks and the sense inventory (`Elexis-WSD-Repo-sr-v2.xlsx`).
2. Disambiguate tokens/MWEs with zero-shot JSON-constrained prompts.
3. Export results to `output/`.

Outputs in this presentation repository are organised into `output/Phase1/` and
`output/Phase2/` (paper-aligned layout).

**Prerequisites:** Install [Ollama](https://ollama.com/) and run `ollama pull llama3.3`.

**Usage:**
Start Ollama, then run the notebook cells sequentially.
