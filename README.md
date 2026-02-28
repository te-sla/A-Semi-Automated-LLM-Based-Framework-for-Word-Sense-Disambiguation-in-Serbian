# LexiSense-SR

LexiSense-SR is a toolkit for word sense disambiguation (WSD) and lexical analysis, focused on Serbian language resources. It provides scripts, notebooks, and data for processing, evaluating, and experimenting with sense-annotated corpora and AI models.

## Features
- Word Sense Disambiguation (WSD) using multiple models (ChatGPT, Gemini, Llama)
- Knowledge-based WSD using domain-specific sense repositories
- Automatic extraction of multiword expressions
- Named-entity resolution and lemma-based filtering
- Data preprocessing and cleaning utilities
- Evaluation scripts and outputs for model predictions
- Logging of model outputs and processing steps for later review

## Project Structure
- `ChatGPT_sense.ipynb`, `GEMINI_sense.ipynb`, `Llama_sense.ipynb`: Notebooks for running and evaluating different AI models on sense disambiguation tasks.
- `config.py`, `preprocessing.py`, `domain.py`: Scripts for configuration, preprocessing, and domain logic.
- `Data/`: Main lexical resources and test datasets (e.g., `Elexis-WSD-Repo-sr-v2.xlsx`, `sr-elexis_*.tsv`).
- `output/`: Model outputs and evaluation results (e.g., `LexiSense.tsv`, `LexiSense_Debug.tsv`, `gemini_test.tsv`).
- `*.log`: Log files for model runs and processing steps.
- `*.tsv`, `*.csv`, `*.json`: Data files for input, output, and intermediate results.

## Installation

```powershell
# 1. Clone the repo
git clone https://github.com/te-sla/LexiSense-SR.git
cd LexiSense-SR

# 2. Create and activate a virtual environment
python -m venv .env
# On Windows:
.env\Scripts\activate
# On Linux/macOS:
source .env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Usage

1. Place your lexical resources in the `Data/` directory.
2. Open any of the provided Jupyter notebooks (e.g., `ChatGPT_sense.ipynb`, `GEMINI_sense.ipynb`, `Llama_sense.ipynb`) to experiment with different models.
3. The notebooks will:
   - Load input data (e.g., `sr-elexis_20250506.tsv`).
   - Use `Elexis-WSD-Repo-sr-v2.xlsx` as the sense repository.
   - Disambiguate each token’s sense via the selected AI model.
   - Write output files to the `output/` directory (e.g., `LexiSense.tsv`, `LexiSense_Debug.tsv`).
   - Log processing steps and model outputs for later review (see `*.log` files).

## Data
- **Elexis-WSD-Repo-sr-v2.xlsx:** Main sense-annotated lexicon (v1 available as `Elexis-WSD-Repo-sr-v1.xlsx`).
- **sr-elexis_*.tsv:** Processed or test datasets.
- **output/**: Contains model predictions and evaluation results.

## Logging
- Model runs and processing steps are logged in files like `gemini.log`, `llama.log`, and others for later review.

## License

See `LICENSE` for details.
