"""Central paths and settings for the FAN backend."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("FAN_DATA_DIR", BASE_DIR / "data"))
CHROMA_DIR = Path(os.getenv("FAN_CHROMA_DIR", BASE_DIR / "chroma_db"))

MANUAL_PDF = DATA_DIR / "FAN_Manual.pdf"
COLLECTION_NAME = "fan_manual"

# Jai (growth) data
PERFORMANCE_FILE = DATA_DIR / "mock_performance.csv"
CAREER_PATH_FILE = DATA_DIR / "career_path.json"
NUDGE_FILE = DATA_DIR / "nudge_library.json"

# Kai (engagement) data
IDEAS_FILE = DATA_DIR / "ideas.csv"
CHALLENGES_FILE = DATA_DIR / "challenges.json"
KUDOS_FILE = DATA_DIR / "kudos.csv"

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = os.getenv("FAN_CHAT_MODEL", "gpt-4o-mini")

# Comma-separated list of allowed frontend origins
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
