# Paper results and archived artifacts

This map accompanies [the IDA article](https://doi.org/10.1177/1088467X261469292) and the [repository README](../README.md). It records what can be traced in repository revision [`80f8f64bcc899c28a59c9954e0eca4817a27f1dc`](https://github.com/te-sla/A-Semi-Automated-LLM-Based-Framework-for-Word-Sense-Disambiguation-in-Serbian/tree/80f8f64bcc899c28a59c9954e0eca4817a27f1dc), checked on 23 September 2026. This revision has not been established as the exact release underlying the published paper. The published scores and authorship in the README are unchanged.

## Evidence labels

- **Confirmed**: the stated artifact, structure or configuration was directly checked. This does not certify an unexecuted evaluation or a numerical result.
- **Partially supported**: relevant inputs, procedures or prediction files exist, but the complete connection to a reported result has not been established.
- **Unverified**: a required output or provenance link was not located in the checked repository. Do not fill the gap with an assumed result.

Result names are used as anchors so the map remains useful across manuscript and publisher layouts. No new accuracy, significance or inventory-statistics results were computed for this documentation update.

## Inventory and input map

| Paper component | Inventory / input | Procedure or recorded role | Saved artifact and status |
| --- | --- | --- | --- |
| Round 1 inventory | [v1 workbook](../Data/Elexis-WSD-Repo-sr-v1.xlsx) | [config.py](../config.py) identifies it as `SENSE_REPO_OLD` for Round 1. | **Confirmed** path and configuration role. Historical inventory counts and spreadsheet content were not recalculated. |
| Round 2 inventory | [v2 workbook](../Data/Elexis-WSD-Repo-sr-v2.xlsx) | [config.py](../config.py) uses it as `SENSE_REPO`. | **Confirmed** path and configuration role. Round 2 uses the expanded inventory; it is not a second name for v1. |
| Development evaluation | [gold sentences 0001–0120](../Data/gold_eval/sr-elexis-WSD_0001_0120-gold.tsv) | Restrict predictions and gold to these sentence IDs and the stated inventory round before scoring. | **Confirmed** 120 sentence blocks (`#Text=`); [gold-set documentation](../Data/gold_eval/README.md). |
| Held-out test evaluation | [0301–0400](../Data/gold_eval/sr-elexis-WSD_0301-0400-gold.tsv), [0401–0500](../Data/gold_eval/sr-elexis-WSD_0401-0500-gold.tsv), [0501–0600](../Data/gold_eval/sr-elexis-WSD_0501-0600-gold.tsv) | Combine these three 100-sentence gold files for the 300-sentence test set. Keep the development set separate. | **Confirmed** 100 sentence blocks per file, 300 total. A prediction file covering 0001–0500 contains more than the selected evaluation ranges. |
| Annotation input chunks | [0001–0500](../Data/sr-elexis-WSD_0001_0500.tsv), [0501–1000](../Data/sr-elexis-WSD_0501_1000.tsv) | [config.py](../config.py) declares the chunk ranges; model notebooks read these inputs. | **Confirmed** paths and declared role. These chunks are not substitutes for the manually checked gold files. |

## Result → input → procedure → saved output

In each row, evaluation requires the appropriate gold subset above. Merely locating a prediction file is insufficient to certify a paper score: span matching, ignored/unmatched outputs, the inventory round and the model identity must also agree.

| Paper result or table group | Inventory and evaluation input | Procedure | Saved output / evidence | Status of the result-to-output link |
| --- | --- | --- | --- | --- |
| Inventory statistics and candidate-sense distributions | v1 and v2 workbooks; development and held-out gold subsets as applicable | Inventory construction and candidate collection; [preprocessing.py](../preprocessing.py), [data_loader.py](../data_loader.py) | Input workbooks and code are present; a complete table-generation export tied to the published inventory/distribution values was not identified. | **Partially supported**; inputs exist, published counts not rederived. |
| Development comparisons across inventory rounds | 120 development sentences; v1 for Round 1 and v2 for Round 2 | Model-specific notebooks, shared [process_senses.py](../process_senses.py), span-level comparison against development gold | Archived [Phase1](../output/Phase1/) and [Phase2](../output/Phase2/) predictions cover development ranges for several systems. No complete saved gold-scoring bundle was located for all reported systems and breakdowns. | **Partially supported**; a complete paper-table reproduction is not established. |
| GPT-4.1, Round 2 held-out: 92.7% overall / 92.4% single-word / 95.2% multi-word | v2; test sentences 0301–0600 | [ChatGPT_sense.ipynb](../ChatGPT_sense.ipynb) and shared WSD pipeline, followed by gold evaluation | [0001–0500 GPT-4.1 export](../output/Phase2/LexiSense_Inception_0001_0500_gpt-4.1_IIround.tsv) and [0501–1000 GPT-4.1 export](../output/Phase2/LexiSense_Inception_0501_1000_gpt-4.1_IIround.tsv) cover the needed ranges. | **Partially supported**; prediction files exist, but an exact saved scorer invocation and metric table tied to these files were not located. |
| GPT-5.1, Round 2 held-out: 83.6% / 82.5% / 93.0% | v2; the same 300-sentence test set | GPT notebook / shared pipeline; historical model identity must be established separately | Available files are named [0001–0500 `gpt-5`](../output/Phase2/LexiSense_Inception_0001_0500_gpt-5_IIround.tsv) and [0501–1000 `gpt-5`](../output/Phase2/LexiSense_Inception_0501_1000_gpt-5_IIround.tsv). | **Unverified** for the exact GPT-5.1 result. Filenames and the current notebook say `gpt-5`; this is not proof of a GPT-5.1 run. |
| Best embedding baseline `mling`, Round 2 held-out: 59.2% / 56.0% / 86.1% | v2; the same test set | [SimpleWSD_sense.ipynb](../SimpleWSD_sense.ipynb), [simple_wsd.py](../simple_wsd.py); `mling` maps to `intfloat/multilingual-e5-large` in [config.py](../config.py) | No explicitly `mling`-identified prediction export was located. Archived `simple_wsd_IIIround` and `simple_wsd_tesla_IIIround` files are not evidence that the multilingual E5 result is stored under another name. | **Unverified** exact output and score. The current notebook's round setting also needs to be selected explicitly for a future run. |
| Lesk baseline, Round 2 held-out: 53.6% / 50.0% / 86.6% | v2; the same test set | [BaselineWSD_sense.ipynb](../BaselineWSD_sense.ipynb), followed by gold evaluation | [0001–0500 Lesk](../output/Phase2/LexiSense_0001_0500_baseline_lesk_round2.tsv), [0501–0600 Lesk](../output/Phase2/LexiSense_0501_0600_baseline_lesk_round2.tsv) | **Partially supported**; required sentence ranges are covered, but the final score export was not identified. |
| Llama4, MistralSmall3.2 and Llama prompt ablations | v1/v2 and the stated gold subset | [Llama notebook](../Llama_sense.ipynb), [Mistral notebook](../Mistral_sense.ipynb), ablation notebooks listed in the README | Both phase directories contain 0001–0500 and 0501–0600 exports; see [import/provenance notes](targeted_update_status_2026-05-11.md). | **Partially supported**. These ranges include development and held-out subsets, but not a full 0501–1000 archive for these systems. |
| Gemini Pro comparisons | Appropriate inventory and evaluation subset | [GEMINI_pro_sense.ipynb](../GEMINI_pro_sense.ipynb) | The notebook exists; corresponding `GeminiPro_*` range-output pairs were not located. | **Unverified** saved predictions and result binding. |
| Accuracy by UPOS / number of candidate senses, unmatched-output counts, confidence intervals and pairwise McNemar results | Matched system predictions, round-specific inventory and the explicitly selected gold subset | The paper's evaluation protocol; gold scoring and paired statistical comparison | No complete machine-readable package binding all these paper tables/figures to input hashes, scoring settings and outputs was identified. | **Unverified** full reproduction. Do not substitute inter-model agreement for gold accuracy. |

## Current settings are not a historical run manifest

- The checked [GPT notebook](../ChatGPT_sense.ipynb) selects `model = "gpt-5"` and a test mode that restricts processing to the first 20 sentences. Those settings do not reproduce a full GPT-5.1 test run as-is.
- The checked [embedding notebook](../SimpleWSD_sense.ipynb) selects the `mling` preset but Round 1. A preset's presence does not prove that its reported Round 2 outputs were archived.
- Legacy suffixes such as `IIIround` must not be interpreted as a third published inventory version without provenance evidence. Only v1 and v2 are mapped here.
- [post_anntotaion_stats.ipynb](../post_anntotaion_stats.ipynb) and the [stats directory](../stats/) contain inter-model agreement analysis. They are not a verified replacement for scoring predictions against the development/test gold data.

## Remaining artifacts needed for complete reproduction

1. A manifest tying every published result to model/provider version, inventory hash, input/gold hashes, prompt variant and prediction files.
2. A confirmed identity link for the published GPT-5.1 predictions and the missing `mling` exports.
3. The exact gold-scoring procedure and saved metric outputs, including span alignment, unmatched-output handling, subgroup denominators and statistical comparisons.
4. Missing Gemini Pro prediction pairs; full 0501–1000 local-model/ablation pairs if reproducing the wider annotation archive rather than only the evaluation subsets.

These are documented gaps. Generating missing predictions, rerunning paid models, revising scores and changing code are outside this documentation update.
