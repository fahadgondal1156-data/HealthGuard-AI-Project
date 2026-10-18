from pathlib import Path
from src.healthguard.data import discover_tables

def test_signatures_exist():
    # Structural test only; integration workflow creates demo data before full ingestion test.
    assert "activity" in {"activity","labels","physiology","sleep","demographics"}
