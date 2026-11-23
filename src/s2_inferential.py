"""Stage 2 - Inferential statistics.

H1  Care-programme members spend a different amount per year than non-members (Welch t-test,
    Mann-Whitney U as a robustness check because spending is right-skewed).
H2  Returning in H1-2025 is associated with insurance status (chi-square test of independence).
H3  Returning is associated with acquisition channel (chi-square).
H4  Mean waiting time differs between departments (one-way ANOVA + Kruskal-Wallis).
H5  Programme members report higher satisfaction (Welch t-test on mean SAT score).
"""
import numpy as np
import pandas as pd
from scipy import stats

from common import load, patient_features, save_table, update_results


def cohens_d(a, b):
    sp = np.sqrt(((len(a) - 1) * a.var() + (len(b) - 1) * b.var()) / (len(a) + len(b) - 2))
    return (a.mean() - b.mean()) / sp


def cramers_v(table):
    chi2 = stats.chi2_contingency(table)[0]
    return np.sqrt(chi2 / (table.values.sum() * (min(table.shape) - 1)))


def main():
    patients, visits, survey = load()
    df = patient_features(patients, visits)
    rows = []

    # H1: annual spend in 2024 among patients already registered before 2024
    v24 = visits[visits.visit_date.dt.year == 2024].groupby("patient_id").out_of_pocket_kvnd.sum()
    base = patients[patients.first_visit_date < "2024-01-01"].set_index("patient_id")
    spend = base.join(v24.rename("spend_2024")).fillna({"spend_2024": 0})
    a = spend.loc[spend.care_programme == "Yes", "spend_2024"]
    b = spend.loc[spend.care_programme == "No", "spend_2024"]
    t, p = stats.ttest_ind(a, b, equal_var=False)
    u, pu = stats.mannwhitneyu(a, b)
    rows.append(["H1 Spend 2024: programme vs not", "Welch t", t, p, f"d={cohens_d(a, b):.2f}",
                 f"means {a.mean():.0f} vs {b.mean():.0f}"])
    rows.append(["H1 (robustness)", "Mann-Whitney U", u, pu, "", f"medians {a.median():.0f} vs {b.median():.0f}"])

    # H2, H3: chi-square tests on the 2024 cohort's return status
    for var, label in [("insurance", "H2 Returned x insurance"), ("acquisition_channel", "H3 Returned x channel"),
                       ("chronic_condition", "H2b Returned x chronic")]:
        tab = pd.crosstab(df[var], df.returned)
        chi2, p, dof, _ = stats.chi2_contingency(tab)
        rate = df.groupby(var).returned.mean().mul(100).round(1).to_dict()
        rows.append([label, f"Chi-square (df={dof})", chi2, p, f"V={cramers_v(tab):.2f}", f"return % {rate}"])

    # H4: waiting time by department
    groups = [g.wait_minutes.values for _, g in visits.groupby("department")]
    f, p = stats.f_oneway(*groups)
    h, ph = stats.kruskal(*groups)
    lev = stats.levene(*groups)
    ss_b = sum(len(g) * (g.mean() - visits.wait_minutes.mean())**2 for g in groups)
    eta2 = ss_b / ((visits.wait_minutes - visits.wait_minutes.mean())**2).sum()
    rows.append(["H4 Wait time across departments", "One-way ANOVA", f, p, f"eta2={eta2:.3f}",
                 f"Levene p={lev.pvalue:.3g}"])
    rows.append(["H4 (robustness)", "Kruskal-Wallis", h, ph, "", ""])

    # H5: satisfaction score (mean of SAT1-3) by programme membership
    s = survey.assign(SAT=survey[["SAT1", "SAT2", "SAT3"]].mean(axis=1)).merge(
        patients[["patient_id", "care_programme"]], on="patient_id")
    a, b = s.loc[s.care_programme == "Yes", "SAT"], s.loc[s.care_programme == "No", "SAT"]
    t, p = stats.ttest_ind(a, b, equal_var=False)
    rows.append(["H5 Satisfaction: programme vs not", "Welch t", t, p, f"d={cohens_d(a, b):.2f}",
                 f"means {a.mean():.2f} vs {b.mean():.2f}"])

    res = pd.DataFrame(rows, columns=["Hypothesis", "Test", "Statistic", "p-value", "Effect size", "Detail"])
    res["Statistic"] = res.Statistic.astype(float).round(3)
    res["Decision (alpha=0.05)"] = np.where(res["p-value"] < 0.05, "Reject H0", "Fail to reject H0")
    save_table(res, "t3_hypothesis_tests", index=False)
    update_results("inferential", res.to_dict(orient="records"))
    pd.set_option("display.width", 200, "display.max_colwidth", 60)
    print(res)


if __name__ == "__main__":
    main()
