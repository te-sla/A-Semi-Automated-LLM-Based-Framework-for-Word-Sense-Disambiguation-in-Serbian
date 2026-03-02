# A Semi-Automated LLM-Based Framework for Word Sense Disambiguation in Serbian

Companion code and data for the paper:

> **A Semi-Automated LLM-Based Framework for Word Sense Disambiguation in Serbian**
> *Submitted to SAGE Journal*

This repository implements a semi-automated annotation workflow for Word Sense
Disambiguation (WSD) in Serbian, leveraging Large Language Models (LLMs) through
specialised prompt engineering with zero-shot inference and constrained
JSON-formatted output. The framework guides LLMs in selecting the appropriate
sense from a custom inventory built on the Serbian WordNet and enhanced with
additional senses.

## Key Results

| Model | Single-word accuracy | Multi-word accuracy |
|-------|---------------------|---------------------|
| GPT 4.1 | 83.1 % | 100 % |
| GPT 5 | adaptive reasoning, excels on extreme polysemy & verbs | — |
| Baselines (XLM-RoBERTa, all-MiniLM-L6-v2) | significantly lower | — |

## Features

- **LLM-based WSD** – zero-shot sense disambiguation via GPT 4.1 / GPT 5, Gemini 2.0 Flash Lite, and Llama 3.3
  > *Note:* Llama 3.3 was not included in the paper's evaluation — local inference was too slow on the available hardware for full-scale annotation, though it produced correct results on a 10-sample test run. The pipeline is fully functional and included here for reproducibility.
- **Embedding baseline** – cosine-similarity WSD with `all-MiniLM-L6-v2` sentence transformer
- **Custom sense inventory** – Serbian WordNet senses enriched with additional entries (`Elexis-WSD-Repo-sr-v2.xlsx`)
- **Semi-automated annotation** – structured prompts produce constrained JSON; multi-round workflow with validation and retry logic
- **Multi-word expression handling** – automatic MWE extraction and disambiguation
- **WebAnno / INCEpTION export** – TSV writers compatible with both annotation platforms

## Repository Structure

```
├── ChatGPT_sense.ipynb          # GPT 4.1 / GPT 5 WSD pipeline
├── GEMINI_sense.ipynb           # Gemini 2.0 Flash Lite WSD pipeline
├── Llama_sense.ipynb            # Llama 3.3 (local, via Ollama) WSD pipeline
├── SimpleWSD_sense.ipynb        # Embedding-baseline WSD notebook
├── post_anntotaion_stats.ipynb  # Inter-model agreement & statistics
├── config.py                    # Paths, constants, field names
├── preprocessing.py             # Token/MWE filtering, sense collection
├── process_senses.py            # LLM disambiguation loop (shared)
├── data_loader.py               # Sense-repo & chunked-TSV loaders
├── domain.py                    # EN→SR domain-label translation
├── writers.py                   # WebAnno / INCEpTION TSV export
├── simple_wsd.py                # Sentence-transformer baseline
├── Data/
│   ├── Elexis-WSD-Repo-sr-v2.xlsx   # Sense inventory (current)
│   ├── Elexis-WSD-Repo-sr-v1.xlsx   # Sense inventory (v1)
│   └── sr-elexis-WSD_*.tsv          # Annotation chunks (500-sentence groups)
├── output/                      # Paper-aligned outputs (Phase 1 / Phase 2)
│   ├── Phase1/                  # Phase 1 exports (inputs + intermediate/test TSVs)
│   └── Phase2/                  # Phase 2 model outputs used for reporting
├── stats/                       # Agreement CSVs produced by the notebooks
└── doc/                         # Per-file documentation
```

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/te-sla/A-Semi-Automated-LLM-Based-Framework-for-Word-Sense-Disambiguation-in-Serbian.git
cd A-Semi-Automated-LLM-Based-Framework-for-Word-Sense-Disambiguation-in-Serbian

# 2. Create and activate a virtual environment
python -m venv .env
# Windows:
.env\Scripts\activate
# Linux / macOS:
source .env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

For local Llama inference, install [Ollama](https://ollama.com/) and pull the
model: `ollama pull llama3.3`.

## Usage

1. Copy API keys into a `.env` file (see `config.py` for the expected variable names: `OPENAI_API_KEY`, `GOOGLE_GENAI_API_KEY`).
2. Place lexical resources in `Data/`.
3. Open one of the WSD notebooks (`ChatGPT_sense.ipynb`, `GEMINI_sense.ipynb`, `Llama_sense.ipynb`, or `SimpleWSD_sense.ipynb`).
4. The notebook will:
   - Load annotation chunks (`sr-elexis-WSD_*.tsv`).
   - Load the sense inventory (`Elexis-WSD-Repo-sr-v2.xlsx`).
   - Disambiguate each token/MWE via the selected model.
   - Write WebAnno-compatible TSVs to `output/`.

## Data

| File | Description |
|------|-------------|
| `Elexis-WSD-Repo-sr-v2.xlsx` | Enhanced sense inventory (Serbian WordNet + additional senses) |
| `Elexis-WSD-Repo-sr-v1.xlsx` | Original sense inventory used in Round I |
| `sr-elexis-WSD_XXXX_YYYY.tsv` | Pre-chunked annotation files (500 sentences each) |

## Citation

If you use this code or data, please cite:

```
@article{lexisense-sr-2026,
  title   = {A Semi-Automated LLM-Based Framework for Word Sense Disambiguation in Serbian},
  journal = {SAGE Journal},
  year    = {2026}
}
```

## License

See `LICENSE` for details.
