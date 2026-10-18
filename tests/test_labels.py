import pandas as pd
from src.healthguard.data import add_future_labels

def test_future_label_excludes_current_day():
    d=pd.DataFrame({"patient_id":["p1","p1"],"day":pd.to_datetime(["2026-01-01","2026-01-02"])})
    l=pd.DataFrame({"patient_id":["p1","p1"],"date":pd.to_datetime(["2026-01-01 12:00","2026-01-02 12:00"]),"type":["Pulse","Pulse"]})
    o=add_future_labels(d,l,24)
    assert o.loc[0,"target_24h"]==1
    assert o.loc[1,"target_24h"]==0
