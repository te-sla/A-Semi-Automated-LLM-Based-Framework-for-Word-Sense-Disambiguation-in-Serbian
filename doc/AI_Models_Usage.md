# AI Models Usage

> Part of the companion repository for *A Semi-Automated LLM-Based Framework
> for Word Sense Disambiguation in Serbian* (submitted to SAGE Journal).

This document summarizes the model notebooks and output traceability used by
the Serbian WSD framework.

## Models Summary

| Model / origin label | Type | Integration | API required | Notebook / file |
|---|---|---|---|---|
| GPT-5 / GPT-4.1 | Cloud LLM | LangChain + OpenAI | Yes | `ChatGPT_sense.ipynb` |
| Gemini 2.0 Flash Lite | Cloud LLM | LangChain + Google GenAI | Yes | `GEMINI_sense.ipynb` |
| Gemini Pro (`GeminiPro_*`) | Cloud LLM | LangChain + Google GenAI | Yes | `GEMINI_pro_sense.ipynb` |
| Llama4 (`Llama4`) | Local LLM | LangChain + Ollama | No | `Llama_sense.ipynb` |
| MistralSmall3.2 | Local LLM | LangChain + Ollama | No | `Mistral_sense.ipynb` |
| Llama4 ablations | Local LLM | LangChain + Ollama | No | `Llama_sense_ablation_*.ipynb` |
| SimpleWSD / Tesla / mling | Embeddings | Sentence Transformers | No | `SimpleWSD_sense.ipynb`, `simple_wsd.py` |
| Lesk baseline | Knowledge baseline | Local notebook logic | No | `BaselineWSD_sense.ipynb` |

## OpenAI ChatGPT

`ChatGPT_sense.ipynb` contains the primary OpenAI WSD notebook. It uses the
shared `process_senses.py` loop and writes WebAnno and INCEpTION TSV outputs.

## Google Gemini

`GEMINI_sense.ipynb` is the Gemini 2.0 Flash Lite notebook. `GEMINI_pro_sense.ipynb`
is the Gemini Pro notebook and includes configurable model selection between a
stable Pro model and a preview model.

Gemini Pro output files were not present in the working repository at the time
of this targeted update, so no `GeminiPro_*` TSV pairs were copied into the
presentation repository.

## Llama and Mistral via Ollama

`Llama_sense.ipynb` uses the `Llama4` origin label. `Mistral_sense.ipynb` uses
the `MistralSmall3.2` origin label. Both notebooks use local Ollama-backed
LangChain chains and the shared `process_senses_with_chain` workflow.

The imported local-model artifacts cover:

| Origin | Ranges | Rounds | Output location |
|---|---|---|---|
| `Llama4` | `0001-0500`, `0501-0600` | 1 and 2 | `output/Phase1/`, `output/Phase2/` |
| `MistralSmall3.2` | `0001-0500`, `0501-0600` | 1 and 2 | `output/Phase1/`, `output/Phase2/` |

Full `0501-1000` pairs for these origins are not present yet. The accepted
`0501-0600` runs should not be rerun during this update.

## Llama Ablations

Three Llama4 ablation notebooks are included:

| Variant | Notebook | Origin label |
|---|---|---|
| Simplified prompt | `Llama_sense_ablation_simplified_prompt.ipynb` | `Llama4_simple` |
| No `NEW_SENSE` | `Llama_sense_ablation_no_new_sense.ipynb` | `Llama4_nonew` |
| No explanation | `Llama_sense_ablation_no_explanation.ipynb` | `Llama4_noexp` |

Each ablation has copied TSV pairs for `0001-0500` and `0501-0600`, round 1 and
round 2. Full `0501-1000` ablation pairs are not present yet. See
`ablation_run_checklist.md` for the first-600 completion checklist.

## Simple WSD and Baselines

`SimpleWSD_sense.ipynb` and `simple_wsd.py` provide embedding-based WSD. The
copied support script `tools/run_simple_wsd_range.py` can run configured
sentence-transformer presets across both sense-repository rounds.

The available SimpleWSD `0501-1000` round 1 pair was copied into
`output/Phase1/`. Exact `_round2` SimpleWSD `0501-1000` files were not present
under the same naming convention in the working repository; existing
presentation `IIIround` files are preserved.

## Output Traceability

Presentation outputs keep the phase layout:

- Round 1 files are stored under `output/Phase1/`.
- Round 2 files are stored under `output/Phase2/`.
- Imported local-model files preserve source names such as
  `LexiSense_0501_0600_Llama4_round2.tsv`.
- Each copied model/range output should have both the standard `LexiSense_...`
  TSV and the `LexiSense_Inception_...` TSV.

## Environment Variables

`config.py` reads cloud credentials from environment variables:

```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY", "")
```

Local Ollama notebooks require Ollama to be running and the requested local
model to be available.
