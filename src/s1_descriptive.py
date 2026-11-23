"""Stage 1 - Descriptive statistics: distributions, means, variances, skewness."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

from common import load, patient_features, save_fig, save_table, update_results


def main():
    patients, visits, survey = load()
    df = patient_features(patients, visits)

    # Summary table for the key numeric variables
    cols = {
        "Age (years)": patients.age,
        "Visit cost ('000 VND)": visits.total_cost_kvnd,
        "Out-of-pocket ('000 VND)": visits.out_of_pocket_kvnd,
        "Waiting time (min)": visits.wait_minutes,
        "Visits per patient (to 2024)": df.frequency,
        "Patient spend 2025 ('000 VND)": df.plv_2025,
    }
    summary = pd.DataFrame({
        k: {"N": v.count(), "Mean": v.mean(), "SD": v.std(), "Variance": v.var(),
            "Median": v.median(), "Min": v.min(), "Max": v.max(),
            "Skewness": stats.skew(v), "Kurtosis": stats.kurtosis(v)}
        for k, v in cols.items()}).T.round(2)
    save_table(summary, "t1_descriptive_summary")

    cat = pd.concat({c: patients[c].value_counts(normalize=True).mul(100).round(1)
                     for c in ["gender", "insurance", "chronic_condition", "care_programme",
                               "acquisition_channel", "main_department"]})
    save_table(cat.rename("percent").to_frame(), "t2_categorical_profile")

    # Figures
    fig, ax = plt.subplots(1, 3, figsize=(12, 3.4))
    sns.histplot(patients.age, bins=30, ax=ax[0], color="#4C72B0"); ax[0].set_title("Patient age")
    sns.histplot(visits.out_of_pocket_kvnd, bins=60, ax=ax[1], color="#55A868")
    ax[1].set_title("Out-of-pocket per visit ('000 VND)"); ax[1].set_xlim(0, 3000)
    sns.histplot(visits.wait_minutes, bins=60, ax=ax[2], color="#C44E52")
    ax[2].set_title("Waiting time (minutes)"); ax[2].set_xlim(0, 150)
    save_fig(fig, "f1_histograms")

    fig, ax = plt.subplots(1, 2, figsize=(12, 3.8))
    order = visits.groupby("department").total_cost_kvnd.median().sort_values().index
    sns.boxplot(data=visits, x="department", y="total_cost_kvnd", order=order, ax=ax[0],
                showfliers=False, color="#8DA0CB")
    ax[0].set_title("Visit cost by department"); ax[0].set_ylabel("'000 VND"); ax[0].set_xlabel("")
    ax[0].tick_params(axis="x", rotation=20)
    sns.boxplot(data=visits, x="department", y="wait_minutes", order=order, ax=ax[1],
                showfliers=False, color="#FC8D62")
    ax[1].set_title("Waiting time by department"); ax[1].set_ylabel("minutes"); ax[1].set_xlabel("")
    ax[1].tick_params(axis="x", rotation=20)
    save_fig(fig, "f2_boxplots")

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.scatterplot(data=df, x="frequency", y="plv_2025", hue="chronic_condition", alpha=0.4, s=14, ax=ax)
    ax.set_xlabel("Visits up to Dec 2024"); ax.set_ylabel("Spend in 2025 ('000 VND)")
    ax.set_title("Past visit frequency vs next-year value")
    save_fig(fig, "f3_scatter_freq_plv")

    weekly = visits.set_index("visit_date").resample("W-SUN").size()
    weekly = weekly[(weekly.index >= "2023-01-08") & (weekly.index <= "2025-12-28")]  # complete weeks only
    fig, ax = plt.subplots(figsize=(10, 3.2))
    weekly.plot(ax=ax, color="#4C72B0"); ax.set_title("Weekly visits, 2023-2025"); ax.set_xlabel("")
    save_fig(fig, "f4_weekly_visits")

    likert = survey.drop(columns="patient_id")
    fig, ax = plt.subplots(figsize=(7, 5.5))
    sns.heatmap(likert.corr(method="spearman"), cmap="vlag", center=0, ax=ax, cbar_kws={"shrink": .7})
    ax.set_title("Spearman correlation of survey items")
    save_fig(fig, "f5_survey_corr")

    update_results("descriptive", {
        "n_patients": len(patients), "n_visits": len(visits), "n_survey": len(survey),
        "cohort_to_2024": len(df), "return_rate_h1_2025": df.returned.mean(),
        "mean_oop": visits.out_of_pocket_kvnd.mean(), "median_wait": visits.wait_minutes.median(),
        "share_zero_plv": (df.plv_2025 == 0).mean(),
    })
    print(summary)


if __name__ == "__main__":
    main()
