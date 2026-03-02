# ChatGPT_sense.ipynb

> Part of the companion repository for *A Semi-Automated LLM-Based Framework
> for Word Sense Disambiguation in Serbian* (submitted to SAGE Journal).

Primary WSD notebook using OpenAI GPT 4.1 / GPT 5 via LangChain. Workflow:

1. Load annotation chunks (`sr-elexis-WSD_*.tsv`) and the sense inventory (`Elexis-WSD-Repo-sr-v2.xlsx`).
2. Build structured Serbian-language prompts with constrained JSON output.
3. Run zero-shot disambiguation via `process_senses.py`.
4. Export WebAnno / INCEpTION-compatible TSVs to `output/`.

Outputs in this presentation repository are organised into `output/Phase1/` and
`output/Phase2/` (paper-aligned layout).

**Usage:**
Set `OPENAI_API_KEY` in a `.env` file and run the notebook cells sequentially.
