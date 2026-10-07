import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
CORS_ORIGINS = [s.strip() for s in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if s.strip()]
DEMO_ASSET_BASE_URL = os.getenv("DEMO_ASSET_BASE_URL", "http://localhost:3000").rstrip("/")
DATA_PATH = Path(__file__).resolve().parents[1] / "demo_data" / "photos.json"
HINT_MIN_RESULTS = 5
MIN_VALUE_COUNT = 1
MAX_ELIGIBLE_SHARE = .85
MIN_FACET_SCORE = .25
MAX_HINT_ROWS = 3
MAX_VALUES_PER_ROW = 4
DROP_ROW_MAX_RESULTS = 1
