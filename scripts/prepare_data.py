from pathlib import Path as _Path
import sys
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
import argparse
from pathlib import Path
from src.healthguard.data import build_research_dataset
p=argparse.ArgumentParser(); p.add_argument("--input",required=True); p.add_argument("--horizons",nargs="+",type=int,default=[24,48]); a=p.parse_args()
out=Path("data/processed"); out.mkdir(parents=True,exist_ok=True)
for h in a.horizons:
    df=build_research_dataset(a.input,h)
    path=out/f"healthguard_{h}h.csv"; df.to_csv(path,index=False)
    t=f"target_{h}h"; print(f"{path}: rows={len(df):,}, patients={df.patient_id.nunique()}, positives={int(df[t].sum())} ({df[t].mean():.2%})")
