#!/usr/bin/env python3
"""Apply CPM and variance-based feature filters to each manual exRNA cohort.

For every dataset under results/derived/<EXR-ID>/ this script:
    1. Recomputes CPM and log2(CPM+1).
    2. Retains miRNAs with CPM >= 1 in at least 20% of samples.
    3. Drops near-zero variance features (log2 CPM variance < 0.01).
    4. Writes filtered counts/CPM/log2 tables and a summary JSON report.

Outputs are stored in results/derived/<EXR-ID>/filtered/ along with a
feature_filter_summary.json capturing counts before/after filtering.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "derived"

MIN_CPM = 1.0
MIN_PROP = 0.20
MIN_LOGVAR = 0.01


@dataclass
class DatasetPaths:
    dataset_id: str
    counts_path: Path
    metadata_path: Path

    def out_dir(self) -> Path:
        out = RESULTS / self.dataset_id / "filtered"
        out.mkdir(parents=True, exist_ok=True)
        return out


def load_counts(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t", index_col=0)


def compute_cpm(counts: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    lib_sizes = counts.sum(axis=0)
    lib_sizes = lib_sizes.replace(0, np.nan)
    cpm = counts.divide(lib_sizes, axis=1) * 1_000_000.0
    cpm = cpm.fillna(0.0)
    return cpm, lib_sizes


def filter_features(dataset: DatasetPaths) -> Dict[str, int]:
    counts = load_counts(dataset.counts_path)
    cpm, lib_sizes = compute_cpm(counts)
    log2_cpm = np.log2(cpm + 1.0)

    n_samples = counts.shape[1]
    min_detect = int(np.ceil(MIN_PROP * n_samples))

    detect_mask = (cpm >= MIN_CPM).sum(axis=1) >= min_detect
    var_mask = log2_cpm.var(axis=1) >= MIN_LOGVAR
    combined_mask = detect_mask & var_mask

    filtered_counts = counts.loc[combined_mask]
    filtered_cpm = cpm.loc[combined_mask]
    filtered_log2 = log2_cpm.loc[combined_mask]

    out_dir = dataset.out_dir()
    filtered_counts.to_csv(out_dir / "miRNA_counts.filtered.tsv", sep="\t")
    filtered_cpm.to_csv(out_dir / "miRNA_cpm.filtered.tsv", sep="\t", float_format="%.6f")
    filtered_log2.to_csv(out_dir / "miRNA_log2cpm.filtered.tsv", sep="\t", float_format="%.6f")

    summary = {
        "dataset_id": dataset.dataset_id,
        "min_cpm": MIN_CPM,
        "min_detect_samples": int(min_detect),
        "min_detect_fraction": MIN_PROP,
        "min_log2_variance": MIN_LOGVAR,
        "n_features_initial": int(counts.shape[0]),
        "n_features_detect": int(detect_mask.sum()),
        "n_features_variance": int(var_mask.sum()),
        "n_features_filtered": int(filtered_counts.shape[0]),
        "n_samples": int(n_samples),
    }

    (out_dir / "feature_filter_summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def main() -> None:
    dataset_configs = [
        DatasetPaths(
            dataset_id="EXR-KJENS1RID1-AN",
            counts_path=RESULTS / "EXR-KJENS1RID1-AN" / "miRNA_counts.tsv",
            metadata_path=RESULTS / "EXR-KJENS1RID1-AN" / "sample_metadata.tsv",
        ),
        DatasetPaths(
            dataset_id="EXR-TTUSC1gCrGDH-AN",
            counts_path=RESULTS / "EXR-TTUSC1gCrGDH-AN" / "miRNA_counts.tsv",
            metadata_path=RESULTS / "EXR-TTUSC1gCrGDH-AN" / "sample_metadata.tsv",
        ),
        DatasetPaths(
            dataset_id="EXR-LLAUR1AVB5CS-AN",
            counts_path=RESULTS / "EXR-LLAUR1AVB5CS-AN" / "miRNA_counts.tsv",
            metadata_path=RESULTS / "EXR-LLAUR1AVB5CS-AN" / "sample_metadata.tsv",
        ),
    ]

    summaries = [filter_features(cfg) for cfg in dataset_configs]

    summary_path = RESULTS / "feature_filter_summary.json"
    summary_path.write_text(json.dumps({item["dataset_id"]: item for item in summaries}, indent=2))


if __name__ == "__main__":
    main()
