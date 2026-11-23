"""Shared loading, feature engineering and output helpers."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, FIG, TAB = ROOT / "data", ROOT / "outputs" / "figures", ROOT / "outputs" / "tables"
RESULTS = ROOT / "outputs" / "results.json"
for d in (FIG, TAB):
    d.mkdir(parents=True, exist_ok=True)

# Observation window for the patient-level models:
# features use history up to CUTOFF, targets look at what happens afterwards.
CUTOFF = pd.Timestamp("2024-12-31")
RETURN_END = pd.Timestamp("2025-06-30")   # revisit / churn label window (6 months)
PLV_END = pd.Timestamp("2025-12-31")      # patient lifetime value window (12 months)

plt.rcParams.update({"figure.dpi": 150, "savefig.bbox": "tight", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False})


def load():
    patients = pd.read_csv(DATA / "patients.csv", parse_dates=["first_visit_date"])
    visits = pd.read_csv(DATA / "visits.csv", parse_dates=["visit_date"])
    survey = pd.read_csv(DATA / "survey.csv")
    return patients, visits, survey


def patient_features(patients, visits):
    """One row per patient seen on or before CUTOFF, with RFM-style history features
    and the two targets: plv_2025 (spend in 2025) and returned (visit in H1 2025)."""
    hist = visits[visits.visit_date <= CUTOFF]
    g = hist.groupby("patient_id")
    feats = pd.DataFrame({
        "frequency": g.size(),
        "monetary": g.out_of_pocket_kvnd.sum(),
        "avg_spend": g.out_of_pocket_kvnd.mean(),
        "avg_wait": g.wait_minutes.mean(),
        "recency_days": (CUTOFF - g.visit_date.max()).dt.days,
        "tenure_days": (CUTOFF - g.visit_date.min()).dt.days,
        "n_departments": g.department.nunique(),
    })
    fut = visits[(visits.visit_date > CUTOFF) & (visits.visit_date <= PLV_END)]
    feats["plv_2025"] = fut.groupby("patient_id").out_of_pocket_kvnd.sum()
    feats["plv_2025"] = feats["plv_2025"].fillna(0)
    ret = visits[(visits.visit_date > CUTOFF) & (visits.visit_date <= RETURN_END)].patient_id.unique()
    feats["returned"] = feats.index.isin(ret).astype(int)
    df = patients.set_index("patient_id").join(feats, how="inner")
    return df


def save_fig(fig, name):
    fig.savefig(FIG / f"{name}.png")
    plt.close(fig)


def save_table(df, name, index=True):
    df.to_csv(TAB / f"{name}.csv", index=index)


def update_results(section, payload):
    res = json.loads(RESULTS.read_text()) if RESULTS.exists() else {}
    res[section] = payload
    RESULTS.write_text(json.dumps(res, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
