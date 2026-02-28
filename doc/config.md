# config.py

Central repository for constants shared across the annotation and analysis
pipelines. The module loads optional environment variables (e.g.
`OPENAI_API_KEY`, `GOOGLE_GENAI_API_KEY`) via `python-dotenv`, defines the
project root, and exposes canonical paths for the `Data/`, `output/`, and
`stats/` directories.

Key groups of settings:

- **Annotation chunks** – `ANNOTATION_CHUNKS` enumerates the pre-split TSV
	ranges used during the second annotation round, while `ANNOTATIONS_TSV`
	preserves backwards compatibility with the first chunk.
- **Lexis field names** – constants such as `L_LEMMA`, `L_UPOS`, and the MWE
	field identifiers mirror WebAnno export column names, preventing typos in the
	processing code.
- **Sense repository columns** – `S_LEMMA`, `S_ID`, `S_DOMAIN`, etc., capture
	the expected schema of `Elexis-WSD-Repo-sr-v2.xlsx`.
- **Annotation output fields** – WebAnno custom layer keys (`SENSE_ID_FIELD`,
	`SENSE_LIST_FIELD`, `SENSE_AINOTES_FIELD`, `SENSE_COMMENT_FIELD`, `SENSE_ORIGIN`)
	used by `writers.py` and `process_senses.py` when emitting TSVs.
- **Filtering helpers** – `EVENT_FILTER` and `CONTENT_WORDS` encapsulate the
	heuristics applied in `preprocessing.collect_simple_word_senses`.

Import the constants you need instead of hard-coding strings or paths; this keeps
scripts, notebooks, and writers aligned even as field names evolve.
