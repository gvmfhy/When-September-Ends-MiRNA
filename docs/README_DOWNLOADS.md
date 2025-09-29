# Dataset Acquisition Guide

This guide explains how to obtain every dataset referenced in `config/dataset_manifest.csv` and how to keep the on-disk layout consistent with the automation scripts.

## Quick Start

1. Ensure you have `curl` (for macOS, it is installed by default) and Python ≥3.9 available.
2. In the project root run either:
   - `make data` (shell script downloader), or
   - `make data-py` (Python downloader).
3. Downloaded files are deposited under:
   - `data/raw/` for archives and other raw payloads.
   - `data/processed/` for submitter-provided expression matrices.
   - `data/meta/` for supplementary metadata (e.g. `series_matrix` files).
4. Optionally run `make untar` to unpack any `*.tar` archives into sibling directories (contents stay alongside the original archive for provenance).

## Public, Scripted Downloads

The automation covers all GEO-hosted artefacts that can be fetched without credentials.

| Accession | Fluids | Files downloaded automatically | Notes |
| --- | --- | --- | --- |
| GSE153135 | peripheral blood, menstrual blood, saliva, semen, vaginal secretion | `GSE153135_series_matrix.txt.gz`, `GSE153135_RAW.tar` | Exiqon miRCURY LNA GPR files within the raw archive.
| GSE49630 | peripheral blood, saliva, semen, vaginal secretion | `GSE49630_series_matrix.txt.gz`, `GSE49630_RAW.tar` | Affymetrix Multispecies miRNA-3 CEL files and RMA-normalised matrix.
| GSE85830 | venous blood, menstrual blood, saliva, semen, vaginal secretion, urine, feces, perspiration | `GSE85830_miR_NGS_read_Data_-_all_32_body_fluids.csv.gz`, `GSE85830_series_matrix.txt.gz` | Processed counts plus metadata for Illumina small RNA-seq study.

The script prints status messages such as `[fetch]`, `[cached]`, or `[skip]`. If a download fails, re-run the command; partial files are overwritten on the next attempt.

## Manual / Credentialed Resources

Some high-value datasets require a login or controlled-access approval. The downloader surfaces them as `[skip]` entries—use the instructions below to retrieve them manually and place them under `data/` using the suggested layout.

- **exRNA Atlas (https://www.exrna-atlas.org/exat/).** Create a free account, filter by fluid (e.g. saliva, urine, plasma), and export the `*.txt` count matrices. Store each export at `data/processed/exrna_atlas/<query_name>.txt` and record filtering parameters in `data/meta/exrna_atlas_<query>.json`.
- **ICPSR study 38391 (https://www.icpsr.umich.edu/web/NACJD/studies/38391).** Register with ICPSR, accept the data-use agreement, and download the dataset bundle (`*.zip`). Extract into `data/processed/ICPSR_38391/` and keep the codebook PDF alongside the CSV files.
- **dbGaP phs001258 (https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id=phs001258.v1.p1).** Requires an NIH eRA Commons account and Data Access Request (DAR). Once approved, use dbGaP's `dbGaPDownload` scripts or `aspera` to place raw data under `data/raw/phs001258/` with the dbGaP-provided encrypted directory structure intact. Document the DAR ID in `data/meta/phs001258_access.txt`.
- **ENA PRJEB83455 microbiome study (https://www.ebi.ac.uk/ena/browser/view/PRJEB83455).** Use the ENA web interface or `enaBrowserTools` to fetch FASTQ files. Position them under `data/raw/PRJEB83455/<run_id>.fastq.gz`.

## Verifying Downloads

- Validate archive integrity with `shasum -a 256 data/raw/<file>` and record the digest in a tracking spreadsheet or `data/meta/checksums.txt`.
- For GEO tarballs, `make untar` extracts into `data/raw/<file_without_tar>/`. After extraction, spot-check the number of files against GEO’s “supplementary files” listing.
- Compressed text tables (`*.txt.gz`, `*.csv.gz`) can be inspected without full decompression using `zcat` or `gzcat`.

## Storage Layout Convention

```
project_root/
├── data/
│   ├── raw/
│   │   ├── GSE153135_RAW.tar
│   │   ├── GSE153135_RAW/
│   │   │   └── *.gpr
│   │   └── ...
│   ├── processed/
│   │   ├── GSE153135_series_matrix.txt.gz
│   │   ├── GSE85830_processed_counts.csv.gz
│   │   └── ...
│   └── meta/
│       ├── GSE85830_series_matrix.txt.gz
│       └── ...
```

This structure keeps immutable source artefacts (`data/raw/`) separate from analysis-ready tables (`data/processed/`). Derived analysis products (QC reports, normalised matrices) should live under a future `results/` or `analysis/` directory, not in `data/`.

## Troubleshooting

- **Firewall/SSL errors:** GEO’s download URLs use HTTPS and should work behind most corporate networks. If `curl` fails with SSL issues, append `-k` (insecure) as a last resort, or prefer the Python script which uses the system certificate store.
- **Interrupted downloads:** Re-run the command; `curl` will resume from scratch. For large downloads, consider adding `--continue-at -` to the `curl` invocation in `scripts/download_datasets.sh`.
- **SRA toolkit missing:** Install via `conda install -c bioconda sra-tools` or Homebrew `brew install sratoolkit` before attempting raw FASTQ retrieval.

Document every manual retrieval in a lab notebook or `data/meta/download_log.md` so that the chain of custody stays intact.
