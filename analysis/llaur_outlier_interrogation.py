#!/usr/bin/env python3
"""Interrogate LLAUR outlier samples to assess forensic robustness.

Strategy:
    Rather than reflexively dropping samples with extreme TMM factors (0.25-63.3),
    we interrogate whether they represent:
    1. Technical failures (random scatter in PCA) → Safe to exclude
    2. Protocol effects (cluster by isolation method) → Document as method-dependent
    3. Degraded but valid samples (still cluster by biofluid) → KEEP for robustness

For forensic assays, markers that fail on "messy" samples are not court-ready.
LLAUR's variability is a feature, not a bug—it tests real-world robustness.

Outputs:
    - Outlier sample metadata table
    - PCA plots highlighting outliers vs. inliers
    - Biofluid clustering metrics for outlier subset
    - DE concordance between clean-only vs. all-samples
    - Decision matrix for sample retention/exclusion
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.spatial.distance import cdist
from scipy.stats import pearsonr
from sklearn.metrics import silhouette_score

# Plotting
sns.set_style("whitegrid")
sns.set_context("notebook", font_scale=1.1)

# Paths
ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DERIVED = RESULTS / "derived"
QC_DIR = RESULTS / "qc"
LLAUR_DIR = DERIVED / "EXR-LLAUR1AVB5CS-AN"
LLAUR_QC = QC_DIR / "EXR-LLAUR1AVB5CS-AN"
OUT_DIR = RESULTS / "outlier_analysis" / "EXR-LLAUR1AVB5CS-AN"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Thresholds for outlier definition
TMM_LOW_THRESHOLD = 0.4
TMM_HIGH_THRESHOLD = 5.0
LIBRARY_SIZE_MIN = 1000


def load_llaur_data() -> Dict:
    """Load LLAUR counts, metadata, TMM factors, and PCA coordinates."""
    print("Loading LLAUR data...")

    # Filtered counts
    counts = pd.read_csv(
        LLAUR_DIR / "filtered" / "miRNA_counts.filtered.tsv",
        sep="\t",
        index_col=0,
    )

    # Metadata (includes library_size)
    metadata = pd.read_csv(
        LLAUR_DIR / "sample_metadata.tsv",
        sep="\t",
        index_col=0,
    )

    # TMM-normalized log2 CPM
    tmm_log2cpm = pd.read_csv(
        LLAUR_DIR / "differential_expression" / "tmm_log2cpm.tsv",
        sep="\t",
        index_col=0,
    )

    # PCA coordinates
    pca_coords = pd.read_csv(
        LLAUR_QC / "EXR-LLAUR1AVB5CS-AN_pca_coordinates.tsv",
        sep="\t",
        index_col=0,
    )

    # Load TMM summary to extract factors
    with open(LLAUR_DIR / "differential_expression" / "summary.json") as f:
        summary = json.load(f)

    # Align all data to common samples
    common_samples = (
        counts.columns
        .intersection(metadata.index)
        .intersection(tmm_log2cpm.columns)
        .intersection(pca_coords.index)
    )

    print(f"  Common samples across all sources: {len(common_samples)}")

    return {
        "counts": counts[common_samples],
        "metadata": metadata.loc[common_samples],
        "tmm_log2cpm": tmm_log2cpm[common_samples],
        "pca_coords": pca_coords.loc[common_samples],
        "tmm_range": summary["tmm_factor_range"],
    }


def compute_tmm_factors(counts: pd.DataFrame) -> pd.Series:
    """Re-compute TMM factors manually for per-sample attribution."""
    # Simple proxy: library size ratio to median
    lib_sizes = counts.sum(axis=0)
    median_lib = lib_sizes.median()
    tmm_proxy = median_lib / lib_sizes  # Inverse because TMM upweights small libraries
    return tmm_proxy


def identify_outliers(data: Dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Identify outlier samples based on TMM factors and library size."""
    counts = data["counts"]
    metadata = data["metadata"]

    # Compute per-sample TMM proxy
    tmm_factors = compute_tmm_factors(counts)

    # Library sizes
    lib_sizes = counts.sum(axis=0)

    # Combine into analysis table
    analysis = metadata.copy()
    analysis["library_size_computed"] = lib_sizes
    analysis["tmm_factor_proxy"] = tmm_factors

    # Define outliers
    analysis["is_outlier"] = (
        (tmm_factors < TMM_LOW_THRESHOLD)
        | (tmm_factors > TMM_HIGH_THRESHOLD)
        | (lib_sizes < LIBRARY_SIZE_MIN)
    )

    outliers = analysis[analysis["is_outlier"]]
    inliers = analysis[~analysis["is_outlier"]]

    print(f"\nOutlier identification:")
    print(f"  Total samples: {len(analysis)}")
    print(f"  Outliers: {len(outliers)} ({len(outliers)/len(analysis)*100:.1f}%)")
    print(f"  Inliers: {len(inliers)}")

    return outliers, inliers


