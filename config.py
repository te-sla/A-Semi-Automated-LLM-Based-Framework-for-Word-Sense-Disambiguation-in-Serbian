# config.py
import os
from pathlib import Path
from typing import List, Tuple

try:
	from dotenv import load_dotenv
except ImportError:
	def load_dotenv(*_args, **_kwargs):
		return False

# =============================
# 1. Environment settings
# =============================
# Load variables from your .env (must be at project root or specify path)
load_dotenv()

# Environment-backed settings (kept out of VCS via .env)
OPENAI_API_KEY       = os.getenv("OPENAI_API_KEY", "")
GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY", "")

# =============================
# 2. Directories and file paths
# =============================
BASE_DIR    = Path(__file__).parent
# Note: Data directory is capitalized 'Data' in repository
DATA_DIR    = BASE_DIR / "Data"
# MODELS_DIR = BASE_DIR / "models"
OUTPUT_DIR  = BASE_DIR / "output"
STATS_DIR   = BASE_DIR / "stats"

# Data files
# Second round uses pre-chunked TSVs grouped by 500 sentences: sr-elexis-WSD_0001_0500.tsv, ...
TEST_TSV        = DATA_DIR / "test_sr_lexix.tsv"
SENSE_REPO      = DATA_DIR / "Elexis-WSD-Repo-sr-v2.xlsx"
SENSE_REPO_OLD  = DATA_DIR / "Elexis-WSD-Repo-sr-v1.xlsx"  # Round 1 sense repository

# Human-readable list of pre-chunked TSVs as (begin, end, filename)
ANNOTATION_CHUNKS: List[Tuple[int, int, str]] = [
	(1, 500,   "sr-elexis-WSD_0001_0500.tsv"),
	(501, 1000, "sr-elexis-WSD_0501_1000.tsv"),
	(1001, 1500, "sr-elexis-WSD_1001_1500.tsv"),
	(1501, 2000, "sr-elexis-WSD_1501_2000.tsv"),
	(2001, 2024, "sr-elexis-WSD_2001_2024.tsv"),
]

# Backwards compatibility: default to first chunk path
ANNOTATIONS_TSV = (DATA_DIR / ANNOTATION_CHUNKS[0][2]) if ANNOTATION_CHUNKS else (DATA_DIR / "sr-elexis-WSD_0001_0500.tsv")

# # Model checkpoints
# WSD_MODEL_CHECKPOINT = MODELS_DIR / "wsd_model"
# EMBED_MODEL_NAME     = "sentence-transformers/all-MiniLM-L6-v2"

# # Utility
# LOG_FILE = BASE_DIR / "logs" / "pipeline.log"

# =============================
# 3. Lexis file fields
# =============================
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.lexmorph.type.pos.POS|PosValue|coarseValue
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity|identifier|value
#T_SP=de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Lemma|value 
# Note: because there are two fields with the same name 'value', the latter gets added '_4' (its index) to avoid being overwritten
L_POS    = "PosValue"
L_UPOS   = "coarseValue" 
L_LEMMA  = "value_4"
L_NAMED_ENT = "value"
L_NE_ID  = "identifier"

# =============================
# 4. Sense‐repository and MWE fields
# =============================
# Sense‐repository file fields
S_LEMMA      = "lemma"
S_DEFINITION = "definition"
S_LITERALS   = "literals"
S_POS        = "pos"
S_UPOS       = "upos"
S_TYPE       = "Type"
S_DOMAIN     = "domain"
S_ID         = "senseID"

# Multi-Word Expression (MWE) support
#T_SP=webanno.custom.MWE|MWEid|MWElemma|MWEtype
L_MWE_ID    = "MWEid"
L_MWE_LEMMA = "MWElemma"
L_MWE_TYPE  = "MWEtype"

# =============================
# 5. Model settings
# =============================
SWD_MODEL = "all-MiniLM-L6-v2"  # Sentence-transformer model for SimpleWSD
TESLA_SWD_MODEL = "te-sla/TeslaXLM"  # Tesla sentence-transformer model
MLING_SWD_MODEL = "intfloat/multilingual-e5-large"  # Multilingual E5 large embedding model

SIMPLE_WSD_MODEL_PRESETS = {
	"simple": {
		"model_name": SWD_MODEL,
		"origin": "simple_wsd",
		"text_prefix": "",
		"normalize_embeddings": False,
	},
	"tesla": {
		"model_name": TESLA_SWD_MODEL,
		"origin": "tesla_wsd",
		"text_prefix": "",
		"normalize_embeddings": False,
	},
	"mling": {
		"model_name": MLING_SWD_MODEL,
		"origin": "mling",
		"text_prefix": "query: ",
		"normalize_embeddings": True,
	},
}

# =============================
# 6. Filters
# =============================
EVENT_FILTER  = ["ROLE", "EVENT", "DEMO", "PRODUCT", "WORK"]
CONTENT_WORDS = ["NOUN", "VERB", "ADJ", "ADV"]

# =============================
# 7. WebAnno custom field names (UI)
# =============================
#T_SP=webanno.custom.WSD|Comment|Explanation|KBid|NumberOfSenses|Origine|Possible

# New in second round: an additional free-text annotator comment field precedes Explanation.
SENSE_COMMENT_FIELD = "Comment"

SENSE_ID_FIELD     = "KBid"
SENSE_COUNT_FIELD  = "NumberOfSenses"
SENSE_LIST_FIELD   = "Possible"
SENSE_AINOTES_FIELD = "Explanation"
SENSE_ORIGIN       = "Origine"
