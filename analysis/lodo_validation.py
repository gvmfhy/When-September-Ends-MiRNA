#!/usr/bin/env python3
"""
Leave-One-Dataset-Out (LODO) Cross-Validation for Forensic Biofluid Classification

Purpose: Test whether biofluid signatures generalize to "new lab" scenarios by
         holding out each dataset as a test set while training on the other two.

Design:
  - Primary classifier: Multinomial logistic regression (L2, C=1.0) - interpretable
  - Secondary classifier: Random forest (shallow, max_depth=10) - stress test
  - Features: 364 batch-corrected miRNAs
  - Labels: Plasma, Serum, Urine, Saliva (kept distinct)
  - Metrics: Confusion matrix, per-fluid precision/recall/F1, ROC-AUC
  - Random seed: 20250929 (deterministic)

Output: results/lodo/<test_dataset>/ with all artifacts for forensic audit
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)
from sklearn.preprocessing import StandardScaler, label_binarize

# Reproducibility
RANDOM_STATE = 20250929
np.random.seed(RANDOM_STATE)

# Paths
BASE_DIR = Path("results/derived/cross_cohort")
OUT_DIR = Path("results/lodo")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load batch-corrected data
print("Loading batch-corrected expression matrix...")
expr_file = BASE_DIR / "tmm_log2cpm_batch_corrected.tsv"
expr_df = pd.read_csv(expr_file, sep="\t", index_col=0)

meta_file = BASE_DIR / "sample_metadata_merged.tsv"
meta_df = pd.read_csv(meta_file, sep="\t", index_col=0)

print(f"  Expression: {expr_df.shape[0]} miRNAs × {expr_df.shape[1]} samples")
print(f"  Metadata: {meta_df.shape[0]} samples")

# Align samples
shared_samples = expr_df.columns.intersection(meta_df.index)
expr_df = expr_df[shared_samples]
meta_df = meta_df.loc[shared_samples]

print(f"  Aligned: {len(shared_samples)} samples")
print(f"  Biofluids: {meta_df['biofluid'].value_counts().to_dict()}")
print(f"  Datasets: {meta_df['dataset_id'].value_counts().to_dict()}")

# Prepare feature matrix and labels
X = expr_df.T.values  # Samples × miRNAs
y = meta_df["biofluid"].values
datasets = meta_df["dataset_id"].values
feature_names = expr_df.index.tolist()

# LODO permutations
dataset_ids = np.unique(datasets)
print(f"\nLODO permutations: {dataset_ids}")

# Model configurations
models = {
    "logistic": LogisticRegression(
        C=1.0,
        penalty="l2",
        multi_class="multinomial",
        solver="lbfgs",
        random_state=RANDOM_STATE,
        max_iter=1000,
    ),
    "random_forest": RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),
}


def compute_roc_auc_multiclass(y_true, y_pred_proba, classes):
    """Compute one-vs-rest ROC-AUC for multiclass."""
    y_bin = label_binarize(y_true, classes=classes)
    n_classes = len(classes)

    # Handle case where test set doesn't have all classes
    if y_bin.shape[1] < n_classes:
        # Pad with zeros for missing classes
        missing = n_classes - y_bin.shape[1]
        y_bin = np.hstack([y_bin, np.zeros((y_bin.shape[0], missing))])

    auc_scores = {}
    for i, cls in enumerate(classes):
        if i < y_pred_proba.shape[1]:
            try:
                auc = roc_auc_score(y_bin[:, i], y_pred_proba[:, i])
                auc_scores[cls] = auc
            except ValueError:
                auc_scores[cls] = np.nan  # Class not in test set
        else:
            auc_scores[cls] = np.nan

    return auc_scores


def plot_confusion_matrix(cm, classes, out_path, title="Confusion Matrix"):
    """Plot confusion matrix heatmap."""
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=classes,
        yticklabels=classes,
        cbar_kws={"label": "Count"},
    )
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.savefig(out_path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close()


def plot_roc_curves(y_true, y_pred_proba, classes, out_path, title="ROC Curves"):
    """Plot one-vs-rest ROC curves."""
    y_bin = label_binarize(y_true, classes=classes)
    n_classes = len(classes)

    # Handle missing classes in test set
    if y_bin.shape[1] < n_classes:
        missing = n_classes - y_bin.shape[1]
        y_bin = np.hstack([y_bin, np.zeros((y_bin.shape[0], missing))])

    plt.figure(figsize=(10, 8))

    for i, cls in enumerate(classes):
        if i < y_pred_proba.shape[1] and y_bin[:, i].sum() > 0:
            fpr, tpr, _ = roc_curve(y_bin[:, i], y_pred_proba[:, i])
            auc = roc_auc_score(y_bin[:, i], y_pred_proba[:, i])
            plt.plot(fpr, tpr, label=f"{cls} (AUC={auc:.3f})")

    plt.plot([0, 1], [0, 1], "k--", label="Random (AUC=0.500)")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(title)
    plt.legend(loc="lower right")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.savefig(out_path.with_suffix(".pdf"), bbox_inches="tight")
    plt.close()


def save_feature_importances(
    model, model_name, feature_names, classes, out_path, top_n=50
):
    """Extract and save feature importances."""
    if model_name == "logistic":
        # Coefficients: shape (n_classes, n_features) or (1, n_features) for binary
        coef = model.coef_
        # Use model.classes_ to get actual classes the model learned
        trained_classes = model.classes_

        if coef.shape[0] == 1:
            # Binary case - shouldn't happen with multinomial
            importances = pd.DataFrame(
                {"miRNA": feature_names, "coefficient": coef[0]}
            )
        else:
            # Multinomial: one row per class the model actually saw
            importance_data = {"miRNA": feature_names}
            for i, cls in enumerate(trained_classes):
                importance_data[f"coef_{cls}"] = coef[i, :]
            importances = pd.DataFrame(importance_data)

            # Add mean absolute coefficient across classes
            coef_cols = [c for c in importances.columns if c.startswith("coef_")]
            importances["mean_abs_coef"] = (
                importances[coef_cols].abs().mean(axis=1)
            )
            importances = importances.sort_values(
                "mean_abs_coef", ascending=False
            )

    elif model_name == "random_forest":
        # Feature importances: single array
        importances = pd.DataFrame(
            {
                "miRNA": feature_names,
                "importance": model.feature_importances_,
            }
        )
        importances = importances.sort_values("importance", ascending=False)

    # Save full table
    importances.to_csv(out_path, sep="\t", index=False)

    # Save top N
    top_path = out_path.with_name(out_path.stem + "_top50.tsv")
    importances.head(top_n).to_csv(top_path, sep="\t", index=False)

    return importances


# Run LODO
all_classes = np.unique(y)
print(f"\nAll classes: {all_classes}")

lodo_results = []

for test_dataset in dataset_ids:
    print(f"\n{'='*60}")
    print(f"LODO Fold: Test on {test_dataset}")
    print(f"{'='*60}")

    # Split train/test
    test_mask = datasets == test_dataset
    train_mask = ~test_mask

    X_train, X_test = X[train_mask], X[test_mask]
    y_train, y_test = y[train_mask], y[test_mask]

    train_datasets = datasets[train_mask]
    test_samples = shared_samples[test_mask]

    print(f"  Train: {X_train.shape[0]} samples from {np.unique(train_datasets)}")
    print(f"  Test: {X_test.shape[0]} samples from {test_dataset}")
    print(f"  Train biofluids: {pd.Series(y_train).value_counts().to_dict()}")
    print(f"  Test biofluids: {pd.Series(y_test).value_counts().to_dict()}")

    # Standardize features (fit on train, apply to test)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Create output directory
    fold_dir = OUT_DIR / f"test_{test_dataset}"
    fold_dir.mkdir(exist_ok=True)

    # Train and evaluate both models
    fold_results = {
        "test_dataset": test_dataset,
        "train_datasets": np.unique(train_datasets).tolist(),
        "n_train": int(X_train.shape[0]),
        "n_test": int(X_test.shape[0]),
        "train_biofluids": pd.Series(y_train).value_counts().to_dict(),
        "test_biofluids": pd.Series(y_test).value_counts().to_dict(),
        "models": {},
    }

    for model_name, model in models.items():
        print(f"\n  Training {model_name}...")
        model.fit(X_train_scaled, y_train)

        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred, labels=all_classes)
        cm_path = fold_dir / f"confusion_matrix_{model_name}.png"
        plot_confusion_matrix(
            cm, all_classes, cm_path, title=f"{model_name.replace('_', ' ').title()} - {test_dataset}"
        )

        # Classification report
        report = classification_report(
            y_test, y_pred, labels=all_classes, output_dict=True, zero_division=0
        )
        report_path = fold_dir / f"classification_report_{model_name}.txt"
        with open(report_path, "w") as f:
            f.write(
                classification_report(
                    y_test, y_pred, labels=all_classes, zero_division=0
                )
            )

        # ROC-AUC
        auc_scores = compute_roc_auc_multiclass(y_test, y_pred_proba, all_classes)
        roc_path = fold_dir / f"roc_curves_{model_name}.png"
        plot_roc_curves(
            y_test,
            y_pred_proba,
            all_classes,
            roc_path,
            title=f"{model_name.replace('_', ' ').title()} ROC - {test_dataset}",
        )

        # Feature importances
        importance_path = fold_dir / f"feature_importances_{model_name}.tsv"
        importances = save_feature_importances(
            model, model_name, feature_names, all_classes, importance_path
        )

        # Save predictions
        pred_df = pd.DataFrame(
            {
                "sample_id": test_samples,
                "true_label": y_test,
                "predicted_label": y_pred,
            }
        )
        # Add probability columns
        for i, cls in enumerate(all_classes):
            if i < y_pred_proba.shape[1]:
                pred_df[f"prob_{cls}"] = y_pred_proba[:, i]
        pred_df.to_csv(
            fold_dir / f"predictions_{model_name}.tsv", sep="\t", index=False
        )

        # Store results
        fold_results["models"][model_name] = {
            "accuracy": float(report["accuracy"]),
            "macro_avg": {
                k: float(v)
                for k, v in report["macro avg"].items()
                if k != "support"
            },
            "weighted_avg": {
                k: float(v)
                for k, v in report["weighted avg"].items()
                if k != "support"
            },
            "per_class": {
                cls: {k: float(v) for k, v in metrics.items() if k != "support"}
                for cls, metrics in report.items()
                if cls not in ["accuracy", "macro avg", "weighted avg"]
            },
            "roc_auc": {k: float(v) if not np.isnan(v) else None for k, v in auc_scores.items()},
            "top_features": importances.head(10).to_dict(orient="records"),
        }

        print(f"    Accuracy: {report['accuracy']:.3f}")
        print(f"    Macro F1: {report['macro avg']['f1-score']:.3f}")
        print(
            f"    AUC (mean): {np.nanmean(list(auc_scores.values())):.3f}"
        )

    # Save fold summary
    fold_summary_path = fold_dir / "fold_summary.json"
    with open(fold_summary_path, "w") as f:
        json.dump(fold_results, f, indent=2)

    # Reproducibility manifest
    script_path = Path(__file__)
    script_hash = hashlib.md5(script_path.read_bytes()).hexdigest()

    reproducibility = {
        "script": {
            "path": str(script_path),
            "md5": script_hash,
            "timestamp": datetime.now().isoformat(),
        },
        "random_state": RANDOM_STATE,
        "environment": {
            "python": "3.x",
            "sklearn": "1.7.2",  # From env
            "numpy": "2.3.3",
            "pandas": "2.3.2",
        },
        "data_sources": {
            "expression_matrix": str(expr_file),
            "metadata": str(meta_file),
            "n_features": len(feature_names),
            "n_samples": len(shared_samples),
        },
        "models": {
            "logistic": {
                "class": "LogisticRegression",
                "C": 1.0,
                "penalty": "l2",
                "multi_class": "multinomial",
                "solver": "lbfgs",
                "max_iter": 1000,
            },
            "random_forest": {
                "class": "RandomForestClassifier",
                "n_estimators": 100,
                "max_depth": 10,
            },
        },
        "preprocessing": {
            "standardization": "StandardScaler (fit on train, apply to test)",
        },
    }

    repro_path = fold_dir / "reproducibility.json"
    with open(repro_path, "w") as f:
        json.dump(reproducibility, f, indent=2)

    lodo_results.append(fold_results)

# Save overall summary
print(f"\n{'='*60}")
print("LODO Validation Complete")
print(f"{'='*60}")

summary = {
    "lodo_folds": lodo_results,
    "overall_statistics": {},
}

# Compute average metrics across folds
for model_name in models.keys():
    accuracies = [r["models"][model_name]["accuracy"] for r in lodo_results]
    macro_f1s = [
        r["models"][model_name]["macro_avg"]["f1-score"] for r in lodo_results
    ]

    summary["overall_statistics"][model_name] = {
        "mean_accuracy": float(np.mean(accuracies)),
        "std_accuracy": float(np.std(accuracies)),
        "mean_macro_f1": float(np.mean(macro_f1s)),
        "std_macro_f1": float(np.std(macro_f1s)),
        "accuracies_per_fold": {
            r["test_dataset"]: r["models"][model_name]["accuracy"]
            for r in lodo_results
        },
    }

    print(f"\n{model_name.replace('_', ' ').title()}:")
    print(f"  Mean Accuracy: {np.mean(accuracies):.3f} ± {np.std(accuracies):.3f}")
    print(f"  Mean Macro F1: {np.mean(macro_f1s):.3f} ± {np.std(macro_f1s):.3f}")

summary_path = OUT_DIR / "lodo_summary.json"
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)

print(f"\nResults saved to: {OUT_DIR}")
print("✓ LODO validation complete")