def plot_outlier_characteristics(outliers: pd.DataFrame, inliers: pd.DataFrame):
    """Plot outlier vs inlier distributions."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # TMM factors
    ax = axes[0, 0]
    ax.hist(inliers["tmm_factor_proxy"], bins=30, alpha=0.7, label="Inliers", color="steelblue")
    ax.hist(outliers["tmm_factor_proxy"], bins=30, alpha=0.7, label="Outliers", color="coral")
    ax.axvline(TMM_LOW_THRESHOLD, color="red", linestyle="--", linewidth=1, label=f"Threshold {TMM_LOW_THRESHOLD}")
    ax.axvline(TMM_HIGH_THRESHOLD, color="red", linestyle="--", linewidth=1)
    ax.set_xlabel("TMM Factor (proxy)")
    ax.set_ylabel("Number of Samples")
    ax.set_title("TMM Factor Distribution")
    ax.legend()
    ax.set_xscale("log")

    # Library sizes
    ax = axes[0, 1]
    ax.hist(inliers["library_size_computed"], bins=30, alpha=0.7, label="Inliers", color="steelblue")
    ax.hist(outliers["library_size_computed"], bins=30, alpha=0.7, label="Outliers", color="coral")
    ax.axvline(LIBRARY_SIZE_MIN, color="red", linestyle="--", linewidth=1, label=f"Min {LIBRARY_SIZE_MIN}")
    ax.set_xlabel("Library Size")
    ax.set_ylabel("Number of Samples")
    ax.set_title("Library Size Distribution")
    ax.legend()
    ax.set_xscale("log")

    # Biofluid breakdown for outliers
    ax = axes[1, 0]
    if len(outliers) > 0:
        outlier_fluids = outliers["biofluid"].value_counts()
        outlier_fluids.plot(kind="bar", ax=ax, color="coral", alpha=0.7)
        ax.set_ylabel("Number of Outlier Samples")
        ax.set_xlabel("Biofluid")
        ax.set_title("Outliers by Biofluid")
        ax.tick_params(axis="x", rotation=45)
    else:
        ax.text(0.5, 0.5, "No outliers detected", ha="center", va="center")
        ax.set_title("Outliers by Biofluid")

    # Isolation method breakdown (if available)
    ax = axes[1, 1]
    if len(outliers) > 0 and "isolation_method" in outliers.columns:
        outlier_methods = outliers["isolation_method"].value_counts().head(10)
        if len(outlier_methods) > 0:
            outlier_methods.plot(kind="barh", ax=ax, color="coral", alpha=0.7)
            ax.set_xlabel("Number of Outlier Samples")
            ax.set_ylabel("Isolation Method")
            ax.set_title("Outliers by Isolation Method (Top 10)")
        else:
            ax.text(0.5, 0.5, "No isolation method data", ha="center", va="center")
    else:
        ax.text(0.5, 0.5, "Isolation method not available", ha="center", va="center")

    plt.tight_layout()
    plt.savefig(OUT_DIR / "outlier_characteristics.png", dpi=300, bbox_inches="tight")
    plt.savefig(OUT_DIR / "outlier_characteristics.pdf", bbox_inches="tight")
    plt.close()

    print(f"  Saved: outlier_characteristics.png/pdf")


def plot_pca_with_outliers(pca_coords: pd.DataFrame, outliers: pd.DataFrame, inliers: pd.DataFrame):
    """Plot PCA with outliers highlighted."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Get biofluid labels
    all_samples = pd.concat([inliers, outliers])
    biofluids = all_samples["biofluid"]

    # PC1 vs PC2 colored by biofluid, shaped by outlier status
    ax = axes[0]
    for fluid in sorted(set(biofluids)):
        # Inliers
        mask_in = (biofluids == fluid) & (all_samples.index.isin(inliers.index))
        if mask_in.sum() > 0:
            ax.scatter(
                pca_coords.loc[mask_in, "PC1"],
                pca_coords.loc[mask_in, "PC2"],
                label=f"{fluid} (inlier)",
                s=60,
                alpha=0.7,
                marker="o",
                edgecolors="k",
                linewidth=0.5,
            )

        # Outliers
        mask_out = (biofluids == fluid) & (all_samples.index.isin(outliers.index))
        if mask_out.sum() > 0:
            ax.scatter(
                pca_coords.loc[mask_out, "PC1"],
                pca_coords.loc[mask_out, "PC2"],
                label=f"{fluid} (outlier)",
                s=120,
                alpha=0.9,
                marker="X",
                edgecolors="red",
                linewidth=2,
            )

    ax.set_xlabel("PC1 (30.2%)")
    ax.set_ylabel("PC2 (6.7%)")
    ax.set_title("LLAUR: PCA with Outliers Highlighted")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)

    # PC1 vs PC3 (in case outliers separate better here)
    ax = axes[1]
    for fluid in sorted(set(biofluids)):
        mask_in = (biofluids == fluid) & (all_samples.index.isin(inliers.index))
        if mask_in.sum() > 0:
            ax.scatter(
                pca_coords.loc[mask_in, "PC1"],
                pca_coords.loc[mask_in, "PC3"],
                s=60,
                alpha=0.7,
                marker="o",
                edgecolors="k",
                linewidth=0.5,
            )

        mask_out = (biofluids == fluid) & (all_samples.index.isin(outliers.index))
        if mask_out.sum() > 0:
            ax.scatter(
                pca_coords.loc[mask_out, "PC1"],
                pca_coords.loc[mask_out, "PC3"],
                s=120,
                alpha=0.9,
                marker="X",
                edgecolors="red",
                linewidth=2,
            )

    ax.set_xlabel("PC1 (30.2%)")
    ax.set_ylabel("PC3")
    ax.set_title("LLAUR: PC1 vs PC3")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUT_DIR / "pca_outliers_highlighted.png", dpi=300, bbox_inches="tight")
    plt.savefig(OUT_DIR / "pca_outliers_highlighted.pdf", bbox_inches="tight")
    plt.close()

    print(f"  Saved: pca_outliers_highlighted.png/pdf")


