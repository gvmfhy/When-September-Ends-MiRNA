# Repository Orientation

Welcome! This project develops a forensic miRNA body-fluid assay. Start with these documents to understand the current state:

- `docs/exrna_dataset_strategy.md` – master log of datasets, processing status, and key findings (QC, harmonization, LODO tiers).
- `docs/HARMONIZATION_GUIDE.md` – step-by-step pipeline for integrating new datasets with provenance requirements.
- `docs/REPRODUCIBILITY.md` – verification protocols, script hashes, and environment details for every analysis stage.
- `results/derived/cross_cohort/HARMONIZATION_SUMMARY.md` – latest ComBat batch correction outcomes and feature intersection stats.
- `results/lodo/LODO_SUMMARY.md` – leave-one-dataset-out performance, fluid tiers (court-ready vs quality-sensitive), and forensic recommendations.

For reproducible re-runs, follow the manifests in each `results/**/reproducibility.json` and use the recorded script MD5 hashes.
