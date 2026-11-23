"""
Simulate a private outpatient clinic (Jan 2023 - Dec 2025).

Produces three tables in data/:
  patients.csv  - one row per patient (demographics, insurance, care programme)
  visits.csv    - one row per visit (date, department, cost, waiting time)
  survey.csv    - Likert 1-5 satisfaction survey answered by a subset of patients

Why simulate?  Real patient records are protected, and the course allows simulated
data. Because we write the generating rules ourselves, we also know the "true"
effects and can check whether each statistical method recovers them
(see TRUE_EFFECTS below - quoted in the report).
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 3013
N_PATIENTS = 5000
START, END = pd.Timestamp("2023-01-01"), pd.Timestamp("2025-12-31")
DATA_DIR = Path(__file__).resolve().parents[1] / "data"

DEPARTMENTS = ["General Medicine", "Cardiology", "Endocrinology", "Dermatology", "Dental"]
DEPT_COST = {  # median price of one visit, thousand VND
    "General Medicine": 350, "Cardiology": 900, "Endocrinology": 700,
    "Dermatology": 500, "Dental": 800,
}
DEPT_WAIT = {  # extra waiting minutes on top of the clinic baseline
    "General Medicine": 10, "Cardiology": 5, "Endocrinology": 0,
    "Dermatology": -5, "Dental": -8,
}
# Lunar New Year (Tet) - the clinic is almost empty for ~a week
TET = [pd.Timestamp(d) for d in ("2023-01-22", "2024-02-10", "2025-01-29")]
WEEKDAY_FACTOR = np.array([1.15, 1.05, 1.0, 1.0, 1.0, 0.85, 0.45])  # Mon..Sun

# Structural relations used to generate the survey (standardised latent scale)
TRUE_EFFECTS = {
    "SAT <- SQ (service quality)": 0.30,
    "SAT <- DC (doctor communication)": 0.35,
    "SAT <- AC (access & convenience)": 0.20,
    "SAT <- PF (price fairness)": 0.20,
    "LOY <- SAT": 0.65,
    "log visit-rate <- chronic": 0.60,
    "log visit-rate <- care programme": 0.30,
    "out-of-pocket multiplier, insured": 0.60,
    "out-of-pocket multiplier, programme member": 0.90,
}


def day_factor(dates: pd.DatetimeIndex) -> np.ndarray:
    """Relative busyness of each calendar day: flu season, weekday, Tet."""
    doy = dates.day_of_year.to_numpy()
    season = 1 + 0.25 * np.cos(2 * np.pi * (doy - 20) / 365.25)  # peak late January
    weekday = WEEKDAY_FACTOR[dates.day_of_week.to_numpy()]
    tet = np.ones(len(dates))
    for t in TET:
        tet[np.abs((dates - t).days.to_numpy()) <= 4] = 0.25
    return season * weekday * tet


MAX_FACTOR = 1.25 * WEEKDAY_FACTOR.max()


def simulate_patients(rng):
    n = N_PATIENTS
    age = np.clip(rng.normal(42, 15, n), 18, 85).round().astype(int)
    gender = rng.choice(["Female", "Male"], n, p=[0.55, 0.45])
    insured = rng.random(n) < 0.65
    chronic = rng.random(n) < 1 / (1 + np.exp(-(-3.0 + 0.05 * age)))
    programme = rng.random(n) < np.where(chronic, 0.45, 0.22)
    channel = rng.choice(["Walk-in", "Referral", "Online"], n, p=[0.45, 0.30, 0.25])

    # Main department: chronic patients go to Cardiology / Endocrinology more often
    p_chronic = [0.25, 0.35, 0.30, 0.05, 0.05]
    p_other = [0.40, 0.08, 0.07, 0.22, 0.23]
    dept = np.array([rng.choice(DEPARTMENTS, p=p_chronic if c else p_other) for c in chronic])

    # First-visit date: the clinic grows ~60% over three years, plus seasonality
    days = pd.date_range(START, END, freq="D")
    trend = 1 + 0.6 * np.arange(len(days)) / len(days)
    w = trend * day_factor(days)
    first_visit = days[rng.choice(len(days), n, p=w / w.sum())]

    # Latent patient experience (standard-normal scale)
    typical_wait = np.clip(25 + np.vectorize(DEPT_WAIT.get)(dept) + rng.normal(0, 8, n), 5, None)
    sq = rng.normal(0, 1, n)                                  # service quality
    dc = 0.4 * sq + np.sqrt(1 - 0.4**2) * rng.normal(0, 1, n)  # doctor communication
    ac = -0.6 * (typical_wait - typical_wait.mean()) / typical_wait.std() + rng.normal(0, 0.8, n)
    pf = 0.5 * insured + 0.3 * programme - 0.4 + rng.normal(0, 0.9, n)
    sat = 0.30 * sq + 0.35 * dc + 0.20 * ac + 0.20 * pf + rng.normal(0, 0.6, n)
    loy = 0.65 * sat + rng.normal(0, 0.6, n)

    patients = pd.DataFrame({
        "patient_id": [f"P{i:05d}" for i in range(1, n + 1)],
        "age": age, "gender": gender,
        "insurance": np.where(insured, "Yes", "No"),
        "chronic_condition": np.where(chronic, "Yes", "No"),
        "care_programme": np.where(programme, "Yes", "No"),
        "acquisition_channel": channel,
        "main_department": dept,
        "first_visit_date": first_visit,
    })
    latent = pd.DataFrame({"sq": sq, "dc": dc, "ac": ac, "pf": pf, "sat": sat, "loy": loy,
                           "typical_wait": typical_wait})
    return patients, latent


def simulate_visits(rng, patients, latent):
    rows = []
    for i, p in patients.iterrows():
        chronic = p.chronic_condition == "Yes"
        prog = p.care_programme == "Yes"
        insured = p.insurance == "Yes"
        # Visits per month while the patient is still "active"
        rate = 0.35 * np.exp(0.6 * chronic + 0.3 * prog + 0.008 * (p.age - 42) + rng.normal(0, 0.3))
        # How long the patient stays with the clinic (months) - loyal patients stay longer
        mean_life = np.exp(2.4 + 0.5 * latent.loy[i] + 0.35 * prog + 0.3 * chronic)
        last_active = min(p.first_visit_date + pd.Timedelta(days=30.4 * rng.exponential(mean_life)), END)

        dates = [p.first_visit_date]
        span = (last_active - p.first_visit_date).days
        if span > 0:  # thinned Poisson process -> seasonality carries into revisits
            k = rng.poisson(rate / 30.4 * MAX_FACTOR * span)
            cand = p.first_visit_date + pd.to_timedelta(np.sort(rng.integers(1, span + 1, k)), unit="D")
            keep = rng.random(k) < day_factor(pd.DatetimeIndex(cand)) / MAX_FACTOR
            dates += list(cand[keep])

        for d in dates:
            dept = p.main_department if rng.random() < 0.75 else rng.choice(DEPARTMENTS)
            cost = DEPT_COST[dept] * rng.lognormal(0, 0.45)
            oop = cost * (0.60 if insured else 1.0) * (0.90 if prog else 1.0)
            flu = 1 + 0.2 * np.cos(2 * np.pi * (d.day_of_year - 20) / 365.25)
            monday = 1.25 if d.day_of_week == 0 else 1.0
            wait = rng.gamma(4, latent.typical_wait[i] * flu * monday / 4)
            rows.append((p.patient_id, d, dept, round(cost), round(oop), round(wait, 1)))

    visits = pd.DataFrame(rows, columns=["patient_id", "visit_date", "department",
                                         "total_cost_kvnd", "out_of_pocket_kvnd", "wait_minutes"])
    visits = visits.drop_duplicates(["patient_id", "visit_date"]).sort_values(["visit_date", "patient_id"])
    visits.insert(0, "visit_id", [f"V{i:06d}" for i in range(1, len(visits) + 1)])
    return visits


def simulate_survey(rng, patients, latent, n_resp=1500):
    """Likert items: item = 3 + loading * latent + noise, rounded and clipped to 1..5."""
    eligible = np.flatnonzero(patients.first_visit_date < pd.Timestamp("2025-10-01"))
    idx = rng.choice(eligible, n_resp, replace=False)
    constructs = {  # construct -> (latent column, item loadings)
        "SQ": ("sq", [0.80, 0.75, 0.70, 0.78]),
        "DC": ("dc", [0.82, 0.78, 0.74, 0.70]),
        "AC": ("ac", [0.76, 0.72, 0.68]),
        "PF": ("pf", [0.80, 0.74, 0.70]),
        "SAT": ("sat", [0.85, 0.80, 0.78]),
        "LOY": ("loy", [0.82, 0.78, 0.72]),
    }
    out = {"patient_id": patients.patient_id.to_numpy()[idx]}
    for name, (col, loads) in constructs.items():
        z = latent[col].to_numpy()[idx]
        z = (z - z.mean()) / z.std()
        for j, lam in enumerate(loads, 1):
            noise = rng.normal(0, np.sqrt(1 - lam**2), len(idx))
            out[f"{name}{j}"] = np.clip(np.round(3 + 1.1 * (lam * z + noise)), 1, 5).astype(int)
    return pd.DataFrame(out)


def main():
    rng = np.random.default_rng(SEED)
    DATA_DIR.mkdir(exist_ok=True)
    patients, latent = simulate_patients(rng)
    visits = simulate_visits(rng, patients, latent)
    survey = simulate_survey(rng, patients, latent)
    patients.to_csv(DATA_DIR / "patients.csv", index=False)
    visits.to_csv(DATA_DIR / "visits.csv", index=False)
    survey.to_csv(DATA_DIR / "survey.csv", index=False)
    print(f"patients={len(patients):,}  visits={len(visits):,}  survey={len(survey):,}")


if __name__ == "__main__":
    main()
