# LexiSense-SR: File Overview

## Python Source Files

### config.py
Loads environment-backed secrets and collects shared constants. Defines the
canonical paths for `Data/`, `output/`, and `stats/`, enumerates the annotation
chunk TSVs, and centralises WebAnno layer names (lemma, POS, MWE, and sense
fields) together with filtering helpers (`CONTENT_WORDS`, `EVENT_FILTER`).

### domain.py
Provides the English→Serbian domain label map used for presenting sense
metadata. Exposes `translate_domain` to normalise raw domain strings and fall
back to `"nepoznato"` when a key is unknown.

### preprocessing.py
Utility helpers that operate on `webanno_spacy_converter` sentence objects:
highlighting MWEs/tokens, filtering tokens based on MWE/NER/UPOS layers, and
collecting candidate senses for MWEs and single tokens from the Sense
Repository DataFrame.

### process_senses.py
Implements the LLM-driven disambiguation loop. Orchestrates sense candidate
generation (via `preprocessing`), calls a LangChain-style `chain`, validates the
returned sense IDs, and writes the results onto token layers so they can be
exported. Includes retry logic and a time-delayed variant for rate-limited
models.

### writers.py
Defines two WebAnno TSV writers tailored for the project:
`CustomWebAnnoTSVWriter` (generic export) and
`IncetprionWebAnnoTSVWriter` (Inception schema). Both extend the base writer to
emit the exact layer order and decorate identifiers/URIs.

### data_loader.py
Loads the Sense Repository Excel file and chunked WebAnno TSV annotations. It
also enumerates available TSV groups, provides helper path builders, and offers
iterators for streaming sentence batches.

### simple_wsd.py
Embeddings-based baseline that ranks candidate glosses with a sentence
transformer and annotates tokens/MWEs accordingly, mirroring the WebAnno layer
schema of the LLM pipeline.

## Notebooks

### ChatGPT_sense.ipynb, GEMINI_sense.ipynb, Llama_sense.ipynb
Jupyter notebooks for running and analyzing sense assignment using different LLM pipelines (ChatGPT, Gemini, Llama). Each notebook typically loads model outputs, processes sense assignments, and visualizes results.

### post_anntotaion_stats.ipynb
Notebook for post-hoc analysis and comparison of sense-annotated TSV files. Computes statistics (e.g., NEW_SENSE assignments), compares model outputs, and measures agreement/disagreement between models.

### cuda_test.ipynb, test.ipynb
Utility notebooks for testing CUDA setup and running miscellaneous tests or experiments.

## Data and Output

### Data/
Contains input data files, such as:
- Elexis-WSD-Repo-sr-v2.xlsx: Main lexical resource (current version).
- Elexis-WSD-Repo-sr-v1.xlsx: Previous version of the lexical resource.
- sr-elexis_*.tsv: Sense-annotated TSV files for Serbian.
- test_sr_lexix.tsv: Test data for evaluation.

### output/
Stores model outputs and processed results, including:
- *_test_out*.tsv: Model predictions for test sets.
- gemini_*, LexiSense_*, llama_*: Outputs from different models and experiments.

### stats/
Contains derived CSV statistics (agreement scores, NEW_SENSE counts, etc.)
produced by the notebooks and analysis scripts.

## Other Files

### requirements.txt, dev-requirements.txt
Lists required Python packages for running the project and for development.

### README.md
Project overview, setup instructions, and usage guide.

### LICENSE
Project license information.

### mwe_dist.csv, token_dist.csv, simple_words_senses_distribution.csv
CSV files with statistics on MWEs, token distributions, and sense distributions.

### mwe_for_save.json, simple_words_senses.json
JSON files with serialized MWE and sense data.

### mwe_with_more_than_one_sense.txt, mwe_with_no_sense.txt
Text files listing MWEs with multiple or no sense assignments.

### .gitignore, .gitattributes
Git configuration files.

### __pycache__/
Python bytecode cache directory.

---
For detailed documentation on each file, see the corresponding markdown files in this folder.
