# GEMINI_sense.ipynb

> Part of the companion repository for *A Semi-Automated LLM-Based Framework
> for Word Sense Disambiguation in Serbian* (submitted to SAGE Journal).

WSD notebook using Gemini 2.0 Flash Lite via LangChain + Google GenAI. Uses the
same shared pipeline as the ChatGPT notebook but adds rate-limit throttling
(`RATE_LIMIT_DELAY`) between API calls.

1. Load annotation chunks and the sense inventory (`Elexis-WSD-Repo-sr-v2.xlsx`).
2. Disambiguate tokens/MWEs with zero-shot JSON-constrained prompts.
3. Export results to `output/`.

Outputs in this presentation repository are organised into `output/Phase1/` and
`output/Phase2/` (paper-aligned layout).

**Usage:**
Set `GOOGLE_GENAI_API_KEY` in a `.env` file and run the notebook cells sequentially.
