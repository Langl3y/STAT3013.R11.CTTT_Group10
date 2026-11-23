# ClinicAnalytics — Statistics and ML for Patient Value, Satisfaction and Retention in a Private Clinic

STAT3013 course project (2026). Class `R11.CTTT`, Group `Group10` (group number to be confirmed).

> **Data notice.** All data in this repository is **simulated**, as the course brief allows. Nothing here describes real patients.
> Because we wrote the data-generating process ourselves (`src/simulate.py`), the true effects are known,
> so we can check whether each method recovers them.

## Research questions

| Stage | Method | Question |
|---|---|---|
| 1 | Descriptive statistics | What do patients, visits, costs and waiting times look like? |
| 2 | Inferential (t-test, chi-square, ANOVA) | Do care-programme members spend more? Is returning related to insurance, channel or chronic status? |
| 3 | Regression: two-part model | How much will each patient spend next year (Patient Lifetime Value, PLV)? |
| 4 | SEM | Which service factors drive satisfaction, and does satisfaction drive loyalty? |
| 5 | ARIMA forecasting | How many visits should the clinic plan for next quarter? |
| 6 | ML / DL (LogReg, RF, GBM, MLP) | Which patients are likely to churn (not return within 6 months)? |

## Headline results

- **PLV:** the two-part model (logit × log-OLS with Duan smearing) reaches test R² = 0.40, against 0.00 for a mean baseline. The top predicted decile spends about 3.9M VND on average; the bottom decile spends ≈0.
- **SEM:** satisfaction is driven by doctor communication (β = 0.37), service quality (0.35), access (0.27) and price fairness (0.22). Satisfaction → loyalty β = 0.69. Each 1 SD of stated loyalty raises the odds of an actual return visit by 1.6×.
- **Forecasting:** ARIMA(2,1,1) with Fourier seasonality has a 13-week test MAPE of 5.8%; Holt-Winters gets 4.5% and seasonal naive 19.4%.
- **Churn:** Logistic Regression is the best model (CV AUC 0.887, sensitivity 0.78, specificity 0.84), ahead of the MLP neural network. Recency of the last visit is by far the strongest signal.

## Repository layout

```
src/
  simulate.py        data generator (documented assumptions, seed 3013)
  common.py          loading, feature engineering, output helpers
  s1_descriptive.py  ... s6_ml.py   one script per analysis stage
  run_all.py         reproduces everything
data/                patients.csv, visits.csv, survey.csv (generated)
outputs/figures/     all figures used in the report, paper and slides
outputs/tables/      all result tables (CSV)
outputs/results.json every number quoted in the report
```

## Setup and execution

Requirements: Python 3.10+ (tested on 3.12.6, macOS). No GPU needed. A full run takes about 15 seconds.

```bash
git clone https://github.com/<your-user>/STAT3013.R11.CTTT_Group10.git
cd STAT3013.R11.CTTT_Group10
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd src && python run_all.py
```

To run a single stage, run e.g. `python s4_sem.py` from inside `src/`.

## Links

- Dataset: `data/` in this repository (also archived at: <ADD CLOUD LINK>)
- Demo video (15 min): <ADD CLOUD LINK>
- Full report and IEEE paper: submitted on the course system

## AI usage

AI assistance (Claude) was used for parts of the code and draft text. Every result was re-run and checked, and the text was revised by the author. See the AI Usage Disclosure Statement for details.

## License

MIT, see [LICENSE](LICENSE).
