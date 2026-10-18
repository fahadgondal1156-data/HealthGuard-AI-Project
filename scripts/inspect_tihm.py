from pathlib import Path as _Path
import sys
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
import argparse
from src.healthguard.data import discover_tables, load_tihm
p=argparse.ArgumentParser(); p.add_argument("--input",required=True); a=p.parse_args()
paths=discover_tables(a.input); print("Detected tables:")
for k,v in paths.items(): print(f"  {k:12s} {v}")
t=load_tihm(a.input)
for k,df in t.items():
    print(f"\n[{k}] rows={len(df):,} patients={df.patient_id.nunique()}")
    print("columns:",", ".join(df.columns))
    if "date" in df: print("date:",df.date.min(),"->",df.date.max())
