"""Stage 5 - Forecasting weekly patient visits with ARIMA.

Steps (Box-Jenkins):
  1. Stationarity: ADF test on the level and first difference.
  2. Identification: ACF / PACF plots.
  3. Estimation: grid search ARIMA(p,1,q) with Fourier terms for the yearly flu season
     (a 52-week seasonal ARIMA needs many years of data; Fourier terms need only 2 parameters
     per harmonic). Choose by AIC on the training period.
  4. Diagnostics: Ljung-Box test on residuals.
  5. Evaluation on the last 13 weeks (one quarter) vs seasonal-naive and Holt-Winters benchmarks.
  6. Refit on all data and forecast the first quarter of 2026.
"""
import itertools
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller

from common import load, save_fig, save_table, update_results

warnings.filterwarnings("ignore")
H = 13  # test horizon in weeks
K = 2   # Fourier harmonics for yearly seasonality
PERIOD = 365.25 / 7


def fourier(index, start):
    t = ((index - start).days / 7).to_numpy()
    cols = {}
    for k in range(1, K + 1):
        cols[f"sin{k}"] = np.sin(2 * np.pi * k * t / PERIOD)
        cols[f"cos{k}"] = np.cos(2 * np.pi * k * t / PERIOD)
    return pd.DataFrame(cols, index=index)


def tet_dummy(index):
    tet = pd.to_datetime(["2023-01-22", "2024-02-10", "2025-01-29", "2026-02-17"])
    return pd.Series([int(any(abs((d - t).days) <= 6 for t in tet)) for d in index], index=index, name="tet")


def exog(index, start):
    return fourier(index, start).join(tet_dummy(index))


def metrics(y, f):
    e = y - f
    return {"MAE": np.abs(e).mean(), "RMSE": np.sqrt((e**2).mean()), "MAPE_%": (np.abs(e) / y).mean() * 100}


def main():
    _, visits, _ = load()
    # Weeks run Monday-Sunday; drop the partial first and last weeks
    y = visits.set_index("visit_date").resample("W-SUN").size().astype(float)
    y = y[(y.index >= "2023-01-08") & (y.index <= "2025-12-28")]
    start = y.index[0]
    train, test = y.iloc[:-H], y.iloc[-H:]

    adf = {"level_p": adfuller(train)[1], "diff1_p": adfuller(train.diff().dropna())[1]}

    fig, ax = plt.subplots(1, 2, figsize=(11, 3.2))
    plot_acf(train.diff().dropna(), lags=40, ax=ax[0]); ax[0].set_title("ACF of differenced series")
    plot_pacf(train.diff().dropna(), lags=40, ax=ax[1], method="ywm"); ax[1].set_title("PACF of differenced series")
    save_fig(fig, "f9_acf_pacf")

    X_tr, X_te = exog(train.index, start), exog(test.index, start)
    grid = []
    for p, q in itertools.product(range(4), range(4)):
        try:
            m = SARIMAX(train, exog=X_tr, order=(p, 1, q), trend="t").fit(disp=False)
            grid.append({"p": p, "d": 1, "q": q, "AIC": m.aic, "BIC": m.bic})
        except Exception:
            pass
    grid = pd.DataFrame(grid).sort_values("AIC").reset_index(drop=True)
    save_table(grid.round(2), "t13_arima_grid", index=False)
    p, q = int(grid.p[0]), int(grid.q[0])
    best = SARIMAX(train, exog=X_tr, order=(p, 1, q), trend="t").fit(disp=False)
    lb = acorr_ljungbox(best.resid.iloc[1:], lags=[10, 20], return_df=True)

    fc = best.get_forecast(H, exog=X_te)
    f_arima, ci = fc.predicted_mean, fc.conf_int(alpha=0.05)
    f_snaive = pd.Series(y.shift(52).loc[test.index].to_numpy(), index=test.index)
    hw = ExponentialSmoothing(train, trend="add", seasonal="add", seasonal_periods=52).fit()
    f_hw = hw.forecast(H)

    comp = pd.DataFrame({f"ARIMA({p},1,{q}) + Fourier": metrics(test, f_arima),
                         "Holt-Winters (additive)": metrics(test, f_hw),
                         "Seasonal naive (t-52)": metrics(test, f_snaive)}).T.round(2)
    save_table(comp, "t14_forecast_comparison")
    coverage = ((test >= ci.iloc[:, 0]) & (test <= ci.iloc[:, 1])).mean()

    # Refit on all data and forecast Q1-2026
    full = SARIMAX(y, exog=exog(y.index, start), order=(p, 1, q), trend="t").fit(disp=False)
    fut_idx = pd.date_range(y.index[-1] + pd.Timedelta(weeks=1), periods=H, freq="W-SUN")
    ffc = full.get_forecast(H, exog=exog(fut_idx, start))
    future = pd.DataFrame({"forecast": ffc.predicted_mean, "lower95": ffc.conf_int().iloc[:, 0],
                           "upper95": ffc.conf_int().iloc[:, 1]}).round(1)
    save_table(future, "t15_forecast_2026Q1")

    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(train.index, train, color="#4C72B0", label="Training data")
    ax.plot(test.index, test, color="k", label="Actual (test)")
    ax.plot(test.index, f_arima, color="#C44E52", label=f"ARIMA({p},1,{q})+Fourier")
    ax.fill_between(test.index, ci.iloc[:, 0], ci.iloc[:, 1], color="#C44E52", alpha=0.15)
    ax.plot(test.index, f_hw, "--", color="#55A868", label="Holt-Winters")
    ax.plot(future.index, future.forecast, color="#8172B2", label="Forecast Q1-2026")
    ax.fill_between(future.index, future.lower95, future.upper95, color="#8172B2", alpha=0.15)
    ax.set_title("Weekly visits: test-period forecasts and Q1-2026 outlook (95% intervals)")
    ax.legend(loc="upper left", fontsize=8)
    save_fig(fig, "f10_forecast")

    fig, ax = plt.subplots(1, 2, figsize=(11, 3))
    best.resid.iloc[1:].plot(ax=ax[0], title="ARIMA residuals"); plot_acf(best.resid.iloc[1:], lags=30, ax=ax[1])
    ax[1].set_title("ACF of residuals")
    save_fig(fig, "f11_arima_residuals")

    (save_table(pd.DataFrame(best.summary().tables[1].data[1:], columns=best.summary().tables[1].data[0]),
                "t16_arima_params", index=False))
    update_results("forecast", {"adf": adf, "order": [p, 1, q], "aic": best.aic,
                                "ljung_box_p": lb.lb_pvalue.to_dict(), "comparison": comp.to_dict(orient="index"),
                                "interval_coverage_test": coverage, "n_weeks": len(y),
                                "q1_2026_total": future.forecast.sum()})
    print(adf); print(grid.head()); print(best.summary().tables[1]); print(lb); print(comp)
    print("coverage", coverage); print(future)


if __name__ == "__main__":
    main()
