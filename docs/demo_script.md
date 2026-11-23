# 15-minute narrated demo: script and shot list

Record with QuickTime (File → New Screen Recording) or OBS, 1080p, with the microphone on.
Before recording, open: VS Code with the repo, a terminal in `src/`, the slide deck, and the report PDF.
Speak in your own words. The lines below are prompts, not text to read word for word.

| Time | On screen | What to say / do |
|---|---|---|
| 0:00–1:00 | Slide 1–2 | Introduce yourself (name, ID, class, group). State the three clinic questions: who is valuable, what keeps patients loyal, how much demand / who will leave. |
| 1:00–2:30 | Slide 3–4 | Why simulated data (confidential records, need survey + visits for the same people, known ground truth). Show the workflow and explain the 31-Dec-2024 cut-off (no leakage). |
| 2:30–4:00 | VS Code: `README.md`, folder tree | Walk through the repo: `src/simulate.py`, one script per stage, `outputs/`. Show `requirements.txt`. |
| 4:00–5:30 | VS Code: `src/simulate.py` | Scroll to `TRUE_EFFECTS` and to the `sat = 0.30*sq + ...` and `mean_life = ...` lines. Explain: the same hidden loyalty drives the survey AND how long a patient stays. |
| 5:30–6:30 | Terminal | **Live run:** `rm -rf ../outputs ../data && python run_all.py`. Point at the stage timings; the whole project rebuilds in ~15 s. Open `data/visits.csv` briefly. |
| 6:30–7:30 | `outputs/figures/f1, f2, f4` + `t3_hypothesis_tests.csv` | Descriptive: growth, seasonality, skew. Tests: 3 of 6 hypotheses supported; explain one null result (channel). |
| 7:30–9:00 | `src/s3_regression.py` + `f6_plv_diagnostics.png` | Explain why the first OLS failed (60% zeros → negative R²) and the two-part model + smearing. Show the decile chart. |
| 9:00–10:30 | `src/s4_sem.py` (model string) + `f8_sem_path_diagram.png` | Read the SEM syntax line by line. Doctor communication is the top driver. Mention the perfect fit is expected; the single-factor model fits badly. Loyalty → real return visits OR = 1.60. |
| 10:30–11:45 | `f9_acf_pacf.png`, `f10_forecast.png`, `t14_forecast_comparison.csv` | Box–Jenkins steps; ARIMA(2,1,1)+Fourier MAPE 5.8% vs Holt–Winters 4.5%; Q1-2026 outlook. |
| 11:45–13:15 | `src/s6_ml.py` pipeline + `f12_roc_confusion.png`, `f13_feature_importance.png` | Four models with 5-fold CV; logistic regression wins (AUC 0.887); recency dominates. Why the simple model beats the neural net. |
| 13:15–14:15 | Slide 14–15 | Recommendations for management and patient care; limitations (simulated data) and future work (real data, SHAP, survival, fairness). |
| 14:15–15:00 | Slide 16 + GitHub page | Show the GitHub repo and README links. Thank the audience. |

## Likely questions to prepare

- *Why is the SEM fit perfect?* Because the survey was generated from exactly that structure; the single-factor model (CFI 0.50) shows the indices still discriminate.
- *Why not use real data?* Confidentiality, and the need for survey + visits for the same patients; the code runs unchanged on real data with the same columns.
- *Why did logistic regression beat the neural network?* The main relation (recency → churn) is simple and monotonic; with ~3,000 patients a neural net has little more to learn and overfits more easily.
- *What is Duan's smearing?* exp() of a mean log prediction underestimates the mean; multiplying by the average of exp(residuals) corrects it.
- *How did you avoid leakage?* Fixed cut-off date; preprocessing inside scikit-learn pipelines so cross-validation folds never see test data.
