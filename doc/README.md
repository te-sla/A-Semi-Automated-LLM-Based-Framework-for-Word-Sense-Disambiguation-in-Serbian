Project Documentation
=====================

> Companion repository for *A Semi-Automated LLM-Based Framework for Word Sense
> Disambiguation in Serbian* (accepted for publication; DOI and final citation pending).

This folder contains detailed documentation for all modules and notebooks in the
repository. The documentation is organised by file, providing an overview of the
purpose, architecture, and usage of each component.

| File | Covers |
|------|--------|
| [file_overview.md](file_overview.md) | High-level map of the entire repo |
| [AI_Models_Usage.md](AI_Models_Usage.md) | All AI/LLM models, integration details, prompt templates |
| [config.md](config.md) | `config.py` – paths, constants, field names |
| [data_loader.md](data_loader.md) | `data_loader.py` – sense-repo & TSV loaders |
| [preprocessing.md](preprocessing.md) | `preprocessing.py` – token/MWE filtering |
| [process_senses.md](process_senses.md) | `process_senses.py` – LLM disambiguation loop |
| [writers.md](writers.md) | `writers.py` – WebAnno / INCEpTION export |
| [domain.md](domain.md) | `domain.py` – EN → SR domain labels |
| [simple_wsd.md](simple_wsd.md) | `simple_wsd.py` – embedding baseline |
| [ChatGPT_sense.md](ChatGPT_sense.md) | ChatGPT WSD notebook |
| [GEMINI_sense.md](GEMINI_sense.md) | Gemini WSD notebook |
| [Llama_sense.md](Llama_sense.md) | Llama WSD notebook |
| [post_anntotaion_stats.md](post_anntotaion_stats.md) | Post-annotation statistics notebook |
