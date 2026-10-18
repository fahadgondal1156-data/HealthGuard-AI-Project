from pathlib import Path
import argparse, numpy as np, pandas as pd
p=argparse.ArgumentParser(); p.add_argument("--patients",type=int,default=24); p.add_argument("--days",type=int,default=75); p.add_argument("--seed",type=int,default=7); a=p.parse_args()
rng=np.random.default_rng(a.seed); out=Path("data/demo"); out.mkdir(parents=True,exist_ok=True)
activity=[]; physiology=[]; sleep=[]; labels=[]; demographics=[]
start=pd.Timestamp("2019-04-01")
locs=["Hallway","Lounge","Fridge Door","Bedroom","Kitchen","Bathroom","Front Door"]
for i in range(a.patients):
    pid=f"demo-{i:03d}"; sex="Male" if i%2 else "Female"; age=["(70, 80]","(80, 90]","(90, 110]"][i%3]
    demographics.append([pid,sex,age]); base_hr=rng.normal(72,6); base_sys=rng.normal(132,12); base_dia=rng.normal(77,7); base_temp=rng.normal(36.6,.2); base_water=rng.normal(51,4); base_weight=rng.normal(72,10)
    event_days=set(rng.choice(np.arange(8,a.days),size=max(2,a.days//18),replace=False).tolist())
    for d in range(a.days):
        day=start+pd.Timedelta(days=d); pre_event=1 if (d+1 in event_days or d+2 in event_days) else 0
        activity_level=max(5,int(rng.normal(95-25*pre_event,18)))
        for _ in range(activity_level): activity.append([pid,rng.choice(locs),day+pd.Timedelta(seconds=int(rng.integers(0,86400)))])
        vals={
            "Heart rate":base_hr+7*pre_event+rng.normal(0,4),"Systolic blood pressure":base_sys+13*pre_event+rng.normal(0,8),
            "Diastolic blood pressure":base_dia+7*pre_event+rng.normal(0,5),"Body Temperature":base_temp+.45*pre_event+rng.normal(0,.15),
            "O/E - total body water":base_water-3.5*pre_event+rng.normal(0,1.8),"O/E - body weight":base_weight+rng.normal(0,.35),
            "Skin Temperature":base_temp-.3+rng.normal(0,.2),"O/E - muscle mass":rng.normal(28,4),}
        units={"Heart rate":"beats/min","Systolic blood pressure":"mm[Hg]","Diastolic blood pressure":"mm[Hg]","Body Temperature":"C","O/E - total body water":"%","O/E - body weight":"kg","Skin Temperature":"C","O/E - muscle mass":"kg"}
        for k,v in vals.items(): physiology.append([pid,day+pd.Timedelta(hours=8),k,v,units[k]])
        # 6 hours/minute-like synthetic sleep rows per day to keep demo lightweight.
        for m in range(0,360,5):
            state=rng.choice(["LIGHT","AWAKE","DEEP","REM"],p=[.48,.12+.08*pre_event,.20-.04*pre_event,.20-.04*pre_event])
            sleep.append([pid,day+pd.Timedelta(hours=23)+pd.Timedelta(minutes=m),state,base_hr-8+5*pre_event+rng.normal(0,3),16+1.5*pre_event+rng.normal(0,1),bool(rng.random()<.15)])
        if d in event_days:
            et=rng.choice(["Agitation","Blood pressure","Body temperature","Body water","Pulse","Weight"]); labels.append([pid,day+pd.Timedelta(hours=12),et])
pd.DataFrame(activity,columns=["patient_id","location_name","date"]).to_csv(out/"Activity.csv",index=False)
pd.DataFrame(physiology,columns=["patient_id","date","device_type","value","unit"]).to_csv(out/"Physiology.csv",index=False)
pd.DataFrame(sleep,columns=["patient_id","date","state","heart_rate","respiratory_rate","snoring"]).to_csv(out/"Sleep.csv",index=False)
pd.DataFrame(labels,columns=["patient_id","date","type"]).to_csv(out/"Labels.csv",index=False)
pd.DataFrame(demographics,columns=["patient_id","sex","age"]).to_csv(out/"Demographics.csv",index=False)
print(f"Synthetic research demo written to {out}. It is not clinical data.")
