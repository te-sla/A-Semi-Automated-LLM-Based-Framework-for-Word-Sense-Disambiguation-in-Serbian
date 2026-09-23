# A Semi-Automated LLM-Based Framework for Word Sense Disambiguation in Serbian

Companion code and data for the paper:

> **A Semi-Automated LLM-Based Framework for Word Sense Disambiguation in Serbian**
> Published online in *Intelligent Data Analysis* on 22 August 2026.
> [https://doi.org/10.1177/1088467X261469292](https://doi.org/10.1177/1088467X261469292)

This repository implements a semi-automated annotation workflow for Word Sense
Disambiguation (WSD) in Serbian, leveraging Large Language Models (LLMs) through
specialised prompt engineering with zero-shot inference and constrained
JSON-formatted output. The framework guides LLMs in selecting the appropriate
sense from a custom inventory built on the Serbian WordNet and enhanced with
additional senses.

## Key Results

| Model | Overall accuracy | Single-word accuracy | Multi-word accuracy |
|-------|------------------|----------------------|---------------------|
| GPT-4.1 (Round 2 held-out test) | 92.7 % | 92.4 % | 95.2 % |
| GPT-5.1 (Round 2 held-out test) | 83.6 % | 82.5 % | 93.0 % |
| Best non-LLM baseline (`mling`) | 59.2 % | 56.0 % | 86.1 % |
| Lesk baseline (`base-lesk`) | 53.6 % | 50.0 % | 86.6 % |

## Paper-to-artifact map

See [the paper results and artifact map](doc/paper_results_map.md) for the link between paper results, the two inventory rounds, the **120-sentence development set**, the **300-sentence held-out test set**, inference procedures and saved outputs. Each mapping is marked **confirmed**, **partially supported** or **unverified**. The map explicitly records missing evaluation outputs and the GPT-5/GPT-5.1 naming discrepancy; it does not claim that all paper scores can be reproduced from the current archive.

Machine-readable citation metadata is available in [CITATION.cff](CITATION.cff). The inspected revision is [`80f8f64bcc899c28a59c9954e0eca4817a27f1dc`](https://github.com/te-sla/A-Semi-Automated-LLM-Based-Framework-for-Word-Sense-Disambiguation-in-Serbian/tree/80f8f64bcc899c28a59c9954e0eca4817a27f1dc), checked on 23 September 2026. It is a current documentation snapshot, not a verified historical release used for the publication.

## Features

- **LLM-based WSD** - zero-shot sense disambiguation via GPT 4.1 / GPT 5, Gemini 2.0 Flash Lite, Gemini Pro, Llama4, and MistralSmall3.2.
- **Llama ablations** - simplified prompt, no `NEW_SENSE`, and no-explanation variants for the first 600 sentences in both sense-repository rounds.
- **Baselines** - cosine-similarity WSD with `all-MiniLM-L6-v2`, `te-sla/TeslaXLM`, and `intfloat/multilingual-e5-large`, plus a Lesk-style knowledge baseline.
- **Custom sense inventory** - Serbian WordNet senses enriched with additional entries (`Elexis-WSD-Repo-sr-v2.xlsx`).
- **Semi-automated annotation** - structured prompts produce constrained JSON; multi-round workflow with validation and retry logic.
- **Multi-word expression handling** - automatic MWE extraction and disambiguation.
- **WebAnno / INCEpTION export** - TSV writers compatible with both annotation platforms.

## Repository Structure

```text
ChatGPT_sense.ipynb                  # GPT 4.1 / GPT 5 WSD pipeline
GEMINI_sense.ipynb                   # Gemini 2.0 Flash Lite WSD pipeline
GEMINI_pro_sense.ipynb               # Gemini Pro WSD pipeline
Llama_sense.ipynb                    # Llama4 local WSD pipeline via Ollama
Llama_sense_ablation_*.ipynb         # Llama4 ablation notebooks
Mistral_sense.ipynb                  # MistralSmall3.2 WSD pipeline
SimpleWSD_sense.ipynb                # Embedding-baseline WSD notebook
BaselineWSD_sense.ipynb              # Lesk-style baseline notebook
post_anntotaion_stats.ipynb          # Inter-model agreement and statistics
config.py                            # Paths, constants, field names
preprocessing.py                     # Token/MWE filtering and sense collection
process_senses.py                    # Shared LLM disambiguation loop
data_loader.py                       # Sense-repo and chunked-TSV loaders
domain.py                            # EN-to-SR domain-label translation
writers.py                           # WebAnno / INCEpTION TSV export
simple_wsd.py                        # Sentence-transformer baseline
Data/
  Elexis-WSD-Repo-sr-v2.xlsx         # Current sense inventory
  Elexis-WSD-Repo-sr-v1.xlsx         # Round 1 sense inventory
  sr-elexis-WSD_*.tsv                # Annotation chunks
  gold_eval/                         # Development and held-out gold TSVs
output/
  Phase1/                            # Round 1 exports and imported artifacts
  Phase2/                            # Round 2 exports and imported artifacts
stats/                               # Agreement CSVs produced by notebooks
doc/                                 # Per-file documentation
```

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/te-sla/A-Semi-Automated-LLM-Based-Framework-for-Word-Sense-Disambiguation-in-Serbian.git
cd A-Semi-Automated-LLM-Based-Framework-for-Word-Sense-Disambiguation-in-Serbian

# 2. Create and activate a virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux / macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

For local Llama or Mistral inference, install [Ollama](https://ollama.com/) and
pull the required local model, for example `ollama pull llama4` or the Mistral
model used by your local Ollama setup.

## Usage

1. Copy API keys into a `.env` file. `config.py` reads `OPENAI_API_KEY` and `GOOGLE_GENAI_API_KEY`.
2. Place lexical resources in `Data/`.
3. Open one of the WSD notebooks: `ChatGPT_sense.ipynb`, `GEMINI_sense.ipynb`, `GEMINI_pro_sense.ipynb`, `Llama_sense.ipynb`, `Mistral_sense.ipynb`, or `SimpleWSD_sense.ipynb`.
4. The notebook loads annotation chunks, loads the sense inventory, disambiguates each token/MWE via the selected model, and writes WebAnno-compatible TSVs to `output/Phase1/` or `output/Phase2/`.

## Run Status

Imported local-model, ablation, and Lesk-baseline artifacts currently cover
sentences `0001-0500` and `0501-0600` for both round 1 and round 2. These
files are stored in the presentation layout: round 1 under `output/Phase1/`
and round 2 under `output/Phase2/`.

The following full-range artifacts are not present in the working repository
yet and therefore are not included here: `0501-1000` pairs for `Llama4`,
`MistralSmall3.2`, `Llama4_simple`, `Llama4_nonew`, `Llama4_noexp`, and all
`GeminiPro_*` range output pairs. Do not rerun the accepted `0501-0600` jobs
when refreshing this repository.

## Data

| File | Description |
|------|-------------|
| `Elexis-WSD-Repo-sr-v2.xlsx` | Enhanced sense inventory (Serbian WordNet + additional senses) |
| `Elexis-WSD-Repo-sr-v1.xlsx` | Original sense inventory used in round 1 |
| `sr-elexis-WSD_XXXX_YYYY.tsv` | Pre-chunked annotation files (500 sentences each) |
| `gold_eval/sr-elexis-WSD_0001_0120-gold.tsv` | 120-sentence development gold set |
| `gold_eval/sr-elexis-WSD_0301-0400-gold.tsv`, `0401-0500`, `0501-0600` | Three 100-sentence held-out gold files, 300 test sentences total |

## Citation

If you use this code or data, please cite:

```bibtex
@article{petalinkar2026semi,
  author  = {Petalinkar, Saša and Stanković, Ranka and Ikonić Nešić, Milica and Krstev, Cvetana},
  title   = {A Semi-Automated LLM-Based Framework for Word Sense Disambiguation in Serbian},
  journal = {Intelligent Data Analysis},
  year    = {2026},
  doi     = {10.1177/1088467X261469292},
  url     = {https://doi.org/10.1177/1088467X261469292},
  note    = {OnlineFirst}
}
```

## License

See `LICENSE` for details.

The existing [LICENSE](LICENSE) declares **CC0-1.0** and is unchanged. Its scope does not override the rights in external lexical resources, ELEXIS-derived annotation material or model weights. Check the original data and model terms for the versions you use; this repository's license alone does not establish permission to redistribute every external resource. Article citation and model/resource attribution remain separate from the software license.
