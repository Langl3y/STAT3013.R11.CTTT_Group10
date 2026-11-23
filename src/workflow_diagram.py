"""Draw the project workflow diagram (data -> preprocessing -> six analysis stages -> recommendations)."""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from common import save_fig


def box(ax, x, y, w, h, text, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=fc, ec="#333", lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8.5)


def arrow(ax, x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color="#333", lw=1))


def main():
    fig, ax = plt.subplots(figsize=(10, 4.2))
    box(ax, 0.0, 1.55, 1.6, 1.1, "Data (simulated)\npatients 5,000\nvisits 24,872\nsurvey 1,500", "#E8EEF7")
    box(ax, 2.1, 1.55, 1.8, 1.1, "Preprocessing\ncut-off 31-12-2024\nRFM features\nPLV & churn targets", "#E8EEF7")
    stages = ["1  Descriptive statistics", "2  Hypothesis tests (t, χ², ANOVA)", "3  Two-part regression → PLV",
              "4  SEM → satisfaction & loyalty", "5  ARIMA → weekly demand", "6  ML / DL → churn"]
    for i, s in enumerate(stages):
        y = 3.55 - i * 0.68
        box(ax, 4.5, y, 2.9, 0.52, s, "#FCEBD9")
        arrow(ax, 3.95, 2.1, 4.45, y + 0.26)
    box(ax, 8.0, 1.55, 1.9, 1.1, "Evaluation &\nrecommendations\nfor managers\nand patient care", "#E3F1E3")
    for i in range(6):
        arrow(ax, 7.45, 3.81 - i * 0.68, 7.95, 2.1)
    arrow(ax, 1.65, 2.1, 2.05, 2.1)
    ax.set_xlim(-0.1, 10); ax.set_ylim(0, 4.2); ax.axis("off")
    save_fig(fig, "f0_workflow")


if __name__ == "__main__":
    main()