def assess_biofluid_clustering(pca_coords: pd.DataFrame, metadata: pd.DataFrame, group: str):
    """Compute silhouette score for biofluid clustering."""
    samples = metadata.index
    if len(samples) < 2:
        return None

    coords = pca_coords.loc[samples, ["PC1", "PC2", "PC3"]].values
    labels = metadata.loc[samples, "biofluid"].values

    # Require at least 2 classes
    unique_labels = set(labels)
    if len(unique_labels) < 2:
        return None

    try:
        score = silhouette_score(coords, labels)
        return score
    except:
        return None


def compare_de_concordance(counts: pd.DataFrame, metadata: pd.DataFrame, outliers: pd.DataFrame, inliers: pd.DataFrame):
    """Compare DE results using all samples vs. inliers-only."""
    print("\nComparing differential expression concordance...")

    # Load existing DE results (all samples)
    de_dir = LLAUR_DIR / "differential_expression"
    de_all = pd.read_csv(de_dir / "de_all_fluids.tsv", sep="\t")

    # For each biofluid, extract top 50 upregulated miRNAs from full analysis
    concordance_results = []

    for fluid in ["Plasma", "Serum", "Urine"]:
        de_fluid_all = de_all[de_all["biofluid"] == fluid].copy()
        de_fluid_all = de_fluid_all[(de_fluid_all["logFC"] > 0) & (de_fluid_all["adj.P.Val"] < 0.05)]
        de_fluid_all = de_fluid_all.sort_values("AUC", ascending=False).head(50)

        top50_all = set(de_fluid_all["miRNA"].values)

        # Check how many of these are also in top 100 when using inliers only
        # (We can't re-run limma here easily, so we use a proxy: check if same miRNAs
        #  show high fold-change in inlier subset via simple calculation)

        # Simple proxy: for inliers only, compute mean expression per fluid
        inlier_samples = inliers.index
        inlier_metadata = metadata.loc[inlier_samples]

        fluid_samples = inlier_metadata[inlier_metadata["biofluid"] == fluid].index
        rest_samples = inlier_metadata[inlier_metadata["biofluid"] != fluid].index

        if len(fluid_samples) < 3 or len(rest_samples) < 3:
            concordance_results.append({
                "biofluid": fluid,
                "n_samples_all": len(metadata[metadata["biofluid"] == fluid]),
                "n_samples_inliers": len(fluid_samples),
                "concordance": "Insufficient inlier samples",
            })
            continue

        # Compute mean log2 expression
        fluid_mean = counts[fluid_samples].mean(axis=1)
        rest_mean = counts[rest_samples].mean(axis=1)
        fc_inliers = np.log2((fluid_mean + 1) / (rest_mean + 1))

        # Top 50 by fold-change in inliers
        top50_inliers = set(fc_inliers.nlargest(50).index)

        # Concordance
        overlap = len(top50_all & top50_inliers)
        concordance_pct = (overlap / 50) * 100

        concordance_results.append({
            "biofluid": fluid,
            "n_samples_all": len(metadata[metadata["biofluid"] == fluid]),
            "n_samples_inliers": len(fluid_samples),
            "top50_all": len(top50_all),
            "top50_inliers": len(top50_inliers),
            "overlap": overlap,
            "concordance_pct": concordance_pct,
        })

        print(f"  {fluid}: {overlap}/50 overlap ({concordance_pct:.1f}%) between all-samples and inliers-only")

    concordance_df = pd.DataFrame(concordance_results)
    concordance_df.to_csv(OUT_DIR / "de_concordance_analysis.tsv", sep="\t", index=False)

    return concordance_df


