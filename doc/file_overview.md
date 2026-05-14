# File Overview

> Companion repository for *A Semi-Automated LLM-Based Framework for Word Sense
> Disambiguation in Serbian* (submitted to SAGE Journal).

## Python Source Files

### `config.py`

Loads environment-backed secrets (`OPENAI_API_KEY`, `GOOGLE_GENAI_API_KEY`) and
collects shared constants. Defines canonical paths for `Data/`, `output/`, and
`stats/`, enumerates the annotation chunk TSVs, and centralises WebAnno layer
names for lemma, POS, MWE, and sense fields.

### `domain.py`

Provides the English-to-Serbian domain label map used for presenting sense
metadata. Exposes `translate_domain` to normalise raw domain strings and fall
back to `"nepoznato"` when a key is unknown.

### `preprocessing.py`

Utility helpers that operate on `webanno_spacy_converter` sentence objects:
highlighting MWEs/tokens, filtering tokens based on MWE/NER/UPOS layers, and
collecting candidate senses from the sense inventory DataFrame.

### `process_senses.py`

Implements the shared LLM-driven disambiguation loop. It builds sense candidate
blocks, calls a LangChain-style chain, validates returned sense IDs against the
allowed list, retries invalid model responses where configured, and writes the
selected sense layers back to tokens for export.

### `writers.py`

Defines WebAnno and INCEpTION TSV writers that emit the expected WSD layer
order and preserve token/MWE sense annotations.

### `data_loader.py`

Loads the sense inventory Excel files and chunked WebAnno TSV annotations.
Supports selecting the sense repository by annotation round.

### `simple_wsd.py`

Embedding-based WSD baseline that ranks candidate glosses with
sentence-transformer similarity and mirrors the WebAnno layer schema of the LLM
pipeline.

### `notebook_utils.py`

Shared notebook helpers imported from the working repository for targeted model
run support.

### `tools/run_simple_wsd_range.py`

Batch runner for configured SimpleWSD presets across one or both
sense-repository rounds. It writes standard and INCEpTION TSV files and round
comparison statistics.

## Notebooks

| Notebook | Purpose |
|---|---|
| `ChatGPT_sense.ipynb` | GPT 4.1 / GPT 5 WSD pipeline |
| `GEMINI_sense.ipynb` | Gemini 2.0 Flash Lite WSD pipeline |
| `GEMINI_pro_sense.ipynb` | Gemini Pro WSD pipeline |
| `Llama_sense.ipynb` | Llama4 WSD pipeline via local Ollama |
| `Mistral_sense.ipynb` | MistralSmall3.2 WSD pipeline via local Ollama |
| `Llama_sense_ablation_simplified_prompt.ipynb` | Llama4 simplified-prompt ablation |
| `Llama_sense_ablation_no_new_sense.ipynb` | Llama4 ablation that disallows `NEW_SENSE` |
| `Llama_sense_ablation_no_explanation.ipynb` | Llama4 ablation that returns only the sense ID |
| `SimpleWSD_sense.ipynb` | Sentence-transformer embedding baseline |
| `BaselineWSD_sense.ipynb` | Lesk-style baseline notebook |
| `post_anntotaion_stats.ipynb` | Agreement, disagreement, and NEW_SENSE statistics |

## Data and Output

### `Data/`

| File | Description |
|---|---|
| `Elexis-WSD-Repo-sr-v2.xlsx` | Current enhanced sense inventory |
| `Elexis-WSD-Repo-sr-v1.xlsx` | Original round 1 sense inventory |
| `sr-elexis-WSD_XXXX_YYYY.tsv` | Pre-chunked annotation files in 500-sentence groups |
| `gold_eval/` | Gold-standard development and held-out evaluation TSV files |

The targeted update does not replace the presentation repository workbooks
with the working-folder `Elexis-WSD-Repo*.xlsx` names.

### `Data/gold_eval/`

Gold-standard TSV files used for development and held-out evaluation:

| File | Use | Sentence range |
|---|---|---|
| `sr-elexis-WSD_0001_0120-gold.tsv` | Development set | 1-120 |
| `sr-elexis-WSD_0301-0400-gold.tsv` | Held-out test set | 301-400 |
| `sr-elexis-WSD_0401-0500-gold.tsv` | Held-out test set | 401-500 |
| `sr-elexis-WSD_0501-0600-gold.tsv` | Held-out test set | 501-600 |

The three held-out files came from `gold-files-20260511T150250Z-3-001.zip`
and provide 300 test sentences total. The 120-sentence file is kept as the
development gold set.

### `output/`

Model outputs are organised into two paper-aligned phases:

```text
output/
  Phase1/    # Round 1 exports and imported artifacts
  Phase2/    # Round 2 exports and imported artifacts
```

Imported first-600 local-model artifacts preserve their source filenames, for
example:

- `output/Phase1/LexiSense_0501_0600_Llama4_round1.tsv`
- `output/Phase2/LexiSense_Inception_0501_0600_Llama4_round2.tsv`

Every copied Llama4, MistralSmall3.2, and Llama4 ablation range has both a
standard `LexiSense_...tsv` file and an `LexiSense_Inception_...tsv` file.

The `0501-1000` ChatGPT/GPT standard TSV files were recovered from downloaded
output archives and renamed to match the phase naming convention:

- round 1 ChatGPT 3.5/4.1 files are under `output/Phase1/` with `Iround`
  suffixes.
- round 2 GPT 4.1/5 files are under `output/Phase2/` with `IIround` suffixes.

## Current Run Coverage

Copied outputs cover `0001-0500` and `0501-0600` for:

- `Llama4`
- `MistralSmall3.2`
- `Llama4_simple`
- `Llama4_nonew`
- `Llama4_noexp`

The full `0501-1000` output pairs are not present yet for those origins.
`GeminiPro_*` TSV output pairs are also not present yet. The accepted
`0501-0600` runs should not be rerun for this update.

## Other Files

| File | Purpose |
|---|---|
| `ablation_run_checklist.md` | First-600 Llama4 ablation completion checklist |
| `requirements.txt` | Runtime Python dependencies |
| `dev-requirements.txt` | Development/testing dependencies |
| `LICENSE` | Project licence |
| `.gitignore`, `.gitattributes` | Git configuration |
