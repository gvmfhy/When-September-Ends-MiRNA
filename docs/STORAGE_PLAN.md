# Storage and Data Management Plan

A disciplined storage plan is essential for reproducibility, scalability, and forensic defensibility. This document outlines recommended practices for allocating, backing up, and auditing project data.

## Directory Layout (current vs future)

```
project_root/
├── config/
├── data/
│   ├── raw/            # immutable downloaded artefacts (tar, fastq, csv.gz)
│   ├── processed/      # submitter-provided ready-to-use matrices
│   └── meta/           # ancillary metadata, manifests, checksums
├── docs/
├── results/           # (to be created) derived analyses and QC reports
├── scripts/
└── env/               # (optional) environment specifications
```

**Rules:**
- Treat `data/` as read-only once files land. Derived matrices belong in `results/derived/` with clear provenance filenames (`<dataset>_rma_v1.tsv`).
- Never delete or overwrite `data/raw/` artefacts; append new versions with suffixes if updated files are published.
- Keep chain-of-custody notes (who downloaded what, when, using which credentials) inside `data/meta/download_log.md`.

## Storage Media Recommendations

| Data type | Expected size | Recommended location | Notes |
| --- | --- | --- | --- |
| GEO processed tables | 5–50 MB each | Internal SSD (`data/processed/`) | Fast access for analysis; minimal footprint.
| GEO tar archives (arrays) | 50–300 MB each | Internal SSD (`data/raw/`) | Required occasionally; manageable locally.
| Small RNA FASTQ (Illumina) | 1–5 GB per sample | External SSD / NAS mounted at `/Volumes/mirna_raw/` with symlink into `data/raw/` | Use symbolic link `ln -s /Volumes/mirna_raw data/raw/sra_fastq`. Ensure drive is encrypted.
| dbGaP deliveries | Tens of GB | Secure encrypted volume with restricted access | Retain original directory structure for audit.
| Derived results (QC, model outputs) | Variable | Internal SSD `results/` with nightly sync to cloud backup | Use git LFS or DVC for large files if versioning is required.

## Backup Strategy

1. **Primary workspace:** Internal SSD with Time Machine (macOS) or rsync-based daily snapshot to an external drive.
2. **Secondary backup:** Weekly encrypted archive (`tar + gpg`) pushed to a trusted cloud provider or institutional object storage. Exclude controlled-access data unless allowed by the Data Use Agreement.
3. **Checksum verification:** Maintain `data/meta/checksums.txt` updated via `shasum -a 256 <file>` each time a new artefact is added. Verify checksums after every backup restore test.

## Access Control

- Restrict raw data directories with macOS POSIX permissions (`chmod 700`) when containing controlled-access datasets.
- Store credentials (dbGaP keys, ICPSR login tokens) in a password manager, not within the repository.
- Document who has access to each medium (e.g. founder, analyst). For controlled-access datasets log approvals (DAR IDs) and expiration dates.

## Audit and Provenance

- Create `data/meta/download_log.md` with entries: date, dataset ID, downloader initials, command used, checksum.
- For analyses, generate machine-readable provenance (e.g. `results/logs/pipeline_run_YYYYMMDD.json`) capturing software versions, commit hash, random seeds.
- Schedule quarterly audit reviews to ensure outdated intermediate files are archived and sensitive data remains encrypted.

## Capacity Planning

- Track disk usage with `du -sh data/raw data/processed results` before and after large ingestions.
- When approaching 75% capacity on any medium, plan a scale-out action (e.g. procure additional SSD/NAS, migrate old raw datasets to cold storage).

Following this plan keeps the workspace tidy, makes audits painless, and protects sensitive forensic data throughout the project lifecycle.
