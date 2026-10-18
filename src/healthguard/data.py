from __future__ import annotations
from pathlib import Path
import re
import numpy as np
import pandas as pd

REQUIRED_SIGNATURES = {
    "activity": {"patient_id", "location_name", "date"},
    "labels": {"patient_id", "date", "type"},
    "physiology": {"patient_id", "date", "device_type", "value"},
    "sleep": {"patient_id", "date", "state", "heart_rate", "respiratory_rate", "snoring"},
    "demographics": {"patient_id", "sex", "age"},
}

def _norm_columns(df: pd.DataFrame) -> pd.DataFrame:
    out=df.copy()
    out.columns=[re.sub(r"[^a-z0-9]+","_",str(c).strip().lower()).strip("_") for c in out.columns]
    return out

def discover_tables(folder: str | Path) -> dict[str, Path]:
    folder=Path(folder)
    found={}
    for path in folder.rglob("*.csv"):
        try:
            sample=pd.read_csv(path,nrows=3)
            cols=set(_norm_columns(sample).columns)
        except Exception:
            continue
        for name,sig in REQUIRED_SIGNATURES.items():
            if sig.issubset(cols) and name not in found:
                found[name]=path
    missing=[k for k in REQUIRED_SIGNATURES if k not in found]
    if missing:
        raise FileNotFoundError(f"Could not identify TIHM tables: {missing}. CSVs inspected under {folder}")
    return found

def load_tihm(folder: str | Path) -> dict[str,pd.DataFrame]:
    tables=discover_tables(folder)
    out={}
    for name,path in tables.items():
        df=_norm_columns(pd.read_csv(path))
        if "date" in df.columns:
            df["date"]=pd.to_datetime(df["date"],errors="coerce")
        df["patient_id"]=df["patient_id"].astype(str)
        out[name]=df
    return out

def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+","_",str(value).lower()).strip("_")

def aggregate_physiology(df: pd.DataFrame) -> pd.DataFrame:
    x=df.dropna(subset=["patient_id","date","device_type","value"]).copy()
    x["day"]=x["date"].dt.floor("D")
    x["feature"]="phys_"+x["device_type"].map(_slug)
    x["value"]=pd.to_numeric(x["value"],errors="coerce")
    p=x.pivot_table(index=["patient_id","day"],columns="feature",values="value",aggfunc="median")
    return p.reset_index()

def aggregate_activity(df: pd.DataFrame) -> pd.DataFrame:
    x=df.dropna(subset=["patient_id","date","location_name"]).copy()
    x["day"]=x["date"].dt.floor("D")
    x["location"]="activity_"+x["location_name"].map(_slug)+"_count"
    counts=x.groupby(["patient_id","day","location"],observed=True).size().rename("n").reset_index()
    wide=counts.pivot_table(index=["patient_id","day"],columns="location",values="n",fill_value=0,aggfunc="sum").reset_index()
    loc_cols=[c for c in wide.columns if str(c).startswith("activity_")]
    wide["activity_total_count"]=wide[loc_cols].sum(axis=1)
    wide["activity_active_locations"]=(wide[loc_cols]>0).sum(axis=1)
    return wide

