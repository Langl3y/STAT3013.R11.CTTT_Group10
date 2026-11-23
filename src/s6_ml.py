"""Stage 6 - Machine learning / deep learning: predicting patient churn.

Churn = the patient (seen by 31 Dec 2024) does NOT come back in Jan-Jun 2025.
Models: Logistic Regression (interpretable baseline), Random Forest, Gradient Boosting,
and a Multi-Layer Perceptron neural network (the deep-learning model).
Evaluation: 5-fold stratified cross-validation on the training set + a held-out 20% test set.
Metrics: accuracy, precision, sensitivity (recall), specificity, F1, ROC-AUC.
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from common import load, patient_features, save_fig, save_table, update_results

NUMS = ["age", "frequency", "monetary", "avg_spend", "avg_wait", "recency_days", "tenure_days", "n_departments"]
CATS = ["gender", "insurance", "chronic_condition", "care_programme", "acquisition_channel", "main_department"]


def build_models():
    prep = ColumnTransformer([("num", StandardScaler(), NUMS),
                              ("cat", OneHotEncoder(drop="first", handle_unknown="ignore"), CATS)])
    return {
        "Logistic Regression": Pipeline([("prep", prep), ("clf", LogisticRegression(max_iter=2000))]),
        "Random Forest": Pipeline([("prep", prep), ("clf", RandomForestClassifier(
            n_estimators=500, min_samples_leaf=5, random_state=42, n_jobs=-1))]),
        "Gradient Boosting": Pipeline([("prep", prep), ("clf", HistGradientBoostingClassifier(
            learning_rate=0.05, max_iter=300, max_depth=4, random_state=42))]),
        "MLP Neural Network": Pipeline([("prep", prep), ("clf", MLPClassifier(
            hidden_layer_sizes=(64, 32), alpha=1e-3, early_stopping=True, max_iter=500, random_state=42))]),
    }


def main():
    patients, visits, _ = load()
    df = patient_features(patients, visits)
    X, y = df[NUMS + CATS], 1 - df.returned  # 1 = churned
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    cv = StratifiedKFold(5, shuffle=True, random_state=42)

    rows, probs = [], {}
    for name, model in build_models().items():
        cv_auc = cross_val_score(model, X_tr, y_tr, cv=cv, scoring="roc_auc")
        model.fit(X_tr, y_tr)
        p = model.predict_proba(X_te)[:, 1]
        pred = (p >= 0.5).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_te, pred).ravel()
        probs[name] = (model, p)
        rows.append({"Model": name, "CV AUC (mean)": cv_auc.mean(), "CV AUC (sd)": cv_auc.std(),
                     "Test AUC": roc_auc_score(y_te, p), "Accuracy": accuracy_score(y_te, pred),
                     "Precision": precision_score(y_te, pred), "Sensitivity": recall_score(y_te, pred),
                     "Specificity": tn / (tn + fp), "F1": f1_score(y_te, pred)})
    res = pd.DataFrame(rows).set_index("Model").round(3)
    save_table(res, "t17_ml_comparison")
    best = res["CV AUC (mean)"].idxmax()

    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for name, (_, p) in probs.items():
        fpr, tpr, _ = roc_curve(y_te, p)
        ax[0].plot(fpr, tpr, label=f"{name} (AUC={roc_auc_score(y_te, p):.3f})")
    ax[0].plot([0, 1], [0, 1], "k--", lw=0.8); ax[0].legend(fontsize=8, loc="lower right")
    ax[0].set(title="ROC curves (test set)", xlabel="1 - specificity", ylabel="Sensitivity")
    ConfusionMatrixDisplay.from_predictions(y_te, (probs[best][1] >= 0.5).astype(int), ax=ax[1],
                                            display_labels=["Returned", "Churned"], colorbar=False, cmap="Blues")
    ax[1].set_title(f"Confusion matrix - {best}")
    save_fig(fig, "f12_roc_confusion")

    # Which features drive the best model? (permutation importance on the test set, AUC drop)
    imp = permutation_importance(probs[best][0], X_te, y_te, scoring="roc_auc", n_repeats=20, random_state=42)
    imp = pd.DataFrame({"mean_auc_drop": imp.importances_mean, "sd": imp.importances_std},
                       index=X_te.columns).sort_values("mean_auc_drop")
    save_table(imp.round(4), "t18_permutation_importance")
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.barh(imp.index, imp.mean_auc_drop, xerr=imp.sd, color="#4C72B0")
    ax.set(title=f"Permutation importance - {best}", xlabel="drop in test AUC when shuffled")
    save_fig(fig, "f13_feature_importance")

    # Logistic regression odds ratios - easy to explain to managers
    lr = probs["Logistic Regression"][0]
    names = lr.named_steps["prep"].get_feature_names_out()
    orat = pd.Series(np.exp(lr.named_steps["clf"].coef_[0]), index=names, name="odds_ratio_per_SD_or_level")
    save_table(orat.round(3).sort_values().to_frame(), "t19_logit_odds_ratios")

    update_results("ml", {"comparison": res.to_dict(orient="index"), "best_model": best,
                          "churn_rate": float(y.mean()), "n_train": len(X_tr), "n_test": len(X_te),
                          "top_features": imp.mean_auc_drop.sort_values(ascending=False).head(5).round(4).to_dict()})
    print(res); print("best:", best); print(imp.tail(6)); print(orat.round(3).sort_values())


if __name__ == "__main__":
    main()
