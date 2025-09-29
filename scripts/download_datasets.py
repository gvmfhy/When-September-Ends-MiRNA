#!/usr/bin/env python3
"""Download publicly accessible datasets listed in config/dataset_manifest.csv."""

from __future__ import annotations

import csv
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SKIPPED_ACCESS_LEVELS = {"registration_portal", "registration_dataset", "controlled_access"}
SKIPPED_FILE_TYPES = {"portal", "html"}


def main() -> None:
    target_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data")
    raw_dir = target_root / "raw"
    proc_dir = target_root / "processed"
    meta_dir = target_root / "meta"

    for directory in (raw_dir, proc_dir, meta_dir):
        directory.mkdir(parents=True, exist_ok=True)

    manifest_path = Path("config") / "dataset_manifest.csv"
    if not manifest_path.exists():
        raise SystemExit(f"Manifest not found at {manifest_path}")

    with manifest_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            dataset = row["dataset_id"].strip()
            url = row["download_url"].strip()
            access_level = row["access_level"].strip()
            file_type = row["file_type"].strip()

            if access_level in SKIPPED_ACCESS_LEVELS or file_type in SKIPPED_FILE_TYPES:
                print(f"[skip   ] {dataset}: manual download required ({access_level})")
                continue

            if not url.startswith("http"):
                print(f"[skip   ] {dataset}: unsupported URL {url}")
                continue

            filename = infer_filename(url, dataset)
            destination = determine_destination(filename, raw_dir, proc_dir, meta_dir)

            if destination.exists():
                print(f"[cached ] {destination.relative_to(target_root)}")
                continue

            print(f"[fetch  ] {dataset} -> {destination.relative_to(target_root)}")
            download(url, destination)


def infer_filename(url: str, dataset: str) -> str:
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    if "file" in query:
        return query["file"][0]
    name = Path(parsed.path).name or dataset
    return name


def determine_destination(filename: str, raw_dir: Path, proc_dir: Path, meta_dir: Path) -> Path:
    lower_name = filename.lower()
    if "raw" in lower_name or lower_name.endswith(".tar"):
        dest_dir = raw_dir
    elif "series_matrix" in lower_name and not lower_name.startswith("gse85830_mir"):
        dest_dir = meta_dir
    else:
        dest_dir = proc_dir
    return dest_dir / filename


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as response, destination.open("wb") as handle:
        handle.write(response.read())


if __name__ == "__main__":
    main()
