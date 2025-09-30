#!/usr/bin/env python3
"""
Cross-Cohort Marker Consensus Analysis

Purpose: Identify miRNAs that are upregulated (logFC > 0, FDR < 0.05) in ≥2 cohorts
         for the same biofluid. These are robust, transferable markers suitable for
         forensic panel development.

Selection Criteria:
  - Upregulated: logFC > 0
  - Significant: adj.P.Val < 0.05 (FDR-corrected)
  - Multi-cohort: Present in ≥2 datasets for the same biofluid
  - Ranking: By mean AUC (descending), then mean logFC (descending)

Output: results/derived/cross_cohort/marker_consensus.tsv
"""

import json
from pathlib import Path

import pandas as pd

# Paths
BASE_DIR = Path("results/derived")
OUT_DIR = BASE_DIR / "cross_cohort"

# Datasets
datasets = {
    "KJENS": "EXR-KJENS1RID1-AN",
    "TTUSC": "EXR-TTUSC1gCrGDH-AN",
    "LLAUR": "EXR-LLAUR1AVB5CS-AN",
}

# Biofluids (matching DE file naming)
biofluids = ["Plasma", "Saliva", "Serum", "Urine"]

print("Loading differential expression results...\n")

# Load all DE results
de_results = {}
for dataset_name, dataset_id in datasets.items():
    de_results[dataset_name] = {}
    de_dir = BASE_DIR / dataset_id / "differential_expression"

    for fluid in biofluids:
        de_file = de_dir / f"de_{fluid}_vs_rest.tsv"
        if de_file.exists():
            df = pd.read_csv(de_file, sep="\t")
            # Filter for upregulated and significant
            df_sig = df[(df["logFC"] > 0) & (df["adj.P.Val"] < 0.05)].copy()
            de_results[dataset_name][fluid] = df_sig
            print(
                f"  {dataset_name}/{fluid}: {len(df_sig)} significant upregulated miRNAs"
            )
        else:
            de_results[dataset_name][fluid] = pd.DataFrame()
            print(f"  {dataset_name}/{fluid}: NOT FOUND")

print("\nFinding consensus markers (present in ≥2 cohorts per biofluid)...\n")

# Build consensus table
consensus_markers = []

for fluid in biofluids:
    print(f"Processing {fluid}...")

    # Collect markers from each dataset
    dataset_markers = {}
    for dataset_name in datasets.keys():
        if fluid in de_results[dataset_name] and not de_results[dataset_name][
            fluid
        ].empty:
            df = de_results[dataset_name][fluid]
            dataset_markers[dataset_name] = df.set_index("miRNA")[
                ["logFC", "AUC", "adj.P.Val"]
            ]

    if len(dataset_markers) < 2:
        print(f"  {fluid}: Only {len(dataset_markers)} dataset(s) available - skipping")
        continue

    # Find miRNAs present in ≥2 datasets
    all_mirnas = set()
    for df in dataset_markers.values():
        all_mirnas.update(df.index)

    for mirna in all_mirnas:
        # Count how many datasets have this miRNA
        present_in = []
        stats = []

        for dataset_name, df in dataset_markers.items():
            if mirna in df.index:
                present_in.append(dataset_name)
                row = df.loc[mirna]
                stats.append(
                    {
                        "dataset": dataset_name,
                        "logFC": row["logFC"],
                        "AUC": row["AUC"],
                        "adj_P_Val": row["adj.P.Val"],
                    }
                )

        if len(present_in) >= 2:
            # Calculate consensus statistics
            mean_logFC = sum(s["logFC"] for s in stats) / len(stats)
            mean_AUC = sum(s["AUC"] for s in stats) / len(stats)
            min_AUC = min(s["AUC"] for s in stats)
            max_adj_P = max(s["adj_P_Val"] for s in stats)

            consensus_markers.append(
                {
                    "miRNA": mirna,
                    "biofluid": fluid,
                    "n_datasets": len(present_in),
                    "datasets": ",".join(present_in),
                    "mean_logFC": mean_logFC,
                    "mean_AUC": mean_AUC,
                    "min_AUC": min_AUC,
                    "max_adj_P_Val": max_adj_P,
                    # Individual dataset values
                    **{
                        f"{ds}_logFC": next(
                            (s["logFC"] for s in stats if s["dataset"] == ds), None
                        )
                        for ds in datasets.keys()
                    },
                    **{
                        f"{ds}_AUC": next(
                            (s["AUC"] for s in stats if s["dataset"] == ds), None
                        )
                        for ds in datasets.keys()
                    },
                }
            )

    print(f"  {fluid}: {sum(1 for m in consensus_markers if m['biofluid'] == fluid)} consensus markers")

# Convert to DataFrame and sort
consensus_df = pd.DataFrame(consensus_markers)

if consensus_df.empty:
    print("\nWARNING: No consensus markers found!")