def generate_decision_matrix(outliers: pd.DataFrame, inliers: pd.DataFrame, pca_coords: pd.DataFrame, metadata: pd.DataFrame):
    """Generate decision matrix for outlier retention/exclusion."""
    print("\nGenerating decision matrix...")

    # Compute silhouette scores
    silhouette_all = assess_biofluid_clustering(pca_coords, metadata, "all")
    silhouette_inliers = assess_biofluid_clustering(pca_coords, inliers, "inliers")
    silhouette_outliers = assess_biofluid_clustering(pca_coords, outliers, "outliers")

    # Decision criteria
    criteria = {
        "n_outliers": len(outliers),
        "pct_outliers": len(outliers) / len(metadata) * 100,
        "silhouette_all_samples": silhouette_all,
        "silhouette_inliers_only": silhouette_inliers,
        "silhouette_outliers_only": silhouette_outliers,
        "outlier_biofluids": outliers["biofluid"].value_counts().to_dict() if len(outliers) > 0 else {},
    }

    # Decision logic
    if len(outliers) == 0:
        decision = "KEEP ALL - No outliers detected"
        recommendation = "Proceed with full dataset"
    elif silhouette_outliers is not None and silhouette_outliers > 0.3:
        decision = "KEEP OUTLIERS - Outliers cluster by biofluid"
        recommendation = "Outliers represent degraded but valid samples. KEEP for robustness testing. Markers validated on this subset are forensically robust."
    elif silhouette_outliers is not None and silhouette_outliers < 0.1:
        decision = "EXCLUDE OUTLIERS - Outliers scatter randomly"
        recommendation = "Outliers show poor biofluid clustering (technical failures). Safe to exclude from primary analysis. Run sensitivity check."
    else:
        decision = "STRATIFIED ANALYSIS - Mixed quality"
        recommendation = "Report markers in tiers: Tier 1 (significant with outliers), Tier 2 (significant without outliers). Document robustness."

    criteria["decision"] = decision
    criteria["recommendation"] = recommendation

    # Save decision matrix
    with open(OUT_DIR / "decision_matrix.json", "w") as f:
        json.dump(criteria, f, indent=2)

    print(f"\n  Decision: {decision}")
    print(f"  Recommendation: {recommendation}")

    return criteria


