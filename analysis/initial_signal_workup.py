#!/usr/bin/env python3
"""Prepare initial harmonized count matrices and metadata for manual exRNA cohorts.

Steps:
    1. Load exceRpt miRNA read-count tables for KJENS, TTUSC, and LLAUR cohorts.
    2. Derive simple sample metadata (dataset ID, inferred biofluid, QC metrics).
    3. Compute per-sample library sizes, CPM, and log2(CPM+1) matrices.
    4. Export dataset-specific artefacts plus an intersection matrix spanning shared miRNAs.

This script is meant as the first pass to separate signal from noise before
running more sophisticated modelling. It keeps all derived artefacts under
`results/derived/` to preserve provenance of raw downloads stored elsewhere.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / "tmp" / "exrna_manual"
RESULTS = ROOT / "results" / "derived"


def read_counts_table(path: Path) -> pd.DataFrame:
    """Load a tab-delimited exceRpt matrix with miRNAs as rows."""
    import csv

    with path.open() as fh:
        reader = csv.reader(fh, delimiter="\t")
        header = next(reader)
        if not header or header[0] != "":
            # Some files may omit the leading empty cell; handle gracefully
            sample_ids = header[1:] if header else []
        else:
            sample_ids = header[1:]
        data = []
        gene_ids = []
        for row in reader:
            if not row:
                continue
            gene_ids.append(row[0].strip())
            numeric = [float(x) if x else 0.0 for x in row[1:]]
            data.append(numeric)
    array = np.array(data, dtype=float)
    df = pd.DataFrame(array, index=gene_ids, columns=[s.strip() for s in sample_ids])
    return df


def compute_cpm(counts: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Return CPM-normalised matrix and per-sample library sizes."""
    lib_sizes = counts.sum(axis=0)
    # Avoid division by zero by replacing zeros with nan then fill later
    lib_sizes = lib_sizes.replace(0, np.nan)
    cpm = counts.divide(lib_sizes, axis=1) * 1_000_000.0
    cpm = cpm.fillna(0.0)
    return cpm, lib_sizes


def log2_cpm(cpm: pd.DataFrame, pseudocount: float = 1.0) -> pd.DataFrame:
    return np.log2(cpm + pseudocount)


@dataclass
class DatasetConfig:
    dataset_id: str
    counts_path: Path
    read_mapping_path: Path | None = None
    sample_metadata_path: Path | None = None

    def dataset_dir(self) -> Path:
        out_dir = RESULTS / self.dataset_id
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir


def infer_fluid_kjens(sample_id: str) -> str:
    if "_Sample_B_" in sample_id:
        return "Plasma"
    if "_Sample_S_" in sample_id:
        return "Saliva"
    if "_Sample_U_" in sample_id:
        return "Urine"
    return "Unknown"


def infer_fluid_ttusc(sample_id: str) -> str:
    tokens = sample_id.split("_")
    for token in tokens:
        norm = token.lower()
        if norm in {"plasma", "serum", "saliva", "urine"}:
            return token.capitalize()
    return "Unknown"


