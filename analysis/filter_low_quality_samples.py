#!/usr/bin/env python3
"""Filter low-quality samples from harmonised matrices based on QC flags.

Inputs:
    - results/derived/harmonized/log2_cpm_intersection.tsv
    - results/derived/harmonized/sample_metadata.tsv

Outputs (under results/derived/harmonized/):
    - log2_cpm_intersection.filtered.tsv
    - sample_metadata.filtered.tsv
    - filter_summary.json

Criteria:
    * drop samples where `low_miRNA_flag` is True (counts < 1e5) unless the
      dataset is LLAUR and the flag is derived.  (LLAUR's low flag also based on library size)
    * drop samples where `qc_status` == 'FAIL'

Also include a CSV of removed samples for traceability.
"""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HARMON_DIR = ROOT / "results" / "derived" / "harmonized"

LOG2_PATH = HARMON_DIR / "log2_cpm_intersection.tsv"
META_PATH = HARMON_DIR / "sample_metadata.tsv"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    expression = pd.read_csv(LOG2_PATH, sep="\t", index_col=0)
    metadata = pd.read_csv(META_PATH, sep="\t", index_col=0)
    return expression, metadata


def apply_filters(expr: pd.DataFrame, meta: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    remove_mask = meta[["low_miRNA_flag"]].copy()
    remove_mask["fail_flag"] = meta.get("qc_status", "PASS").fillna("PASS").str.upper() == "FAIL"
    combined_flag = remove_mask.any(axis=1)

    kept_meta = meta.loc[~combined_flag].copy()
    kept_expr = expr.loc[:, kept_meta.index]
    dropped = meta.loc[combined_flag].copy()
    dropped["low_miRNA_flag"] = remove_mask.loc[combined_flag, "low_miRNA_flag"]
    dropped["fail_flag"] = remove_mask.loc[combined_flag, "fail_flag"]
    return kept_expr, kept_meta, dropped


def main() -> None:
    expr, meta = load_data()
    kept_expr, kept_meta, dropped = apply_filters(expr, meta)

    HARMON_DIR.mkdir(parents=True, exist_ok=True)
    kept_expr.to_csv(HARMON_DIR / "log2_cpm_intersection.filtered.tsv", sep="\t", float_format="%.6f")
    kept_meta.to_csv(HARMON_DIR / "sample_metadata.filtered.tsv", sep="\t")
    dropped.to_csv(HARMON_DIR / "removed_samples.tsv", sep="\t")

    summary = {
        "original_samples": int(meta.shape[0]),
        "kept_samples": int(kept_meta.shape[0]),
        "dropped_samples": int(dropped.shape[0]),
        "dropped_by_dataset": dropped.groupby("dataset_id").size().to_dict(),
    }
    (HARMON_DIR / "filter_summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
