# Harmonization Guide for Multi-Dataset microRNA Analysis

This document captures a repeatable strategy for integrating heterogeneous microRNA datasets (microarrays, small RNA sequencing, targeted qPCR) for forensic body-fluid identification. The intent is to balance statistical rigor with assay-traceable record keeping.

## Guiding Principles

- **Preserve provenance.** Treat each dataset as its own "batch" with explicit metadata (platform, lab, sample collection notes). Never overwrite the original files; create derived artefacts under a dedicated `results/` directory with versioned filenames.
- **Normalize within modality.** Perform background correction and normalization separately for each platform before contemplating cross-study integration.
- **Favor meta-analysis over naïve pooling.** Combine evidence across studies through effect sizes or consensus ranking rather than forcing disparate matrices into a single model unless batch correction diagnostics are excellent.
- **Document every transformation.** Record script paths, git commit hashes, software versions, and parameter settings in analysis notebooks or `results/logs/`.

## Dataset-Specific Processing Recipes

### Exiqon miRCURY LNA Arrays (GSE153135)

1. Unpack `*.gpr` files from the raw archive.
2. Use R with `limma::read.maimages` (source = "genepix") to load arrays.
3. Apply normexp background correction followed by within-array `normalizeWithinArrays(method = "loess")`.
4. Perform between-array quantile normalization (`normalizeBetweenArrays(method = "Aquantile")`).
5. Extract `A` values (average log-intensity) and track dye orientation per slide (swap channels when `printorder = -1`).
6. Map probe IDs to miRBase v22 sequences using the Exiqon annotation CSV, reconcile to canonical names (e.g. `hsa-miR-451a-5p`).
7. Collapse duplicate probes by median polish; drop probes lacking confident annotation.
8. Summarize replicate arrays (if pooled) by averaging log-intensities; store within-study variance to avoid inflated precision later.

### Affymetrix Multispecies miRNA-3 Arrays (GSE49630)

1. Use Bioconductor `oligo::read.celfiles` and `rma()` for robust multi-array average normalisation.
2. Convert probe set IDs to miRBase v22 names via the most recent release of `pd.mirna.3.0` annotation or custom mapping tables.
3. Collapse probes mapping to the same mature miRNA by taking the median expression per sample.
4. Evaluate quality using array intensity distributions and principal component analysis (PCA); flag outlier donors for review.

### Illumina Small RNA Sequencing (GSE85830 and future cohorts)

1. When using submitter-provided counts:
   - Import the processed counts table, confirm sample-to-fluid mapping against the series matrix.
   - Filter out miRNAs with counts per million (CPM) < 1 in more than 80% of samples.
   - Apply `edgeR::calcNormFactors` (TMM) and transform with `limma::voom` for RNA-seq compatible linear modeling.
2. For raw FASTQ processing (if needed):
   - Employ a dedicated small RNA pipeline (e.g. [exceRpt](https://github.com/robinfriedrich/exceRpt) as used by the exRNA Consortium).
   - Pin the reference (miRBase release, genome build) and record all trimming/filtering parameters.
   - Export both counts and normalized CPM/TPM tables for downstream use.

### Targeted RT-qPCR Panels (ICPSR 38391)

1. Parse raw Cq values and manufacturer-provided normalization controls.
2. Apply inter-plate calibration if multiple plates were used, using calibrator samples.
3. Convert to `ΔCq` using chosen endogenous controls, and derive `ΔΔCq` relative to a reference fluid where appropriate.
4. Store per-sample QC flags (e.g. amplification efficiency, melt curve anomalies).

## Cross-Study Integration Strategy

1. **Within-study modeling.** For each dataset, fit a linear model or non-parametric test comparing a target fluid against the others (e.g. limma with empirical Bayes moderation for arrays, `edgeR`/`voom` for sequencing, Wilcoxon for small cohorts). Capture:
   - log fold change,
   - standard error or variance estimate,
   - effect size metrics (Cohen's d, AUC),
   - specificity/sensitivity thresholds at practical cut-offs.

2. **Effect size harmonization.** Convert study-specific statistics to a common measure (e.g. standardized mean difference). Use inverse-variance weighting to compute a pooled estimate per miRNA across studies within the same modality.

3. **Cross-modality consensus.** Create modality-specific candidate lists, then intersect or union them according to assay goals:
   - **Core markers:** miRNAs consistently high in one fluid and low elsewhere across *all* modalities.
   - **Supplemental markers:** modality-specific markers retained for redundancy.

4. **Batch correction diagnostics (if pooling matrices).** If you decide to combine normalized matrices:
   - Use `sva::ComBat` with `batch = dataset_id`, `mod = model.matrix(~ fluid_type)`.
   - Inspect PCA/UMAP plots and clustering dendrograms to ensure dataset labels no longer dominate structure.
   - Apply leave-one-dataset-out cross-validation—train on two datasets, test on the held-out one; repeat for each.
   - Abort the pooled approach if performance collapses on held-out datasets.

5. **Reference miRNA selection.** Identify 2–4 miRNAs with minimal variance across all fluids (e.g. housekeeping candidates). Validate stability via geNorm or NormFinder. Reference markers should be platform-specific because amplification and detection chemistry differ.

6. **Decision thresholds.** Translate model outputs into rule-based thresholds (e.g. `ΔCq ≤ -5` for semen marker positivity). Store these thresholds in a controlled document to align with forensic validation practice.

## Quality Control Checklist

- [ ] All samples have complete metadata (donor, fluid label, replicate, prep method).
- [ ] QC metrics (array quality weights, read depth, qPCR efficiency) reviewed and outliers documented.
- [ ] Normalization scripts executed under version control; session info captured (`sessionInfo()` for R, `pip freeze` for Python).
- [ ] Batch effect diagnostics recorded (plots saved under `results/qc/`).
- [ ] Final candidate panel accompanied by confusion matrices, ROC curves, and 95% confidence intervals per fluid.

## Reproducibility Artifacts

Maintain the following artefacts alongside analytical results:

- `results/derived/<dataset>/normalized_matrix.tsv` – normalized expression with explicit column metadata.
- `results/models/<date>_panel_selection.json` – structured record of selected miRNAs, thresholds, performance metrics.
- `results/logs/<timestamp>_analysis.md` – human-readable log referencing script hashes and seeds.
- `env/` or `environment.yml` – environment specification allowing colleagues to recreate the software stack.

Adhering to these steps ensures the analytical groundwork aligns with ISO 17025-style validation expectations and keeps the path to courtroom admissibility clear.
