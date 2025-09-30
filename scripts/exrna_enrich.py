#!/usr/bin/env python3
"""Enrich the exRNA Atlas catalog with fluid-level metadata.

This script expects that you have an authenticated session cookie for the
exRNA Atlas portal. Copy the `Cookie` header from an authenticated browser
session and expose it as the environment variable `EXRNA_COOKIE` before
running the script.

Usage
-----
    EXRNA_COOKIE="..." python scripts/exrna_enrich.py \
        --catalog config/exrna_atlas_catalog.csv \
        --output config/exrna_atlas_catalog_enriched.csv \
        --metadata-dir data/meta/exrna_atlas

It will:
  * fetch the CSRF token from the datasets page,
  * retrieve the Analysis document for each dataset to obtain biosample IDs,
  * request biosample metadata for those IDs (biofluid, disease, etc.),
  * summarise fluids and diseases per dataset, and
  * write both an enriched catalog CSV and per-dataset metadata JSON
    artefacts under the chosen metadata directory.

The script avoids downloading raw RNA files; it only collects metadata so that
subsequent download tooling can make informed decisions.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import requests

BASE_URL = "https://exrna-atlas.org/genboreeKB"
PROJECT_ID = "extracellular-rna-atlas-v2"
ANALYSES_COLL = "Analyses"

DATASET_PAGE = f"{BASE_URL}/projects/{PROJECT_ID}/exat/datasets"
DOC_ENDPOINT = f"{BASE_URL}/projects/{PROJECT_ID}/exat/doc"
BIOSAMPLE_METADATA_ENDPOINT = f"{BASE_URL}/projects/{PROJECT_ID}/exat/biosampleMetadata"
QC_ENDPOINT = f"{BASE_URL}/projects/{PROJECT_ID}/exat/qcMetrics"
FASTQ_ENDPOINT = f"{BASE_URL}/projects/{PROJECT_ID}/exat/fastqAndDb"

CSRF_META_RE = re.compile(r'<meta[^>]+name="csrf-token"[^>]+content="([^"]+)"', re.I)


class ExRNAClient:
    def __init__(self, session_cookie: str, throttle: float = 0.4) -> None:
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "mirna-assay/0.1 (+github.com/exrna)",
            "Cookie": session_cookie,
            "Accept": "application/json, text/javascript, */*; q=0.1",
        })
        self.csrf_token = None
        self.throttle = throttle

    def ensure_csrf(self) -> str:
        if self.csrf_token:
            return self.csrf_token
        resp = self.session.get(DATASET_PAGE)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to load datasets page (status {resp.status_code})")
        match = CSRF_META_RE.search(resp.text)
        if not match:
            raise RuntimeError("Unable to locate csrf-token meta tag; ensure the cookie is valid")
        self.csrf_token = match.group(1)
        return self.csrf_token

    def get_analysis_doc(self, dataset_id: str) -> Dict[str, Any]:
        token = self.ensure_csrf()
        params = {
            "coll": ANALYSES_COLL,
            "docId": dataset_id,
            "authenticity_token": token,
        }
        resp = self.session.get(DOC_ENDPOINT, params=params)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch analysis doc for {dataset_id} (status {resp.status_code})")
        return resp.json()

    def get_biosample_metadata(self, biosample_ids: Iterable[str]) -> Dict[str, Dict[str, List[str]]]:
        ids = ",".join(biosample_ids)
        if not ids:
            return {}
        token = self.ensure_csrf()
        data = {
            "biosampleIDs": ids,
            "authenticity_token": token,
        }
        resp = self.session.post(BIOSAMPLE_METADATA_ENDPOINT, data=data)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch biosample metadata (status {resp.status_code})")
        return resp.json()

    def get_qc_metrics(self, biosample_ids: Iterable[str]) -> Dict[str, Dict[str, Any]]:
        ids = ",".join(biosample_ids)
        if not ids:
            return {}
        token = self.ensure_csrf()
        data = {
            "biosampleIDs": ids,
            "authenticity_token": token,
        }
        resp = self.session.post(QC_ENDPOINT, data=data)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch QC metrics (status {resp.status_code})")
        return resp.json()

    def get_fastq_db(self, biosample_ids: Iterable[str]) -> Dict[str, Any]:
        ids = ",".join(biosample_ids)
        if not ids:
            return {}
        token = self.ensure_csrf()
        data = {
            "biosampleIDs": ids,
            "authenticity_token": token,
        }
        resp = self.session.post(FASTQ_ENDPOINT, data=data)
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to fetch FASTQ metadata (status {resp.status_code})")
        return resp.json().get("fastqDb", {})

    def sleep(self) -> None:
        if self.throttle:
            time.sleep(self.throttle)


def extract_biosample_ids(analysis_doc: Dict[str, Any]) -> Tuple[List[str], str]:
    try:
        props = analysis_doc["Analysis"]["properties"]["Data Analysis Level"]["properties"]["Type"]["properties"]
    except KeyError as exc:
        raise RuntimeError(f"Unexpected analysis doc structure: missing {exc}")

    for level_key in (
        "Level 1 Reference Alignment",
        "Level 1 Alignment",
        "qPCR Data Analysis Level",
        "qPCR Data Analysis",
    ):
        if level_key in props:
            items = props[level_key]["properties"]["Biosamples"]["items"]
            biosample_ids = [item["Biosample ID"]["value"] for item in items if "Biosample ID" in item]
            return biosample_ids, level_key
    raise RuntimeError("Could not locate biosample list in analysis document")


def normalise_values(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    return [str(value).strip()]


def summarise_metadata(metadata: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
    fluid_counter: Counter[str] = Counter()
    disease_counter: Counter[str] = Counter()
    assay_counter: Counter[str] = Counter()
    location_counter: Counter[str] = Counter()
    exceRpt_ids: List[str] = []

    for biosample_id, fields in metadata.items():
        for fluid in normalise_values(fields.get("Biofluid Name")):
            fluid_counter[fluid] += 1
        for disease in normalise_values(fields.get("Disease Type")):
            disease_counter[disease] += 1
        for assay in normalise_values(fields.get("Profiling Assay")):
            assay_counter[assay] += 1
        for loc in normalise_values(fields.get("Anatomical Location")):
            location_counter[loc] += 1
        exceRpt_values = normalise_values(fields.get("exceRpt Identifier"))
        exceRpt_ids.extend(exceRpt_values)

    summary = {
        "fluids": sorted(fluid_counter),
        "counts_by_fluid": fluid_counter,
        "diseases": sorted([d for d in disease_counter if d and d.lower() != "not applicable"]),
        "profiling_assays": sorted(assay_counter),
        "locations": sorted(location_counter),
        "exceRpt_ids": sorted(set(exceRpt_ids)),
    }
    return summary


def write_metadata_file(directory: Path, dataset_id: str, payload: Dict[str, Any]) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{dataset_id}_metadata.json"
    target.write_text(json.dumps(payload, indent=2))
    return target


def load_catalog(path: Path) -> List[Dict[str, str]]:
    with path.open() as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    return rows


def dump_catalog(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich exRNA Atlas catalog with fluid metadata")
    parser.add_argument("--catalog", type=Path, default=Path("config/exrna_atlas_catalog.csv"),
                        help="Input catalog CSV (default: config/exrna_atlas_catalog.csv)")
    parser.add_argument("--output", type=Path, default=Path("config/exrna_atlas_catalog_enriched.csv"),
                        help="Output CSV for enriched catalog")
    parser.add_argument("--metadata-dir", type=Path, default=Path("data/meta/exrna_atlas"),
                        help="Directory to store per-dataset metadata snapshots")
    parser.add_argument("--throttle", type=float, default=0.4,
                        help="Delay between API calls in seconds (default: 0.4)")
    args = parser.parse_args()

    cookie = os.getenv("EXRNA_COOKIE")
    if not cookie:
        print("ERROR: EXRNA_COOKIE environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = ExRNAClient(cookie, throttle=args.throttle)

    catalog_rows = load_catalog(args.catalog)
    enriched_rows: List[Dict[str, Any]] = []

    for row in catalog_rows:
        dataset_id = row.get("exrna_id")
        if not dataset_id:
            enriched_rows.append(row)
            continue
        print(f"Processing {dataset_id}…", file=sys.stderr)
        try:
            analysis_doc = client.get_analysis_doc(dataset_id)
            biosample_ids, level_key = extract_biosample_ids(analysis_doc)
            if not biosample_ids:
                print(f"  No biosamples found for {dataset_id}; skipping", file=sys.stderr)
                row.update({
                    "fluids": "",
                    "counts_by_fluid": "",
                    "diseases": "",
                    "metadata_file": "",
                    "exceRpt_ids": "",
                    "biosample_ids": "",
                    "analysis_level": level_key,
                })
                enriched_rows.append(row)
                client.sleep()
                continue
            metadata = client.get_biosample_metadata(biosample_ids)
            summary = summarise_metadata(metadata)
            payload = {
                "dataset_id": dataset_id,
                "analysis_level": level_key,
                "biosample_ids": biosample_ids,
                "metadata": metadata,
                "summary": summary,
            }
            metadata_path = write_metadata_file(args.metadata_dir, dataset_id, payload)

            row.update({
                "analysis_level": level_key,
                "biosample_ids": ";".join(biosample_ids),
                "fluids": ";".join(summary["fluids"]),
                "counts_by_fluid": json.dumps(summary["counts_by_fluid"], separators=(",", ":")),
                "diseases": ";".join(summary["diseases"]),
                "exceRpt_ids": ";".join(summary["exceRpt_ids"]),
                "metadata_file": str(metadata_path),
            })
        except Exception as exc:  # noqa: BLE001
            print(f"  ERROR for {dataset_id}: {exc}", file=sys.stderr)
            row.setdefault("analysis_level", "")
            row.setdefault("metadata_file", "")
        enriched_rows.append(row)
        client.sleep()

    dump_catalog(args.output, enriched_rows)
    print(f"Enriched catalog written to {args.output}")


if __name__ == "__main__":
    main()
