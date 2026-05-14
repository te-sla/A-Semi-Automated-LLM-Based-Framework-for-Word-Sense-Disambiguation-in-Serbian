# Ablation Run Checklist

Use this file to track the first 600 sentences for each ablation variant across both sense-repo rounds.

Completion rule:
- Mark a run done only when both the standard TSV and the Inception TSV exist.
- Keep the notebook configured to the exact round, chunk, and range before starting a run.

Coverage target:
- Round 1: sentences 1-500 and 501-600
- Round 2: sentences 1-500 and 501-600

## Variants

| Variant | Notebook | Origin label |
|---------|----------|--------------|
| Simplified prompt | `Llama_sense_ablation_simplified_prompt.ipynb` | `Llama4_simple` |
| No NEW_SENSE | `Llama_sense_ablation_no_new_sense.ipynb` | `Llama4_nonew` |
| No explanation | `Llama_sense_ablation_no_explanation.ipynb` | `Llama4_noexp` |

## Checklist

### Llama4_simple
- [x] Round 1, sentences 1-500
- [x] Round 1, sentences 501-600
- [x] Round 2, sentences 1-500
- [x] Round 2, sentences 501-600

### Llama4_nonew
- [x] Round 1, sentences 1-500
- [x] Round 1, sentences 501-600
- [x] Round 2, sentences 1-500
- [x] Round 2, sentences 501-600

### Llama4_noexp
- [x] Round 1, sentences 1-500
- [x] Round 1, sentences 501-600
- [x] Round 2, sentences 1-500
- [x] Round 2, sentences 501-600

## Status

All first-600 ablation runs are complete for `Llama4_simple`, `Llama4_nonew`, and `Llama4_noexp` across both rounds.