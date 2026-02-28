# simple_wsd.py

> Part of the companion repository for *A Semi-Automated LLM-Based Framework
> for Word Sense Disambiguation in Serbian* (submitted to SAGE Journal).

Implements the embedding-based WSD baseline (`all-MiniLM-L6-v2`) built on
cosine similarity between sentence-transformer embeddings and candidate glosses.
This serves as one of the two baseline models evaluated in the paper (alongside
the Serbian-specific XLM-RoBERTa model).

## Key functions

- `disambiguate_sentence(sentence, glosses, model=None, model_name="all-MiniLM-L6-v2")`
  – loads or reuses a `SentenceTransformer`, encodes the input sentence alongside
  the provided gloss definitions, and returns them ranked by cosine similarity.
  Useful for quick zero-shot experiments or CLI usage.
- `process_senses_with_simple_wsd(sentences, senses_df, …)` – drop-in replacement
  for the LLM pipeline in `process_senses.py`. For every MWE and eligible token
  (content word not inside an MWE) it:
  1. Retrieves candidate senses via `preprocessing.get_mwe_filtered_senses` or
     `preprocessing.get_token_senses`.
  2. Scores each definition using `_compute_similarity_scores`.
  3. Annotates the tokens with the best-matching sense ID, sense list, candidate
     count, origin tag, and a compact note summarising the top similarities.
  4. Falls back to the first sense with a `FIRST` origin marker when no scores
     can be produced.
- Utility helpers such as `_candidate_text_from_sense`, `_format_similarity_note`,
  and `_shorten` keep prompts concise and notes legible.
- The CLI section (`if __name__ == "__main__"`) allows quick manual trials by
  prompting for a sentence and gloss list.

## Dependencies and configuration

- Relies on `sentence-transformers` for embedding generation and uses the
  project constants from `config.py` to write WebAnno layers identical to the LLM
  workflow.
- Shares token/MWE utilities (`mark_token`, `mark_mwe`, filtering helpers) with
  `preprocessing.py` to highlight target spans consistently.

## Typical usage

```python
from data_loader import load_sense_repo, load_annotations_group
from simple_wsd import process_senses_with_simple_wsd

senses_df = load_sense_repo()
sentences = load_annotations_group(1, 500)
process_senses_with_simple_wsd(sentences, senses_df)
```

The returned sentences now carry sense annotations compatible with the TSV
writers in `writers.py`.
