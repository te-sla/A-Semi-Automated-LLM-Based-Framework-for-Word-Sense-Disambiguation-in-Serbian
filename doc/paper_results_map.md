# Paper results and repository guide

This guide connects the [IDA article](https://doi.org/10.1177/1088467X261469292) with the data, model notebooks and prediction exports in this repository. See the [README](../README.md) for the study overview and reported results, and [CITATION.cff](../CITATION.cff) for citation metadata.

## Inventories and evaluation sets

| Resource | Repository files | Use |
| --- | --- | --- |
| Round 1 inventory | [v1 workbook](../Data/Elexis-WSD-Repo-sr-v1.xlsx) | Original sense inventory, configured as `SENSE_REPO_OLD`. |
| Round 2 inventory | [v2 workbook](../Data/Elexis-WSD-Repo-sr-v2.xlsx) | Expanded sense inventory, configured as `SENSE_REPO`. |
| Development set | [Sentences 0001–0120](../Data/gold_eval/sr-elexis-WSD_0001_0120-gold.tsv) | 120 manually checked development sentences. |
| Held-out test set | [0301–0400](../Data/gold_eval/sr-elexis-WSD_0301-0400-gold.tsv), [0401–0500](../Data/gold_eval/sr-elexis-WSD_0401-0500-gold.tsv), [0501–0600](../Data/gold_eval/sr-elexis-WSD_0501-0600-gold.tsv) | Three files containing 300 test sentences in total. |
| Annotation inputs | [0001–0500](../Data/sr-elexis-WSD_0001_0500.tsv), [0501–1000](../Data/sr-elexis-WSD_0501_1000.tsv) | Input chunks used by the model notebooks; ranges are defined in [config.py](../config.py). |

Keep the 120-sentence development set separate from the 300-sentence test set. When using a larger prediction export, select the evaluation sentence IDs and the corresponding inventory round. See the [gold-set instructions](../Data/gold_eval/README.md).

## Models, procedures and outputs

| Study component | Procedure | Repository resources |
| --- | --- | --- |
| Inventory construction and candidate senses | Prepare lexical entries and collect candidates for each target. | [preprocessing.py](../preprocessing.py), [data_loader.py](../data_loader.py), v1/v2 workbooks above. |
| GPT-4.1 and GPT-5.1 | Structured sense selection using the OpenAI model notebook and shared WSD pipeline. | [ChatGPT_sense.ipynb](../ChatGPT_sense.ipynb), [process_senses.py](../process_senses.py); OpenAI prediction exports in [Phase2](../output/Phase2/). |
| Embedding baselines: simple, tesla and mling | Rank candidate definitions by cosine similarity. The mling preset uses `intfloat/multilingual-e5-large`. | [SimpleWSD_sense.ipynb](../SimpleWSD_sense.ipynb), [simple_wsd.py](../simple_wsd.py), model presets in [config.py](../config.py). |
| Lesk baseline | Compare context and candidate definitions with the Lesk-style baseline. | [BaselineWSD_sense.ipynb](../BaselineWSD_sense.ipynb); Round 2 exports for [0001–0500](../output/Phase2/LexiSense_0001_0500_baseline_lesk_round2.tsv) and [0501–0600](../output/Phase2/LexiSense_0501_0600_baseline_lesk_round2.tsv). |
| Llama4, MistralSmall3.2 and Llama prompt variants | Run model-specific notebooks with the selected prompt and inventory. | [Llama_sense.ipynb](../Llama_sense.ipynb), [Mistral_sense.ipynb](../Mistral_sense.ipynb), ablation notebooks listed in the [README](../README.md); exports in [Phase1](../output/Phase1/) and [Phase2](../output/Phase2/). |
| Gemini Pro | Run the Gemini Pro sense-selection notebook. | [GEMINI_pro_sense.ipynb](../GEMINI_pro_sense.ipynb). |
| Evaluation and statistical comparisons | Compare predictions against the appropriate gold set using the span definitions, treatment of unmatched answers and subgroup definitions described in the article. | Gold files above; evaluation protocol and reported tables in the [article](https://doi.org/10.1177/1088467X261469292). |

## Working with the examples

1. Choose the model, inventory round and input sentence range in the relevant notebook before running it.
2. Use `output/Phase1/` for Round 1 exports and `output/Phase2/` for Round 2 exports. Inspect each file’s sentence range when assembling an evaluation subset.
3. Compare predictions with the manually checked gold labels. The [inter-model agreement notebook](../post_anntotaion_stats.ipynb) and [stats directory](../stats/) provide a separate analysis of agreement between systems.

The tables above link the resources included in the repository. For experimental settings, reported scores and statistical interpretation, use the article together with the corresponding data and model instructions.