def load_read_mapping_metrics(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t", index_col=0)
    df.index = df.index.astype(str).str.strip()
    return df


def load_llaur_metadata(path: Path) -> pd.DataFrame:
    columns = [
        "metadata_filename",
        "metadata_url",
        "sample_name",
        "disease_type",
        "biofluid",
        "biomaterial",
        "isolation_method",
        "anatomical_site",
        "disease_detail",
        "assay",
        "organism",
        "qc_status",
        "input_reads",
        "aligned_reads",
        "mapping_ratio",
        "biosample_id",
        "analysis_id",
        "sample_id",
    ]
    df = pd.read_csv(path, sep="\t", names=columns, comment="#", header=None)
    df = df.dropna(subset=["sample_id"])  # defensive trimming
    df["sample_id"] = df["sample_id"].astype(str).str.strip()
    return df


def build_metadata(config: DatasetConfig, counts: pd.DataFrame) -> pd.DataFrame:
    dataset = config.dataset_id
    sample_ids = counts.columns

    records = []

    read_map_df = None
    if config.read_mapping_path and config.read_mapping_path.exists():
        read_map_df = load_read_mapping_metrics(config.read_mapping_path)

    meta_df = None
    if config.sample_metadata_path and config.sample_metadata_path.exists():
        meta_df = load_llaur_metadata(config.sample_metadata_path)

    for sample in sample_ids:
        record: Dict[str, object] = {
            "dataset_id": dataset,
            "sample_id": sample,
            "library_size": float(counts[sample].sum()),
        }

        if dataset == "EXR-KJENS1RID1-AN":
            record["biofluid"] = infer_fluid_kjens(sample)
        elif dataset == "EXR-TTUSC1gCrGDH-AN":
            record["biofluid"] = infer_fluid_ttusc(sample)
        elif dataset == "EXR-LLAUR1AVB5CS-AN":
            if meta_df is not None:
                match = meta_df.loc[meta_df["sample_id"] == sample]
                if not match.empty:
                    record["biofluid"] = match.iloc[0]["biofluid"]
                    record["qc_status"] = match.iloc[0]["qc_status"]
                    record["isolation_method"] = match.iloc[0]["isolation_method"]
                else:
                    record["biofluid"] = "Unknown"
            else:
                record["biofluid"] = "Unknown"
        else:
            record["biofluid"] = "Unknown"

        if read_map_df is not None and sample in read_map_df.index:
            row = read_map_df.loc[sample]
            record["reads_used_for_alignment"] = float(row.get("reads_used_for_alignment", np.nan))
            record["miRNA_sense_counts"] = float(row.get("miRNA_sense", np.nan))
            record["low_miRNA_flag"] = bool(row.get("miRNA_sense", 0) < 100_000)
        else:
            record["reads_used_for_alignment"] = math.nan
            record["miRNA_sense_counts"] = math.nan
            record["low_miRNA_flag"] = False

        records.append(record)

    metadata = pd.DataFrame.from_records(records)
    metadata.set_index("sample_id", inplace=True)

    # For LLAUR, derive low_miRNA_flag from library size if read mapping absent
    if dataset == "EXR-LLAUR1AVB5CS-AN":
        metadata["low_miRNA_flag"] = metadata["library_size"] < 100_000

    return metadata


def export_dataset_artifacts(config: DatasetConfig) -> Dict[str, object]:
    dataset_id = config.dataset_id
    counts = read_counts_table(config.counts_path)
    cpm, lib_sizes = compute_cpm(counts)
    log_cpm = log2_cpm(cpm)

    metadata = build_metadata(config, counts)

    out_dir = config.dataset_dir()
    counts.to_csv(out_dir / "miRNA_counts.tsv", sep="\t")
    cpm.to_csv(out_dir / "miRNA_cpm.tsv", sep="\t", float_format="%.6f")
    log_cpm.to_csv(out_dir / "miRNA_log2cpm.tsv", sep="\t", float_format="%.6f")
    metadata.to_csv(out_dir / "sample_metadata.tsv", sep="\t")

    stats = {
        "n_miRNA": int(counts.shape[0]),
        "n_samples": int(counts.shape[1]),
        "median_library_size": float(metadata["library_size"].median()),
        "median_log2_cpm": float(log_cpm.stack().median()),
        "n_low_miRNA": int(metadata["low_miRNA_flag"].sum()),
    }
    return {
        "dataset_id": dataset_id,
        "stats": stats,
        "counts": counts,
        "log2_cpm": log_cpm,
        "metadata": metadata,
    }


def compute_intersection(matrices: Iterable[pd.DataFrame]) -> pd.Index:
    shared = None
    for df in matrices:
        genes = df.index
        shared = genes if shared is None else shared.intersection(genes)
    return shared if shared is not None else pd.Index([])


def main() -> None:
    configs = [
        DatasetConfig(
            dataset_id="EXR-KJENS1RID1-AN",
            counts_path=TMP
            / "EXR-KJENS1RID1-AN"
            / "selected"
            / "KJENS1-RIDProject-2016-06-27_exceRpt_miRNA_ReadCounts.txt",
            read_mapping_path=TMP
            / "EXR-KJENS1RID1-AN"
            / "KJENS1-RIDProject-2016-06-27_exceRpt_readMappingSummary.txt",
        ),
        DatasetConfig(
            dataset_id="EXR-TTUSC1gCrGDH-AN",
            counts_path=TMP
            / "EXR-TTUSC1gCrGDH-AN"
            / "selected"
            / "TTUSC1-U19_normal_controls-2017-09-26_exceRpt_miRNA_ReadCounts.txt",
            read_mapping_path=TMP
            / "EXR-TTUSC1gCrGDH-AN"
            / "TTUSC1-U19_normal_controls-2017-09-26_exceRpt_readMappingSummary.txt",
        ),
        DatasetConfig(
            dataset_id="EXR-LLAUR1AVB5CS-AN",
            counts_path=TMP
            / "EXR-LLAUR1AVB5CS-AN"
            / "selected"
            / "LLAUR01-RNAIsoBiofluidPool-2023-08-21_exceRpt_miRNA_ReadCounts.txt",
            sample_metadata_path=TMP
            / "EXR-LLAUR1AVB5CS-AN"
            / "selected"
            / "exRNA_Atlas_Biosample_Metadata_Downloads_Mon-Sep-29-2025-18_19_25-GMT-0400-_Eastern-Daylight-Time_.tsv",
        ),
    ]

    dataset_outputs = []
    for config in configs:
        summary = export_dataset_artifacts(config)
        dataset_outputs.append(summary)

    shared_genes = compute_intersection([item["log2_cpm"] for item in dataset_outputs])

    combined_log2cpm = []
    combined_metadata = []
    for item in dataset_outputs:
        log_matrix = item["log2_cpm"].loc[shared_genes]
        metadata = item["metadata"].copy()
        metadata["dataset_id"] = item["dataset_id"]
        combined_log2cpm.append(log_matrix)
        combined_metadata.append(metadata)

    union_matrix = pd.concat(combined_log2cpm, axis=1)
    union_metadata = pd.concat(combined_metadata, axis=0)

    harmon_dir = RESULTS / "harmonized"
    harmon_dir.mkdir(exist_ok=True)
    union_matrix.to_csv(harmon_dir / "log2_cpm_intersection.tsv", sep="\t", float_format="%.6f")
    union_metadata.to_csv(harmon_dir / "sample_metadata.tsv", sep="\t")

    summary_payload = {
        "shared_miRNA": int(len(shared_genes)),
        "datasets": [
        {
            "dataset_id": item["dataset_id"],
            **item["stats"],
        }
        for item in dataset_outputs
    ],
    }
    (harmon_dir / "summary.json").write_text(json.dumps(summary_payload, indent=2))


if __name__ == "__main__":
    main()
