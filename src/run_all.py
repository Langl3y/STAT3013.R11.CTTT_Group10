"""Reproduce the whole project: simulate data, then run the six analysis stages in order."""
import time

import s1_descriptive
import s2_inferential
import s3_regression
import s4_sem
import s5_forecast
import s6_ml
import simulate
import workflow_diagram

STAGES = [("Simulate data", simulate.main), ("Workflow diagram", workflow_diagram.main),
          ("1 Descriptive", s1_descriptive.main),
          ("2 Inferential", s2_inferential.main), ("3 Regression (PLV)", s3_regression.main),
          ("4 SEM", s4_sem.main), ("5 Forecasting (ARIMA)", s5_forecast.main),
          ("6 Machine learning (churn)", s6_ml.main)]

if __name__ == "__main__":
    for name, fn in STAGES:
        t = time.time()
        print(f"\n===== {name} =====")
        fn()
        print(f"[{name}: {time.time() - t:.1f}s]")
    print("\nDone. Figures in outputs/figures, tables in outputs/tables, numbers in outputs/results.json")
