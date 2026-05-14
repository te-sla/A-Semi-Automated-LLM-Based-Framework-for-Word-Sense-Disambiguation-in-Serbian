# Targeted Update Status - 2026-05-11

## Source and Target

- Source working folder: `E:\Github\LexiSense-SR`
- Target presentation repository: `E:\Github\A-Semi-Automated-LLM-Based-Framework-for-Word-Sense-Disambiguation-in-Serbian`
- Update scope: targeted notebook, support-code, documentation, and output artifact sync.
- Output layout: round 1 files in `output/Phase1/`; round 2 files in `output/Phase2/`.

## Pre-Copy Git Status

Source repository had these uncommitted paths before copying:

```text
 M ChatGPT_sense.ipynb
 M Llama_sense.ipynb
 M Llama_sense_ablation_no_explanation.ipynb
 M Llama_sense_ablation_no_new_sense.ipynb
 M Llama_sense_ablation_simplified_prompt.ipynb
 M process_senses.py
?? tests/test_fill_ne_single_token_wsd.py
?? tools/fill_ne_single_token_wsd.py
```

Target repository had these uncommitted paths before copying:

```text
 M ChatGPT_sense.ipynb
 M GEMINI_sense.ipynb
 M Llama_sense.ipynb
 M README.md
 M SimpleWSD_sense.ipynb
 M config.py
 M doc/AI_Models_Usage.md
 M doc/data_loader.md
 M doc/file_overview.md
 M doc/writers.md
 M domain.py
 M postprocess_first_origin.ipynb
 M preprocessing.py
 M process_senses.py
 M requirements.txt
 M simple_wsd.py
 M test_mwe_fix.py
 M test_mwe_processing.py
 M tools/clean_wsd_layer_all.py
 M tools/clean_wsd_layer_test.py
 M tools/fix_existing_wsd_outputs.py
 M writers.py
?? .env.example
?? Data/example-mwe.tsv
```

## Copied Output Coverage

Copied paired standard and INCEpTION TSV artifacts for these origins:

- `Llama4`
- `MistralSmall3.2`
- `Llama4_simple`
- `Llama4_nonew`
- `Llama4_noexp`

For each origin, copied:

- `0001-0500`, round 1 and round 2
- `0501-0600`, round 1 and round 2

The available `0501-1000` SimpleWSD round 1 pair was also copied. Existing
presentation `IIIround` outputs were left in place.

## ChatGPT/GPT 0501-1000 Standard TSV Recovery

Two downloaded output archives were inspected for missing standard TSV files:

- `output (2).zip`: first-round outputs
- `output - jesen.zip`: second-round outputs

The presentation repository already had the matching INCEpTION `0501-1000`
files, so only the missing standard TSV files were copied:

| Destination | Source archive path |
|---|---|
| `output/Phase1/LexiSense_0501_1000_gpt-3.5_Iround_test.tsv` | `output (2).zip` -> `output/LexiSense_test_0501_1000_ChatGPT-3-5.tsv` |
| `output/Phase1/LexiSense_0501_1000_gpt-4.1_Iround.tsv` | `output (2).zip` -> `output/LexiSense_test_0501_1000_ChatGPT-4-1.tsv` |
| `output/Phase2/LexiSense_0501_1000_gpt-4.1_IIround.tsv` | `output - jesen.zip` -> `output/LexiSense_0501_1000_gpt-4.1_IIround.tsv` |
| `output/Phase2/LexiSense_0501_1000_gpt-5_IIround.tsv` | `output - jesen.zip` -> `output/LexiSense_0501_1000_gpt-5_IIround.tsv` |

## Missing / Not Yet Generated

These files were not present in `LexiSense-SR` as full `0501-1000` pairs, so
they were not copied:

- `Llama4`, round 1 and round 2
- `MistralSmall3.2`, round 1 and round 2
- `Llama4_simple`, round 1 and round 2
- `Llama4_nonew`, round 1 and round 2
- `Llama4_noexp`, round 1 and round 2
- all `GeminiPro_*` TSV output pairs

The accepted `0501-0600` jobs were not rerun.
