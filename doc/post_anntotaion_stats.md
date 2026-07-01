# post_anntotaion_stats.ipynb

> Part of the companion repository for *A Semi-Automated LLM-Based Framework
> for Word Sense Disambiguation in Serbian* (accepted for publication; DOI and final citation pending).

This notebook performs post-hoc analysis and comparison of sense-annotated TSV
files produced by different LLM pipelines across the multi-round annotation
workflow. It is structured as follows:

1. **Introduction**: Explains the purpose and objectives of the analysis.
2. **Imports and Constants**: Loads required libraries and sets up constants for analysis (e.g., agreement columns, NEW_SENSE flags).
3. **Utility Functions**: Functions for cleaning data, comparing token senses, and flagging NEW_SENSE assignments.
4. **MWE Functions**: Functions for comparing MWEs by checking agreement of their first tokens.
5. **Sentence and TSV Analysis**: Functions for comparing sentences and entire TSV files, computing agreement statistics, and outputting results as CSV files.

**Usage:**
Use this notebook to:
- Compute statistics on sense assignments (e.g., how many tokens/MWEs were assigned NEW_SENSE)
- Compare outputs of different models (ChatGPT, Gemini, Llama)
- Measure agreement/disagreement between models
- Gain insights into the quality and consistency of sense annotation across models
