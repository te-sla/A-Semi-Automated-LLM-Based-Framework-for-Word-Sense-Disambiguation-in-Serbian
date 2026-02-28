# process_senses.py

> Part of the companion repository for *A Semi-Automated LLM-Based Framework
> for Word Sense Disambiguation in Serbian* (submitted to SAGE Journal).

Coordinates the LLM disambiguation workflow shared by the ChatGPT (GPT 4.1 /
GPT 5), Gemini, and Llama pipelines. Major components:

- `process_senses_with_chain(...)` – main entry point that iterates over
	sentences, prepares candidate senses via `preprocessing`, invokes a LangChain
	compatible `chain`, validates returned IDs against the allowed list, and
	writes the chosen sense metadata back to each token/MWE layer.
- Retry guard `_invoke_chain_with_validation` – prevents hallucinated sense IDs
	by re-querying the model up to `MAX_HALLUCINATION_RETRIES`, marking failures
	as `NEW_SENSE` with explanatory notes.
- Parsing utilities (`parse_model_output`, `default_build_senses_block`,
	`parse_json_response_clean`) – normalise various JSON-ish responses into a
	consistent `{sense_id, explanation}` structure for downstream use.
- Time-delayed variant `process_senses_with_chain_with_time_delay` – wraps the
	main routine with throttling for rate-limited APIs, incrementing the
	multi-token counter per sentence.

Tokens are annotated with the field names defined in `config.py`, which enables
`writers.py` to export WebAnno-compatible TSV files. Import the module and call
`process_senses_with_chain` from notebooks or scripts after loading sentences
and the sense repository DataFrame.
