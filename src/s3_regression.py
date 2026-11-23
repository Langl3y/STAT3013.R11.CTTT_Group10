"""Stage 3 - Regression: forecasting Patient Lifetime Value (PLV).

Target: out-of-pocket spend of each patient during 2025 (next 12 months), using only
information available on 31 Dec 2024.

About 60% of patients spend nothing in 2025, so the target is a mix of zeros and a
right-skewed positive part. We use the classic health-economics TWO-PART MODEL
(Duan et al., 1983):
    Part 1  logistic regression   P(PLV > 0 | x)
    Part 2  OLS on log(PLV)       for patients with PLV > 0
    E[PLV | x] = P(PLV > 0 | x) * exp(x'b) * smearing factor
The smearing factor corrects the bias of exp() when going back from the log scale.
Part 2 is where we check the OLS assumptions. A Random Forest is the non-linear benchmark.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson

from common import TAB, load, patient_features, save_fig, save_table, update_results

RHS = ("age + C(gender) + C(insurance) + C(chronic_condition) + C(care_programme)"
       " + C(acquisition_channel) + log_frequency + log_avg_spend + recency_months"
       " + tenure_months + avg_wait")
CATS = ["gender", "insurance", "chronic_condition", "care_programme", "acquisition_channel"]
NUMS = ["age", "log_frequency", "log_avg_spend", "recency_months", "tenure_months", "avg_wait"]


def prepare(df):
    d = df.copy()
    d["any_spend"] = (d.plv_2025 > 0).astype(int)
    d["log_plv"] = np.log(d.plv_2025.where(d.plv_2025 > 0))
    d["log_frequency"] = np.log(d.frequency)
    d["log_avg_spend"] = np.log(d.avg_spend)
    d["recency_months"] = d.recency_days / 30.4
    d["tenure_months"] = d.tenure_days / 30.4
    return d


def coef_table(res, odds=False):
    ci = res.conf_int()
    t = pd.DataFrame({"coef": res.params, "se": res.bse, "z": res.tvalues, "p_value": res.pvalues,
                      "ci_low": ci[0], "ci_high": ci[1]})
    t["odds_ratio" if odds else "pct_effect"] = np.exp(t.coef) if odds else (np.exp(t.coef) - 1) * 100
    return t.round(4)


def main():
    patients, visits, _ = load()
    d = prepare(patient_features(patients, visits))
    train, test = train_test_split(d, test_size=0.2, random_state=42, stratify=d.any_spend)

    # ---- Part 1: does the patient spend anything in 2025?
    part1 = smf.logit(f"any_spend ~ {RHS}", data=train).fit(disp=0)
    save_table(coef_table(part1, odds=True), "t4a_part1_logit")

    # ---- Part 2: how much, given they spend? (robust HC3 standard errors)
    pos = train[train.any_spend == 1]
    part2 = smf.ols(f"log_plv ~ {RHS}", data=pos).fit(cov_type="HC3")
    save_table(coef_table(part2), "t4b_part2_ols")
    smear = np.mean(np.exp(part2.resid))

    X = part2.model.exog
    vif = pd.Series([variance_inflation_factor(X, i) for i in range(1, X.shape[1])],
                    index=part2.model.exog_names[1:], name="VIF")
    save_table(vif.round(2).to_frame(), "t5_vif")
    diag = {
        "part1_pseudo_R2": part1.prsquared, "part1_LLR_p": part1.llr_pvalue,
        "part2_R2": part2.rsquared, "part2_adj_R2": part2.rsquared_adj, "part2_F_p": part2.f_pvalue,
        "part2_n": int(part2.nobs), "breusch_pagan_p": het_breuschpagan(part2.resid, X)[1],
        "jarque_bera_p": stats.jarque_bera(part2.resid).pvalue, "resid_skew": stats.skew(part2.resid),
        "durbin_watson": durbin_watson(part2.resid), "max_vif": vif.max(), "smearing_factor": smear,
    }

    # ---- Out-of-sample prediction of PLV ('000 VND)
    y = test.plv_2025
    pred_2pm = part1.predict(test) * np.exp(part2.predict(test)) * smear
    Xd = pd.get_dummies(d[NUMS + CATS], drop_first=True, dtype=float)
    rf = RandomForestRegressor(n_estimators=500, min_samples_leaf=20, random_state=42, n_jobs=-1)
    rf.fit(Xd.loc[train.index], train.plv_2025)
    pred_rf = rf.predict(Xd.loc[test.index])
    preds = {"Mean baseline": np.full(len(test), train.plv_2025.mean()),
             "Two-part model": pred_2pm, "Random Forest": pred_rf}
    comp = pd.DataFrame({k: {"RMSE": np.sqrt(mean_squared_error(y, p)), "MAE": mean_absolute_error(y, p),
                             "R2": r2_score(y, p), "Spearman_rho": stats.spearmanr(y, p)[0] if np.ptp(p) > 0 else np.nan}
                         for k, p in preds.items()}).T.round(3)
    save_table(comp, "t6_plv_model_comparison")

    # Value segments: does the model rank patients well? (mean actual PLV by predicted decile)
    dec = pd.qcut(pred_2pm.rank(method="first"), 10, labels=range(1, 11))
    lift = y.groupby(dec, observed=True).mean().round(0)
    save_table(lift.rename("mean_actual_plv").to_frame(), "t7_plv_decile_lift")

    # ---- Figures
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.6))
    ax[0].scatter(part2.fittedvalues, part2.resid, s=5, alpha=0.3)
    ax[0].axhline(0, color="k", lw=0.8); ax[0].set(title="Part 2: residuals vs fitted", xlabel="fitted log(PLV)")
    sm.qqplot(part2.resid, line="45", fit=True, ax=ax[1], markersize=2); ax[1].set_title("Part 2: normal Q-Q")
    ax[2].bar(lift.index.astype(int), lift.values, color="#4C72B0")
    ax[2].set(title="Test set: actual PLV by predicted decile", xlabel="predicted decile (1 = lowest)",
              ylabel="mean 2025 spend ('000 VND)")
    save_fig(fig, "f6_plv_diagnostics")

    c = coef_table(part2).drop("Intercept").sort_values("coef")
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.errorbar(c.coef, range(len(c)), xerr=[c.coef - c.ci_low, c.ci_high - c.coef],
                fmt="o", color="#4C72B0", ecolor="grey", capsize=2)
    ax.axvline(0, color="k", lw=0.8); ax.set_yticks(range(len(c)), c.index)
    ax.set_title("Part 2 OLS coefficients on log(PLV), 95% CI")
    save_fig(fig, "f7_plv_coefficients")

    (TAB / "regression_summaries.txt").write_text(part1.summary().as_text() + "\n\n" + part2.summary().as_text())
    update_results("regression", {"diagnostics": diag, "comparison": comp.to_dict(orient="index"),
                                  "decile_lift": lift.to_dict(),
                                  "part1": coef_table(part1, True).to_dict(orient="index"),
                                  "part2": coef_table(part2).to_dict(orient="index")})
    print(coef_table(part1, True)[["odds_ratio", "p_value"]]); print(coef_table(part2)[["coef", "pct_effect", "p_value"]])
    print(comp); print(lift.to_dict()); print({k: round(float(v), 4) for k, v in diag.items()})


if __name__ == "__main__":
    main()
