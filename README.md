# MicroRNA Forensic Assay Project

This repository houses the end-to-end research workflow for developing a microRNA-based forensic body-fluid identification assay. The project covers dataset acquisition, harmonization, exploratory analysis, and downstream validation planning.

## Structure

- `docs/` – planning and reference material (download instructions, harmonization guide, storage plan, background notes).
- `config/` – machine-readable manifests used by scripts.
- `scripts/` – automation helpers for dataset acquisition and other tooling.
- `data/` – placeholder directories for raw and processed data (`data/raw/` and `data/processed/`).
- `MicroRNA Internal document aug5.docx` – background strategy document supplied by the founder.

## Getting Started

1. Review `docs/README_DOWNLOADS.md` for a walkthrough of the curated public datasets and download workflow.
2. Use the scripts under `scripts/` or the Makefile targets to fetch raw and processed data into the `data/` directory tree.
3. Follow `docs/HARMONIZATION_GUIDE.md` when integrating multiple studies to maintain statistical rigor and chain-of-custody style documentation.

> **Note:** Because this project handles forensic-domain data, keep meticulous records of every transformation, including script versions, command invocations, and environment details.