def aggregate_sleep(df: pd.DataFrame) -> pd.DataFrame:
    x=df.dropna(subset=["patient_id","date"]).copy()
    x["day"]=x["date"].dt.floor("D")
    x["heart_rate"]=pd.to_numeric(x["heart_rate"],errors="coerce")
    x["respiratory_rate"]=pd.to_numeric(x["respiratory_rate"],errors="coerce")
    if x["snoring"].dtype != bool:
        x["snoring"]=x["snoring"].astype(str).str.lower().isin(["1","true","yes"])
    base=x.groupby(["patient_id","day"],observed=True).agg(
        sleep_observed_minutes=("state","size"),
        sleep_hr_mean=("heart_rate","mean"), sleep_hr_std=("heart_rate","std"),
        sleep_hr_min=("heart_rate","min"), sleep_hr_max=("heart_rate","max"),
        sleep_rr_mean=("respiratory_rate","mean"), sleep_rr_std=("respiratory_rate","std"),
        sleep_snore_rate=("snoring","mean"),
    ).reset_index()
    states=(x.assign(state_name="sleep_state_"+x["state"].astype(str).str.lower())
              .groupby(["patient_id","day","state_name"],observed=True).size().rename("n").reset_index())
    st=states.pivot_table(index=["patient_id","day"],columns="state_name",values="n",fill_value=0,aggfunc="sum").reset_index()
    out=base.merge(st,on=["patient_id","day"],how="left")
    state_cols=[c for c in out.columns if str(c).startswith("sleep_state_")]
    for c in state_cols:
        out[c+"_ratio"]=out[c]/out["sleep_observed_minutes"].replace(0,np.nan)
    out=out.drop(columns=state_cols)
    return out

def build_daily_frame(tables: dict[str,pd.DataFrame]) -> pd.DataFrame:
    parts=[aggregate_physiology(tables["physiology"]),aggregate_activity(tables["activity"]),aggregate_sleep(tables["sleep"])]
    # Full patient-day index across all modalities.
    idx=pd.concat([p[["patient_id","day"]] for p in parts]).drop_duplicates()
    out=idx
    for p in parts:
        out=out.merge(p,on=["patient_id","day"],how="left")
    demo=tables["demographics"].copy()
    demo=demo.rename(columns={"age":"age_group"})
    keep=[c for c in ["patient_id","sex","age_group"] if c in demo.columns]
    out=out.merge(demo[keep].drop_duplicates("patient_id"),on="patient_id",how="left")
    return out.sort_values(["patient_id","day"]).reset_index(drop=True)

def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    out=df.copy().sort_values(["patient_id","day"])
    base_cols=[c for c in out.columns if c.startswith("phys_") or c in ["activity_total_count","sleep_hr_mean","sleep_rr_mean","sleep_observed_minutes"]]
    for c in base_cols:
        s=out.groupby("patient_id",observed=True)[c]
        out[c+"_lag1"]=s.shift(1)
        hist=s.shift(1)
        out[c+"_hist7_mean"]=hist.groupby(out["patient_id"]).transform(lambda z:z.rolling(7,min_periods=2).mean())
        out[c+"_hist7_std"]=hist.groupby(out["patient_id"]).transform(lambda z:z.rolling(7,min_periods=2).std())
        denom=out[c+"_hist7_std"].replace(0,np.nan)
        out[c+"_personal_z"]=(out[c]-out[c+"_hist7_mean"])/denom
    return out

def add_future_labels(df: pd.DataFrame, labels: pd.DataFrame, hours: int) -> pd.DataFrame:
    out=df.copy()
    target=f"target_{hours}h"
    out[target]=0
    lab=labels.dropna(subset=["patient_id","date"]).copy()
    lab["event_day"]=lab["date"].dt.floor("D")
    lab["event_type"]=lab["type"].astype(str)
    events={pid:g.sort_values("event_day") for pid,g in lab.groupby("patient_id",observed=True)}
    horizon=pd.Timedelta(hours=hours)
    event_types=[]
    vals=[]
    for row in out[["patient_id","day"]].itertuples(index=False):
        g=events.get(row.patient_id)
        if g is None:
            vals.append(0); event_types.append(""); continue
        mask=(g["event_day"]>row.day) & (g["event_day"]<=row.day+horizon)
        matched=g.loc[mask,"event_type"]
        vals.append(int(len(matched)>0))
        event_types.append("|".join(sorted(set(matched))))
    out[target]=vals
    out[f"future_event_types_{hours}h"]=event_types
    return out

def build_research_dataset(folder: str|Path, hours: int) -> pd.DataFrame:
    t=load_tihm(folder)
    daily=build_daily_frame(t)
    daily=add_temporal_features(daily)
    daily=add_future_labels(daily,t["labels"],hours)
    return daily
