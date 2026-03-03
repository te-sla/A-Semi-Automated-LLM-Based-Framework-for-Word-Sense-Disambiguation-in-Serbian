# AI Models Usage

> Part of the companion repository for *A Semi-Automated LLM-Based Framework
> for Word Sense Disambiguation in Serbian* (submitted to SAGE Journal).

This document provides a comprehensive overview of all AI/LLM models used in
the WSD framework for Serbian language resources.

---

## Table of Contents

1. [Overview](#overview)
2. [Models Summary](#models-summary)
3. [OpenAI ChatGPT](#openai-chatgpt)
4. [Google Gemini](#google-gemini)
5. [Llama (Local via Ollama)](#llama-local-via-ollama)
6. [Simple WSD (Sentence Transformers)](#simple-wsd-sentence-transformers)
7. [Configuration](#configuration)
8. [Shared Pipeline Architecture](#shared-pipeline-architecture)
9. [Output Traceability](#output-traceability)

---

## Overview

LexiSense-SR uses multiple AI models to annotate tokens with sense information from a lexical repository. The project supports:

- **Cloud-based LLMs**: OpenAI ChatGPT, Google Gemini
- **Local LLMs**: Llama via Ollama
- **Embedding models**: Sentence Transformers

All LLM pipelines share a common architecture using LangChain for prompt management and chain composition.

---

## Models Summary

| Model | Type | Integration | API Required | Notebook/File |
|-------|------|-------------|--------------|---------------|
| GPT-5 / GPT-4.1-nano | Cloud LLM | LangChain + OpenAI | Yes | `ChatGPT_sense.ipynb` |
| Gemini 2.0 Flash Lite | Cloud LLM | LangChain + Google GenAI | Yes | `GEMINI_sense.ipynb` |
| Llama 3.3 | Local LLM | LangChain + Ollama | No | `Llama_sense.ipynb` ¹ |
| all-MiniLM-L6-v2 | Embeddings | Sentence Transformers | No | `simple_wsd.py` |

¹ Llama was not used in the paper due to computational constraints on the available local machine (see [Llama section](#llama-local-via-ollama) for details).

---

## OpenAI ChatGPT

### Models Used
- `gpt-5` - Primary model for WSD

### Integration

```python
from langchain_openai import ChatOpenAI

# Initialize the model
llm = ChatOpenAI(
    model="gpt-5",
    api_key=OPENAI_API_KEY
)
```

### Usage in Pipeline

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Create the chain
prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("user", USER_PROMPT_TEMPLATE)
])

chain = prompt | llm | JsonOutputParser()

# Invoke
result = chain.invoke({
    "sentence": sentence_with_target,
    "senses": formatted_senses
})
```

### Notebooks
- `ChatGPT_sense.ipynb` - Primary WSD pipeline

---

## Google Gemini

### Model Used
- `gemini-2.0-flash-lite`

### Integration

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    temperature=0,
    google_api_key=GOOGLE_GENAI_API_KEY
)
```

### Rate Limiting

Gemini requires rate limiting between requests:

```python
import time

RATE_LIMIT_DELAY = 2  # seconds between requests

# In processing loop
time.sleep(RATE_LIMIT_DELAY)
result = chain.invoke(inputs)
```

### Notebook
- `GEMINI_sense.ipynb`

---

## Llama (Local via Ollama)

> **Note:** Llama 3.3 was not included in the paper's evaluation. Local
> inference was too slow on the available hardware to complete full-scale
> annotation within a practical time frame. A 10-sample test confirmed the
> pipeline works correctly; the code is included here for completeness and
> reproducibility.

### Model Used
- `llama3.3`

### Integration

```python
from langchain_community.chat_models import ChatOllama

llm = ChatOllama(
    model="llama3.3",
    temperature=0.0
)
```

### Special Prompt Format

Llama uses a special prompt format with specific tokens:

```python
# Target word highlighting for Llama
target_highlighted = f"**{target_word}**"  # Uses markdown bold

# Llama-specific tokens in prompt
LLAMA_SYSTEM_PREFIX = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>"
LLAMA_USER_PREFIX = "<|start_header_id|>user<|end_header_id|>"
```

### Requirements
- Ollama must be installed and running locally
- Model must be pulled: `ollama pull llama3.3`

### Notebook
- `Llama_sense.ipynb`

---

## Simple WSD (Sentence Transformers)

### Model Used
- `all-MiniLM-L6-v2` from sentence-transformers

### Integration

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Encode sentence and glosses
sentence_embedding = model.encode(sentence)
gloss_embeddings = model.encode(glosses)

# Compute cosine similarity
from sklearn.metrics.pairwise import cosine_similarity
similarities = cosine_similarity([sentence_embedding], gloss_embeddings)
```

### How It Works

1. Encodes the sentence containing the target word
2. Encodes all candidate sense definitions (glosses)
3. Computes cosine similarity between sentence and each gloss
4. Selects the sense with highest similarity score

### Files
- `simple_wsd.py` - Implementation
- `SimpleWSD_sense.ipynb` - Notebook interface

### Advantages
- No API costs
- Fast local execution
- Good baseline for comparison

---

## Configuration

### Environment Variables

```python
# config.py
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY", "")
```

### Sense Annotation Fields

```python
# Field names in output TSV files
SENSE_ID_FIELD = "KBid"           # Selected sense ID
SENSE_COUNT_FIELD = "NumberOfSenses"  # Number of candidate senses
SENSE_LIST_FIELD = "Possible"     # All candidate sense IDs
SENSE_AINOTES_FIELD = "Explanation"   # Model's explanation
SENSE_ORIGIN = "Origine"          # Model identifier tag
```

### Model Parameters

| Model | Temperature | Notes |
|-------|-------------|-------|
| ChatGPT (gpt-5) | Default | Primary WSD |
| Gemini | 0 | 2s rate limit delay |
| Llama | 0.0 | Special prompt format |

---

## Shared Pipeline Architecture

All LLM pipelines use the `process_senses.py` module with a shared architecture.

### Core Function: `annotate_with_llm`

```python
def annotate_with_llm(
    df: pd.DataFrame,
    llm,
    model_name: str,
    delay: float = 0
) -> pd.DataFrame:
    """
    Annotate tokens with sense information using an LLM.
    
    Args:
        df: DataFrame with tokens to annotate
        llm: LangChain LLM instance
        model_name: Name for origin tracking
        delay: Rate limiting delay in seconds
    
    Returns:
        Annotated DataFrame
    """
    chain = prompt | llm | JsonOutputParser()
    
    for idx, row in df.iterrows():
        # Build inputs
        inputs = build_prompt_inputs(row)
        
        # Rate limiting
        if delay > 0:
            time.sleep(delay)
        
        # Invoke with retry logic
        result = invoke_with_retry(chain, inputs, max_retries=3)
        
        # Validate and update
        df.at[idx, SENSE_ID_FIELD] = result["sense_id"]
        df.at[idx, SENSE_AINOTES_FIELD] = result["explanation"]
        df.at[idx, SENSE_ORIGIN] = model_name
    
    return df
```

### Retry Logic

```python
def invoke_with_retry(chain, inputs, max_retries=3):
    """Retry on hallucinated sense IDs."""
    valid_ids = inputs["valid_sense_ids"]
    
    for attempt in range(max_retries):
        result = chain.invoke(inputs)
        
        if result["sense_id"] in valid_ids or result["sense_id"] == "NEW_SENSE":
            return result
        
        # Log warning and retry
        print(f"Invalid sense_id: {result['sense_id']}, retrying...")
    
    # Fallback to first sense
    return {
        "sense_id": valid_ids[0],
        "explanation": "Fallback - LLM returned invalid sense"
    }
```

### MWE (Multi-Word Expression) Handling

```python
def handle_mwe(tokens: List[dict], llm) -> dict:
    """
    Handle multi-word expressions as a single unit.
    
    MWEs are identified by MWE_ID field and processed together.
    """
    combined_text = " ".join(t["form"] for t in tokens)
    # Process as single unit
    return annotate_single(combined_text, tokens[0]["senses"], llm)
```

---

## Output Traceability

### Origin Field Values

Each annotation includes an `Origine` field tracking how it was determined:

| Value | Meaning |
|-------|---------|
| `ChatGPT` | Annotated by ChatGPT (legacy) |
| `gpt-5` | Annotated by GPT-5 model |
| `Gemini_gemini-2.0-flash-lite` | Annotated by Gemini |
| `Llama` | Annotated by Llama 3.3 |
| `simple_wsd` | Annotated by Simple WSD |
| `FIRST` | Fallback - first sense selected |
| `None` | No sense available |
| `AI-GENERATED` | New sense generated by AI |
| `RAG-OLD-REPO` | Selected from existing repository via RAG |
| `AI-NEW-REPO` | New sense added to repository |

### Output Files

Outputs are organised into two paper-aligned phases:

```
output/
├── Phase1/           # Phase 1 exports (inputs + intermediate/test TSVs)
│   ├── LexiSense_Inception_*_gemini_Iround.tsv
│   ├── LexiSense_Inception_*_gpt-3.5_Iround_test.tsv
│   ├── LexiSense_Inception_*_gpt-4.1_Iround.tsv
│   ├── LexiSense_Inception_*_simple_wsd_Iround.tsv
│   └── LexiSense_Inception_*_simple_wsd_tesla_Iround.tsv
└── Phase2/           # Phase 2 model outputs (paper results)
    └── LexiSense_Inception_*_*.tsv
```

---

## Prompt Templates

All LLM pipelines use Serbian-language prompts. Example system message:

```python
SYSTEM_PROMPT = """
Vi ste ekspert za leksiku i semantiku. Na osnovu konteksta rečenice i liste 
validnih značenja ciljne reči, vaš zadatak je da identifikujete ono značenje 
koje se najpreciznije koristi u datom kontekstu.

Odgovor mora biti u strogo definisanom JSON formatu:
{
  "sense_id": "<jedan od ponuđenih ID-jeva ili 'NEW_SENSE'>",
  "explanation": "<kratko i jasno obrazloženje...>"
}
"""
```

### User Prompt Structure

```python
USER_PROMPT_TEMPLATE = """
Rečenica: {sentence}

Ciljna reč: {target_word}

Ponuđena značenja:
{senses}

Koji ID značenja najbolje odgovara upotrebi ciljne reči u datoj rečenici?
"""
```

### Target Word Highlighting

| Model | Format | Example |
|-------|--------|---------|
| ChatGPT/Gemini | HTML bold | `<b>реч</b>` |
| Llama | Markdown bold | `**реч**` |

---

## Dependencies

From `requirements.txt`:

```
langchain>=0.0.235
langchain-openai>=0.0.2
langchain-google-genai>=0.0.5
langchain-community>=0.0.2
langgraph>=0.1.0
openai>=1.5.0
google-genai>=0.2.0
ollama>=0.1.0
sentence-transformers==3.0.1
transformers>=4.40.0
torch>=2.7.0
```

---

## Quick Start Examples

### Using ChatGPT

```python
from langchain_openai import ChatOpenAI
from process_senses import annotate_with_llm
import pandas as pd

# Load data
df = pd.read_csv("Data/sr-elexis-WSD_0001_0500.tsv", sep="\t")

# Initialize model
llm = ChatOpenAI(model="gpt-5", api_key=OPENAI_API_KEY)

# Annotate
result_df = annotate_with_llm(df, llm, model_name="gpt-5")

# Save
result_df.to_csv("output/annotated.tsv", sep="\t", index=False)
```

### Using Gemini

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    temperature=0,
    google_api_key=GOOGLE_GENAI_API_KEY
)

result_df = annotate_with_llm(df, llm, model_name="Gemini", delay=2)
```

### Using Local Llama

```python
from langchain_community.chat_models import ChatOllama

llm = ChatOllama(model="llama3.3", temperature=0.0)

result_df = annotate_with_llm(df, llm, model_name="Llama")
```

### Using Simple WSD (No API)

```python
from simple_wsd import SimpleWSD

wsd = SimpleWSD(model_name='all-MiniLM-L6-v2')
result_df = wsd.annotate(df)
```