else:
    # Sort by mean_AUC (descending), then mean_logFC (descending)
    consensus_df = consensus_df.sort_values(
        ["biofluid", "mean_AUC", "mean_logFC"], ascending=[True, False, False]
    )

    # Reorder columns for readability
    col_order = [
        "miRNA",
        "biofluid",
        "n_datasets",
        "datasets",
        "mean_logFC",
        "mean_AUC",
        "min_AUC",
        "max_adj_P_Val",
    ]
    # Add individual dataset columns
    for ds in datasets.keys():
        col_order.extend([f"{ds}_logFC", f"{ds}_AUC"])

    consensus_df = consensus_df[col_order]

    # Save consensus table
    out_file = OUT_DIR / "marker_consensus.tsv"
    consensus_df.to_csv(out_file, sep="\t", index=False, float_format="%.4f")

    print(f"\n{'='*60}")
    print("Consensus Marker Summary")
    print(f"{'='*60}")
    print(f"Total consensus markers: {len(consensus_df)}")
    print("\nBy biofluid:")
    for fluid in biofluids:
        count = (consensus_df["biofluid"] == fluid).sum()
        if count > 0:
            n3 = ((consensus_df["biofluid"] == fluid) & (consensus_df["n_datasets"] == 3)).sum()
            n2 = ((consensus_df["biofluid"] == fluid) & (consensus_df["n_datasets"] == 2)).sum()
            print(f"  {fluid}: {count} markers (3 cohorts: {n3}, 2 cohorts: {n2})")

    # Generate tier assignments based on LODO results
    print(f"\n{'='*60}")
    print("Forensic Tier Assignments")
    print(f"{'='*60}")

    tier_summary = {}

    for fluid in biofluids:
        fluid_markers = consensus_df[consensus_df["biofluid"] == fluid]
        if len(fluid_markers) == 0:
            continue

        # Tier logic based on LODO findings
        if fluid == "Urine":
            tier = "Tier 1 (Court-Ready)"
            rationale = "LODO: 91-97% F1 across all conditions, robust to outliers"
        elif fluid in ["Plasma", "Serum"]:
            tier = "Tier 2 (Quality-Controlled)"
            if fluid == "Serum":
                rationale = "LODO: 88% F1 on clean samples, 23% recall on LLAUR - quality-sensitive"
            else:
                rationale = "LODO: 91-95% recall but 59% precision on LLAUR - over-calls under stress"
        elif fluid == "Saliva":
            tier = "Tier 3 (Insufficient Data)"
            rationale = "LODO: Zero-shot detection failed, only present in KJENS (n=45)"
        else:
            tier = "Unclassified"
            rationale = "Not evaluated in LODO"

        tier_summary[fluid] = {
            "tier": tier,
            "n_markers": len(fluid_markers),
            "rationale": rationale,
            "top_5_markers": fluid_markers.head(5)["miRNA"].tolist(),
        }

        print(f"\n{fluid}: {tier}")
        print(f"  Markers: {len(fluid_markers)}")
        print(f"  Rationale: {rationale}")
        print(f"  Top 5: {', '.join(fluid_markers.head(5)['miRNA'].tolist())}")

    # Save tier summary as JSON
    tier_file = OUT_DIR / "marker_tiers.json"
    tier_json = {
        fluid: {
            "tier": info["tier"],
            "n_markers": int(info["n_markers"]),
            "rationale": info["rationale"],
            "top_5_markers": info["top_5_markers"],
        }
        for fluid, info in tier_summary.items()
    }

    with open(tier_file, "w") as f:
        json.dump(tier_json, f, indent=2)

    # Generate top markers by tier
    print(f"\n{'='*60}")
    print("Recommended Forensic Panels")
    print(f"{'='*60}")

    # Tier 1 panel (Urine)
    tier1 = consensus_df[consensus_df["biofluid"] == "Urine"].head(20)
    if not tier1.empty:
        tier1_file = OUT_DIR / "tier1_panel_urine.tsv"
        tier1.to_csv(tier1_file, sep="\t", index=False, float_format="%.4f")
        print(f"\nTier 1 Panel (Urine - Court-Ready):")
        print(f"  {len(tier1)} markers saved to: {tier1_file.name}")
        print(f"  Mean AUC range: {tier1['mean_AUC'].min():.3f} - {tier1['mean_AUC'].max():.3f}")

    # Tier 2 panel (Plasma + Serum)
    tier2 = consensus_df[
        consensus_df["biofluid"].isin(["Plasma", "Serum"])
    ].head(30)
    if not tier2.empty:
        tier2_file = OUT_DIR / "tier2_panel_plasma_serum.tsv"
        tier2.to_csv(tier2_file, sep="\t", index=False, float_format="%.4f")
        print(f"\nTier 2 Panel (Plasma/Serum - Quality-Controlled):")
        print(f"  {len(tier2)} markers saved to: {tier2_file.name}")
        print(f"  Mean AUC range: {tier2['mean_AUC'].min():.3f} - {tier2['mean_AUC'].max():.3f}")
        print(f"  CAUTION: Serum markers require protocol standardization")

    print(f"\n{'='*60}")
    print(f"Output files saved to: {OUT_DIR}")
    print(f"  - {out_file.name} (full consensus table)")
    print(f"  - marker_tiers.json (tier assignments + rationale)")
    print(f"  - tier1_panel_urine.tsv (top 20 Urine markers)")
    print(f"  - tier2_panel_plasma_serum.tsv (top 30 Plasma/Serum markers)")
    print(f"{'='*60}")

print("\n✓ Consensus marker analysis complete")