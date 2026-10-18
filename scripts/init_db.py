from pathlib import Path as _Path
import sys
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from src.healthguard.db import init_db
init_db(); print("Database tables initialized.")
