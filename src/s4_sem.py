"""Stage 4 - Structural Equation Modeling (SEM) of patient satisfaction and loyalty.

Measurement model (CFA): six latent constructs, each measured by 3-4 Likert items
    SQ  Service quality         SQ1-SQ4
    DC  Doctor communication    DC1-DC4
    AC  Access & convenience    AC1-AC3
    PF  Price fairness          PF1-PF3
    SAT Overall satisfaction    SAT1-SAT3
    LOY Loyalty intention       LOY1-LOY3
Structural model:
    SAT <- SQ + DC + AC + PF          LOY <- SAT
Then we bridge survey and behaviour: does stated loyalty predict an actual return visit?
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import semopy
import statsmodels.formula.api as smf

from common import load, patient_features, save_fig, save_table, update_results

CONSTRUCTS = {"SQ": 4, "DC": 4, "AC": 3, "PF": 3, "SAT": 3, "LOY": 3}
MEASUREMENT = "\n".join(f"{c} =~ " + " + ".join(f"{c}{i}" for i in range(1, n + 1))
                        for c, n in CONSTRUCTS.items())
STRUCTURAL = "SAT ~ SQ + DC + AC + PF\nLOY ~ SAT"
FULL_NAMES = {"SQ": "Service\nquality", "DC": "Doctor\ncommunication", "AC": "Access &\nconvenience",
              "PF": "Price\nfairness", "SAT": "Satisfaction", "LOY": "Loyalty\nintention"}


def cronbach_alpha(items):
    k = items.shape[1]
    return k / (k - 1) * (1 - items.var(ddof=1).sum() / items.sum(axis=1).var(ddof=1))


def draw_path_diagram(paths, fit, fname):
    pos = {"SQ": (0, 3), "DC": (0, 2), "AC": (0, 1), "PF": (0, 0), "SAT": (2.2, 1.5), "LOY": (4.2, 1.5)}
    fig, ax = plt.subplots(figsize=(8, 4.2))
    for _, r in paths.iterrows():
        (x0, y0), (x1, y1) = pos[r.rval], pos[r.lval]
        sig = r.p_value < 0.05
        ax.annotate("", xy=(x1 - 0.45, y1), xytext=(x0 + 0.5, y0),
                    arrowprops=dict(arrowstyle="-|>", lw=1 + 3 * abs(r.std_est), color="#333" if sig else "#bbb"))
        mx, my = (x0 + 0.5 + x1 - 0.45) / 2, (y0 + y1) / 2
        star = "***" if r.p_value < .001 else "**" if r.p_value < .01 else "*" if r.p_value < .05 else " (ns)"
        ax.text(mx, my + 0.1, f"β={r.std_est:.2f}{star}", ha="center", fontsize=9,
                bbox=dict(fc="white", ec="none", pad=1))
    for k, (x, y) in pos.items():
        ax.add_patch(plt.matplotlib.patches.Ellipse((x, y), 1.0, 0.7, fc="#DCE6F2", ec="#4C72B0", lw=1.5))
        ax.text(x, y, FULL_NAMES[k], ha="center", va="center", fontsize=9)
    ax.text(4.2, 0.2, f"R²(SAT)={fit['r2_SAT']:.2f}\nR²(LOY)={fit['r2_LOY']:.2f}\n"
                      f"CFI={fit['CFI']:.3f}  TLI={fit['TLI']:.3f}\nRMSEA={fit['RMSEA']:.3f}",
            ha="center", fontsize=9)
    ax.set_xlim(-0.7, 5); ax.set_ylim(-0.6, 3.6); ax.axis("off")
    ax.set_title("SEM path diagram (standardised coefficients)")
    save_fig(fig, fname)


def main():
    patients, visits, survey = load()
    items = survey.drop(columns="patient_id")

    model = semopy.Model(MEASUREMENT + "\n" + STRUCTURAL)
    model.fit(items)
    est = model.inspect(std_est=True).rename(columns={"p-value": "p_value"})
    # semopy writes both loadings (item ~ construct) and paths (construct ~ construct) with op "~";
    # the first indicator of each construct is fixed to 1, so its SE / p-value are "-".
    est[["Std. Err", "p_value"]] = est[["Std. Err", "p_value"]].apply(pd.to_numeric, errors="coerce")
    is_path = (est.op == "~") & est.lval.isin(CONSTRUCTS)
    stats = semopy.calc_stats(model).T.iloc[:, 0]

    # Reliability & convergent validity: Cronbach's alpha, composite reliability, AVE
    load_ = est[(est.op == "~") & ~est.lval.isin(CONSTRUCTS)]
    rel = {}
    for c in CONSTRUCTS:
        lam = load_.loc[load_.rval == c, "Est. Std"].astype(float).to_numpy()
        cols = [f"{c}{i}" for i in range(1, CONSTRUCTS[c] + 1)]
        rel[c] = {"alpha": cronbach_alpha(items[cols]),
                  "CR": lam.sum()**2 / (lam.sum()**2 + (1 - lam**2).sum()),
                  "AVE": (lam**2).mean(), "min_loading": lam.min()}
    rel = pd.DataFrame(rel).T.round(3)
    # Fornell-Larcker: sqrt(AVE) should exceed correlations with other constructs
    scores = pd.DataFrame({c: items[[f"{c}{i}" for i in range(1, n + 1)]].mean(axis=1)
                           for c, n in CONSTRUCTS.items()})
    fl = scores.corr().round(3)
    for c in CONSTRUCTS:
        fl.loc[c, c] = round(np.sqrt(rel.loc[c, "AVE"]), 3)
    save_table(rel, "t8_sem_reliability")
    save_table(fl, "t9_fornell_larcker")

    paths = est[is_path][["lval", "rval", "Estimate", "Est. Std", "Std. Err", "p_value"]].copy()
    paths.columns = ["lval", "rval", "estimate", "std_est", "se", "p_value"]
    paths[["estimate", "std_est", "se", "p_value"]] = paths[["estimate", "std_est", "se", "p_value"]].astype(float)
    save_table(paths.round(4), "t10_sem_paths", index=False)
    save_table(load_[["lval", "rval", "Estimate", "Est. Std", "p_value"]].rename(columns={"lval": "item", "rval": "construct"}).round(3), "t11_sem_loadings", index=False)

    var = est[(est.op == "~~") & (est.lval == est.rval)].set_index("lval")["Est. Std"].astype(float)
    fit = {"chi2": stats["chi2"], "df": stats["DoF"], "chi2_p": stats["chi2 p-value"],
           "CFI": stats["CFI"], "TLI": stats["TLI"], "RMSEA": stats["RMSEA"], "GFI": stats["GFI"],
           "AGFI": stats["AGFI"], "r2_SAT": 1 - var["SAT"], "r2_LOY": 1 - var["LOY"], "n": len(items)}
    draw_path_diagram(paths, fit, "f8_sem_path_diagram")

    # Comparison: a single-factor model (Harman's test for common-method bias).
    # If one general factor fitted as well as six constructs, the constructs would not be distinct.
    one = semopy.Model("G =~ " + " + ".join(items.columns))
    one.fit(items)
    s1 = semopy.calc_stats(one).T.iloc[:, 0]
    compare = pd.DataFrame({
        "Six-construct SEM": {k: fit[k] for k in ["chi2", "df", "CFI", "TLI", "RMSEA"]},
        "Single factor": {"chi2": s1["chi2"], "df": s1["DoF"], "CFI": s1["CFI"], "TLI": s1["TLI"], "RMSEA": s1["RMSEA"]},
    }).T.astype(float).round(3)
    save_table(compare, "t12_sem_model_comparison")

    # Bridge to behaviour: respondents in the 2024 cohort - does stated loyalty predict returning?
    df = patient_features(patients, visits)
    s = scores.assign(patient_id=survey.patient_id).set_index("patient_id").join(df[["returned", "recency_days"]],
                                                                                   how="inner")
    s["LOY_z"] = (s.LOY - s.LOY.mean()) / s.LOY.std()
    bridge = smf.logit("returned ~ LOY_z + recency_days", data=s).fit(disp=0)
    bridge_res = {"n": int(bridge.nobs), "OR_per_SD_loyalty": float(np.exp(bridge.params["LOY_z"])),
                  "p_value": float(bridge.pvalues["LOY_z"])}

    update_results("sem", {"fit": fit, "model_comparison": compare.to_dict(orient="index"), "reliability": rel.to_dict(orient="index"),
                           "paths": paths.round(4).to_dict(orient="records"), "bridge": bridge_res})
    print(rel); print(paths.round(3)); print(compare); print({k: round(float(v), 3) for k, v in fit.items()}); print(bridge_res)


if __name__ == "__main__":
    main()
