# File Overview

> Companion repository for *A Semi-Automated LLM-Based Framework for Word Sense
> Disambiguation in Serbian* (submitted to SAGE Journal).

## Python Source Files

### config.py
Loads environment-backed secrets (`OPENAI_API_KEY`, `GOOGLE_GENAI_API_KEY`) and
collects shared constants. Defines canonical paths for `Data/`, `output/`, and
`stats/`, enumerates the annotation chunk TSVs, and centralises WebAnno layer
names (lemma, POS, MWE, and sense fields) together with filtering helpers
(`CONTENT_WORDS`, `EVENT_FILTER`).

### domain.py
Provides the English → Serbian domain label map used for presenting sense
metadata. Exposes `translate_domain` to normalise raw domain strings and fall
back to `"nepoznato"` when a key is unknown.

### preprocessing.py
Utility helpers that operate on `webanno_spacy_converter` sentence objects:
highlighting MWEs/tokens, filtering tokens based on MWE/NER/UPOS layers, and
collecting candidate senses for MWEs and single tokens from the sense
inventory DataFrame.

### process_senses.py
Implements the LLM-driven disambiguation loop. Orchestrates sense candidate
generation (via `preprocessing`), calls a LangChain-style `chain`, validates the
returned sense IDs against the allowed list, and writes the results onto token
layers so they can be exported. Includes retry logic for hallucinated sense IDs
and a time-delayed variant for rate-limited APIs (e.g. Gemini).

### writers.py
Defines two WebAnno TSV writers:
`CustomWebAnnoTSVWriter` (generic export) and
`IncetprionWebAnnoTSVWriter` (INCEpTION schema). Both extend the base writer to
emit the exact layer order and decorate identifiers/URIs.

### data_loader.py
Loads the sense inventory Excel file (`Elexis-WSD-Repo-sr-v2.xlsx`) and chunked
WebAnno TSV annotations. Enumerates available TSV groups, provides path
builders, and offers iterators for streaming sentence batches.

### simple_wsd.py
Embedding-based baseline that ranks candidate glosses with the
`all-MiniLM-L6-v2` sentence transformer and annotates tokens/MWEs accordingly,
mirroring the WebAnno layer schema of the LLM pipeline.

## Notebooks

### ChatGPT_sense.ipynb
Primary WSD pipeline using GPT 4.1 / GPT 5 via LangChain + OpenAI.

### GEMINI_sense.ipynb
WSD pipeline using Gemini 2.0 Flash Lite via LangChain + Google GenAI.

### Llama_sense.ipynb
WSD pipeline using Llama 3.3 locally via Ollama. Not used in the paper due to
computational constraints; validated on a 10-sample test.

### SimpleWSD_sense.ipynb
Notebook interface for the `all-MiniLM-L6-v2` embedding baseline.

### post_anntotaion_stats.ipynb
Post-hoc analysis: computes inter-model agreement/disagreement, NEW_SENSE
counts, and exports statistics to `stats/`.

## Data and Output

### Data/
| File | Description |
|------|-------------|
| `Elexis-WSD-Repo-sr-v2.xlsx` | Enhanced sense inventory (Serbian WordNet + additional senses) |
| `Elexis-WSD-Repo-sr-v1.xlsx` | Original sense inventory (Round I) |
| `sr-elexis-WSD_XXXX_YYYY.tsv` | Pre-chunked annotation files (500 sentences each) |

### output/
Model outputs organised into two paper-aligned phases:

```
output/
├── Phase1/           # Phase 1 exports (inputs + intermediate/test TSVs)
│   ├── LexiSense_Inception_*_gemini_Iround.tsv
│   ├── LexiSense_Inception_*_gpt-3.5_Iround_test.tsv
│   ├── LexiSense_Inception_*_gpt-4.1_Iround.tsv
│   ├── LexiSense_Inception_*_simple_wsd_Iround.tsv
│   └── LexiSense_Inception_*_simple_wsd_tesla_Iround.tsv
└── Phase2/           # Phase 2 model outputs (paper results)
    └── LexiSense_Inception_*_*.tsv
```

### stats/
Derived CSV statistics (agreement scores, disagreement details) produced by
`post_anntotaion_stats.ipynb`.

## Other Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Runtime Python dependencies |
| `dev-requirements.txt` | Development/testing dependencies |
| `LICENSE` | Project licence |
| `.gitignore`, `.gitattributes` | Git configuration |

---
For detailed documentation on each module, see the corresponding `.md` files in
this folder.
