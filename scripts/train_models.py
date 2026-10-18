from pathlib import Path as _Path
import sys
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
import argparse, json
import pandas as pd
from src.healthguard.modeling import train_all
p=argparse.ArgumentParser(); p.add_argument("--dataset",required=True); p.add_argument("--horizon",type=int,required=True); p.add_argument("--seed",type=int,default=42); a=p.parse_args()
df=pd.read_csv(a.dataset,parse_dates=["day"])
meta=train_all(df,a.horizon,f"models/{a.horizon}h",f"reports/{a.horizon}h",a.seed)
print(json.dumps(meta,indent=2))
