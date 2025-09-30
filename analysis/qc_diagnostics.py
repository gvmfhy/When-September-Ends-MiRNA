#!/usr/bin/env python3
"""Generate QC diagnostic plots for filtered exRNA datasets.

Creates visualizations for quality control assessment:
    1. PCA plots colored by biofluid (PC1 vs PC2, scree plot)
    2. Library size distributions (boxplot, histogram)
    3. miRNA detection rates per sample
    4. TMM normalization factor distributions
    5. Sample correlation heatmaps (optional, for smaller cohorts)

Outputs are saved to results/qc/<EXR-ID>/ for documentation and
supplementary materials.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Plotting style
sns.set_style("whitegrid")
sns.set_context("notebook", font_scale=1.1)

# Directory structure
ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "derived"
QC_DIR = ROOT / "results" / "qc"
QC_DIR.mkdir(parents=True, exist_ok=True)

# Dataset configurations
DATASETS = [
    {
        "id": "EXR-KJENS1RID1-AN",
        "name": "KJENS",
        "description": "Plasma/Saliva/Urine baseline cohort",
    },
    {
        "id": "EXR-TTUSC1gCrGDH-AN",
        "name": "TTUSC",
        "description": "Serum vs EDTA plasma longitudinal series",
    },
    {
        "id": "EXR-LLAUR1AVB5CS-AN",
        "name": "LLAUR",
        "description": "Diverse biofluid isolation methods",
    },
]


def load_dataset(dataset_id: str) -> Dict:
    """Load filtered counts, TMM-normalized CPM, and metadata."""
    base_dir = RESULTS / dataset_id / "filtered"
    de_dir = RESULTS / dataset_id / "differential_expression"

    # Load filtered counts
    counts = pd.read_csv(base_dir / "miRNA_counts.filtered.tsv", sep="\t", index_col=0)

    # Load TMM-normalized log2 CPM
    tmm_log2cpm = pd.read_csv(de_dir / "tmm_log2cpm.tsv", sep="\t", index_col=0)

    # Load metadata (try filtered first, fall back to parent)
    metadata_filtered = RESULTS / dataset_id / "sample_metadata.tsv"
    if not metadata_filtered.exists():
        raise FileNotFoundError(f"Metadata not found for {dataset_id}")

    metadata = pd.read_csv(metadata_filtered, sep="\t", index_col=0)

    # Find samples present in all three sources
    common_samples = (
        counts.columns
        .intersection(metadata.index)
        .intersection(tmm_log2cpm.columns)
    )

    if len(common_samples) == 0:
        raise ValueError(f"No common samples found across counts, metadata, and TMM data for {dataset_id}")

    metadata = metadata.loc[common_samples]
    counts = counts[common_samples]
    tmm_log2cpm = tmm_log2cpm[common_samples]

    return {
        "counts": counts,
        "tmm_log2cpm": tmm_log2cpm,
        "metadata": metadata,
    }


def plot_pca(
    log2_expr: pd.DataFrame,
    metadata: pd.DataFrame,
    dataset_id: str,
    dataset_name: str,
    out_dir: Path,
):
    """Generate PCA plots colored by biofluid."""
    # Transpose for PCA (samples as rows, features as columns)
    X = log2_expr.T.values

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Run PCA
    pca = PCA()
    X_pca = pca.fit_transform(X_scaled)

    # Extract biofluid labels
    sample_ids = log2_expr.columns
    biofluids = metadata.loc[sample_ids, "biofluid"].values

    # Create color palette
    unique_fluids = sorted(set(biofluids))
    palette = sns.color_palette("husl", len(unique_fluids))
    color_map = dict(zip(unique_fluids, palette))
    colors = [color_map[f] for f in biofluids]

    # Plot PC1 vs PC2
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # PC1 vs PC2 scatter
    ax = axes[0]
    for fluid in unique_fluids:
        mask = biofluids == fluid
        ax.scatter(
            X_pca[mask, 0],
            X_pca[mask, 1],
            c=[color_map[fluid]],
            label=fluid,
            s=50,
            alpha=0.7,
            edgecolors="k",
            linewidth=0.5,
        )
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
    ax.set_title(f"{dataset_name}: PCA by Biofluid")
    ax.legend(frameon=True, loc="best")
    ax.grid(True, alpha=0.3)

    # Scree plot
    ax = axes[1]
    variance_explained = pca.explained_variance_ratio_[:10] * 100
    ax.bar(range(1, len(variance_explained) + 1), variance_explained, alpha=0.7, color="steelblue")
    ax.plot(range(1, len(variance_explained) + 1), variance_explained, "o-", color="darkblue")
    ax.set_xlabel("Principal Component")
    ax.set_ylabel("Variance Explained (%)")
    ax.set_title(f"{dataset_name}: Scree Plot")
    ax.set_xticks(range(1, 11))
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_dir / f"{dataset_id}_pca.png", dpi=300, bbox_inches="tight")
    plt.savefig(out_dir / f"{dataset_id}_pca.pdf", bbox_inches="tight")
    plt.close()

    # Save PC coordinates and variance explained
    pca_coords = pd.DataFrame(
        X_pca[:, :10],
        index=sample_ids,
        columns=[f"PC{i+1}" for i in range(10)],
    )
    pca_coords["biofluid"] = biofluids
    pca_coords.to_csv(out_dir / f"{dataset_id}_pca_coordinates.tsv", sep="\t")

    variance_df = pd.DataFrame(
        {
            "PC": [f"PC{i+1}" for i in range(10)],
            "variance_explained_pct": variance_explained,
            "cumulative_variance_pct": np.cumsum(variance_explained),
        }
    )
    variance_df.to_csv(out_dir / f"{dataset_id}_pca_variance.tsv", sep="\t", index=False)

    print(f"  PCA plots: {dataset_id}_pca.png/pdf")
    print(f"    PC1: {pca.explained_variance_ratio_[0]*100:.1f}%, PC2: {pca.explained_variance_ratio_[1]*100:.1f}%")


def plot_library_sizes(
    counts: pd.DataFrame,
    metadata: pd.DataFrame,
    dataset_id: str,
    dataset_name: str,
    out_dir: Path,
):
    """Plot library size distributions by biofluid."""
    sample_ids = counts.columns
    lib_sizes = counts.sum(axis=0)
    biofluids = metadata.loc[sample_ids, "biofluid"].values

    # Create DataFrame for plotting
    plot_df = pd.DataFrame({"library_size": lib_sizes, "biofluid": biofluids})

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Boxplot
    ax = axes[0]
    sns.boxplot(data=plot_df, x="biofluid", y="library_size", hue="biofluid", ax=ax, palette="Set2", legend=False)
    ax.set_ylabel("Library Size (total miRNA counts)")
    ax.set_xlabel("Biofluid")
    ax.set_title(f"{dataset_name}: Library Size by Biofluid")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, alpha=0.3, axis="y")

    # Histogram
    ax = axes[1]
    for fluid in sorted(set(biofluids)):
        mask = biofluids == fluid
        ax.hist(
            lib_sizes[mask],
            bins=30,
            alpha=0.6,
            label=fluid,
            edgecolor="black",
            linewidth=0.5,
        )
    ax.set_xlabel("Library Size (log10 scale)")
    ax.set_ylabel("Number of Samples")
    ax.set_xscale("log")
    ax.set_title(f"{dataset_name}: Library Size Distribution")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(out_dir / f"{dataset_id}_library_sizes.png", dpi=300, bbox_inches="tight")
    plt.savefig(out_dir / f"{dataset_id}_library_sizes.pdf", bbox_inches="tight")
    plt.close()

    print(f"  Library size plots: {dataset_id}_library_sizes.png/pdf")


def plot_detection_rates(
    counts: pd.DataFrame,
    metadata: pd.DataFrame,
    dataset_id: str,
    dataset_name: str,
    out_dir: Path,
):
    """Plot number of detected miRNAs per sample."""
    sample_ids = counts.columns
    detection_counts = (counts > 0).sum(axis=0)
    biofluids = metadata.loc[sample_ids, "biofluid"].values

    plot_df = pd.DataFrame(
        {"detected_miRNAs": detection_counts, "biofluid": biofluids}
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=plot_df, x="biofluid", y="detected_miRNAs", hue="biofluid", ax=ax, palette="Set2", legend=False)
    ax.set_ylabel("Number of Detected miRNAs (count > 0)")
    ax.set_xlabel("Biofluid")
    ax.set_title(f"{dataset_name}: miRNA Detection Rate by Biofluid")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(out_dir / f"{dataset_id}_detection_rates.png", dpi=300, bbox_inches="tight")
    plt.savefig(out_dir / f"{dataset_id}_detection_rates.pdf", bbox_inches="tight")
    plt.close()

    print(f"  Detection rate plots: {dataset_id}_detection_rates.png/pdf")


def plot_tmm_factors(dataset_id: str, dataset_name: str, out_dir: Path):
    """Plot TMM normalization factor distributions."""
    # Load summary from DE analysis
    de_dir = RESULTS / dataset_id / "differential_expression"
    summary_file = de_dir / "summary.json"

    if not summary_file.exists():
        print(f"  WARNING: TMM summary not found for {dataset_id}, skipping")
        return

    with open(summary_file) as f:
        summary = json.load(f)

    tmm_range = summary.get("tmm_factor_range", [])
    if not tmm_range:
        print(f"  WARNING: No TMM factor range in summary for {dataset_id}")
        return

    # Simple bar plot showing range
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(["Min", "Max"], tmm_range, color=["lightcoral", "steelblue"], alpha=0.7)
    ax.axhline(y=1.0, color="black", linestyle="--", linewidth=1, label="No adjustment")
    ax.set_ylabel("TMM Normalization Factor")
    ax.set_title(f"{dataset_name}: TMM Factor Range")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    plt.savefig(out_dir / f"{dataset_id}_tmm_factors.png", dpi=300, bbox_inches="tight")
    plt.savefig(out_dir / f"{dataset_id}_tmm_factors.pdf", bbox_inches="tight")
    plt.close()

    print(f"  TMM factor plot: {dataset_id}_tmm_factors.png/pdf")
    print(f"    Range: [{tmm_range[0]:.3f}, {tmm_range[1]:.3f}]")


def generate_qc_summary(dataset_id: str, data: Dict, out_dir: Path):
    """Generate a JSON summary of QC metrics."""
    counts = data["counts"]
    metadata = data["metadata"]

    lib_sizes = counts.sum(axis=0)
    detection_counts = (counts > 0).sum(axis=0)

    summary = {
        "dataset_id": dataset_id,
        "n_samples": counts.shape[1],
        "n_miRNAs": counts.shape[0],
        "library_size": {
            "min": float(lib_sizes.min()),
            "median": float(lib_sizes.median()),
            "max": float(lib_sizes.max()),
        },
        "detection_rate": {
            "min": int(detection_counts.min()),
            "median": float(detection_counts.median()),
            "max": int(detection_counts.max()),
        },
        "biofluids": list(metadata["biofluid"].value_counts().to_dict()),
        "timestamp": pd.Timestamp.now().isoformat(),
    }

    with open(out_dir / f"{dataset_id}_qc_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"  QC summary: {dataset_id}_qc_summary.json")


def run_qc_diagnostics(dataset_config: Dict):
    """Run all QC diagnostics for one dataset."""
    dataset_id = dataset_config["id"]
    dataset_name = dataset_config["name"]
    print(f"\n=== {dataset_name} ({dataset_id}) ===")

    # Create output directory
    out_dir = QC_DIR / dataset_id
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Load data
        data = load_dataset(dataset_id)
        print(f"Loaded {data['counts'].shape[0]} miRNAs × {data['counts'].shape[1]} samples")

        # Generate plots
        plot_pca(
            data["tmm_log2cpm"],
            data["metadata"],
            dataset_id,
            dataset_name,
            out_dir,
        )

        plot_library_sizes(
            data["counts"],
            data["metadata"],
            dataset_id,
            dataset_name,
            out_dir,
        )

        plot_detection_rates(
            data["counts"],
            data["metadata"],
            dataset_id,
            dataset_name,
            out_dir,
        )

        plot_tmm_factors(dataset_id, dataset_name, out_dir)

        # Generate summary
        generate_qc_summary(dataset_id, data, out_dir)

        print(f"✓ QC diagnostics complete for {dataset_name}")

    except Exception as e:
        print(f"ERROR processing {dataset_id}: {e}")
        import traceback
        traceback.print_exc()


def main():
    print("QC Diagnostics Pipeline")
    print("=" * 50)

    for dataset in DATASETS:
        run_qc_diagnostics(dataset)

    print("\n" + "=" * 50)
    print(f"All QC plots saved to: {QC_DIR}/")
    print("Outputs per dataset:")
    print("  - <ID>_pca.png/pdf (PCA scatter + scree plot)")
    print("  - <ID>_library_sizes.png/pdf (boxplot + histogram)")
    print("  - <ID>_detection_rates.png/pdf (detected miRNAs per sample)")
    print("  - <ID>_tmm_factors.png/pdf (normalization factor range)")
    print("  - <ID>_pca_coordinates.tsv (PC1-10 coordinates)")
    print("  - <ID>_pca_variance.tsv (variance explained)")
    print("  - <ID>_qc_summary.json (metrics summary)")


if __name__ == "__main__":
    main()