def generate_report(outliers: pd.DataFrame, inliers: pd.DataFrame, concordance_df: pd.DataFrame, decision: Dict):
    """Generate markdown report."""
    report = f"""# LLAUR Outlier Interrogation Report

**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
**Dataset**: EXR-LLAUR1AVB5CS-AN (Diverse biofluid isolation methods)
**Analysis**: Robustness assessment for forensic marker validation

---

## Executive Summary

**Total samples**: {len(outliers) + len(inliers)}
**Outliers identified**: {len(outliers)} ({len(outliers)/(len(outliers)+len(inliers))*100:.1f}%)
**Outlier criteria**: TMM factor <{TMM_LOW_THRESHOLD} or >{TMM_HIGH_THRESHOLD}, OR library size <{LIBRARY_SIZE_MIN}

**Decision**: {decision['decision']}

**Recommendation**: {decision['recommendation']}

---

## Outlier Characterization

### By Biofluid
"""

    if len(outliers) > 0:
        for fluid, count in outliers["biofluid"].value_counts().items():
            report += f"- **{fluid}**: {count} outliers\n"
    else:
        report += "- No outliers detected\n"

    # Format silhouette scores
    sil_all = decision.get('silhouette_all_samples')
    sil_inliers = decision.get('silhouette_inliers_only')
    sil_outliers = decision.get('silhouette_outliers_only')

    sil_all_str = f"{sil_all:.3f}" if sil_all is not None else "N/A"
    sil_inliers_str = f"{sil_inliers:.3f}" if sil_inliers is not None else "N/A"
    sil_outliers_str = f"{sil_outliers:.3f}" if sil_outliers is not None else "N/A"

    report += f"""

### Clustering Metrics (Silhouette Score)
- **All samples**: {sil_all_str}
- **Inliers only**: {sil_inliers_str}
- **Outliers only**: {sil_outliers_str}

**Interpretation**:
- Silhouette > 0.5: Strong biofluid separation (outliers are valid)
- Silhouette 0.3-0.5: Moderate separation (mixed quality)
- Silhouette < 0.3: Weak/no separation (likely technical failures)

---

## Differential Expression Concordance

Overlap between top 50 upregulated markers (all samples) vs. inliers-only:

"""

    for _, row in concordance_df.iterrows():
        report += f"- **{row['biofluid']}**: {row.get('overlap', 'N/A')}/50 ({row.get('concordance_pct', 0):.1f}% concordance)\n"

    report += f"""

**Interpretation**:
- >80% concordance: Markers are robust to outliers (Tier 1)
- 60-80%: Moderate sensitivity to quality (Tier 2)
- <60%: Quality-dependent markers (exclude or document)

---

## Forensic Implications

### If Outliers Cluster by Biofluid (Keep Them):
Crime scene samples will be degraded, diluted, or protocol-variable. Outliers that still cluster correctly represent **real-world forensic conditions**. Markers validated on this subset are:
- More likely to survive Daubert challenges
- Defensible under cross-examination ("tested on degraded samples")
- Deployable for field use

**Action**: Keep outliers. Report markers as "Tier 1 (robust)" if significant with outliers included.

### If Outliers Scatter Randomly (Exclude Them):
Random scatter indicates technical failure (failed library prep, contamination). These samples add noise without biological signal.

**Action**: Exclude from primary analysis. Document exclusion rationale. Run sensitivity analysis to confirm marker stability.

---

## Next Steps

1. **Review PCA plots** (`pca_outliers_highlighted.png`): Do outliers cluster by biofluid or scatter?
2. **Check isolation method** (if outliers cluster by method): Document as protocol-dependent, but keep for robustness.
3. **Stratified validation**: Run LODO with/without outliers to quantify marker robustness.
4. **Update harmonization plan**: If keeping outliers, ensure batch correction doesn't over-correct biological variability.

---

## Files Generated

- `outlier_characteristics.png/pdf` - Distribution of TMM factors, library sizes, biofluids
- `pca_outliers_highlighted.png/pdf` - PCA with outliers marked
- `outlier_sample_list.tsv` - Full metadata for outlier samples
- `de_concordance_analysis.tsv` - Marker overlap between all vs. inliers-only
- `decision_matrix.json` - Quantitative decision criteria

---

**Analysis script**: `analysis/llaur_outlier_interrogation.py`
**For questions**: See `docs/REPRODUCIBILITY.md` for environment details
"""

    with open(OUT_DIR / "LLAUR_OUTLIER_REPORT.md", "w") as f:
        f.write(report)

    print(f"\n  Saved: LLAUR_OUTLIER_REPORT.md")


def main():
    print("=" * 60)
    print("LLAUR Outlier Interrogation")
    print("=" * 60)

    # Load data
    data = load_llaur_data()

    # Identify outliers
    outliers, inliers = identify_outliers(data)

    # Save outlier list
    outliers.to_csv(OUT_DIR / "outlier_sample_list.tsv", sep="\t")
    inliers.to_csv(OUT_DIR / "inlier_sample_list.tsv", sep="\t")
    print(f"\n  Saved: outlier_sample_list.tsv, inlier_sample_list.tsv")

    # Generate plots
    plot_outlier_characteristics(outliers, inliers)
    plot_pca_with_outliers(data["pca_coords"], outliers, inliers)

    # Assess clustering
    decision = generate_decision_matrix(outliers, inliers, data["pca_coords"], data["metadata"])

    # Compare DE concordance
    concordance_df = compare_de_concordance(data["counts"], data["metadata"], outliers, inliers)

    # Generate report
    generate_report(outliers, inliers, concordance_df, decision)

    print("\n" + "=" * 60)
    print(f"Analysis complete. Results saved to: {OUT_DIR}/")
    print(f"\nKey decision: {decision['decision']}")
    print(f"Recommendation: {decision['recommendation']}")
    print("=" * 60)


if __name__ == "__main__":
    main()