# exRNA Atlas Dataset Strategy

## Current catalog vs. manifest

- `config/exrna_atlas_catalog.csv` is the **exhaustive index** of 92 exRNA Atlas analysis IDs harvested from the portal. It tracks PI, institution, platform, and reported sample counts for every dataset currently visible in Atlas v2.
- `config/dataset_manifest.csv` is the **pipeline backbone**: it lists the data sources for which we have automated download scripts (two GEO microarrays, the eight-fluid RNA-seq cohort, etc.). It does *not* attempt to mirror the full Atlas; instead it contains the minimal set of datasets that the codebase knows how to fetch without manual consent steps.

When we decide to bring Atlas datasets into the automated workflow, the process is:`EXR-KJENS1RID1-AN`
1. Harvest metadata for the candidate IDs (via `scripts/exrna_enrich.py` or manual `samples.csv`).
2. Evaluate fluid coverage, donor counts, and QC completeness.
3. If a dataset meets the bar, add a new row to `config/dataset_manifest.csv` with the download plan (file URLs, portal steps, required consent) *and* retain the full entry in `exrna_atlas_catalog.csv`.

## Selection criteria for prioritising Atlas datasets

We favour cohorts that:
- Cover **multiple biofluids** per study (e.g., plasma / saliva / urine, or serum vs. EDTA plasma).
- Include **healthy donor baselines** that anchor forensic body-fluid fingerprints.
- Provide **processed count matrices** plus QC summaries (read depth, mapping stats) without needing raw FASTQs.
- Offer **manageable sample counts** (dozens rather than thousands of PCR wells) with clear metadata fields (`Biofluid Name`, `Disease Type`, `Profiling Assay`).

Conversely, we deprioritise datasets if they:
- Focus on a single diseased fluid with many repeated technical replicates.
- Lack accessible metadata after consent, making fluid assignment ambiguous.
- Duplicate another study with only trivial protocol changes.

## Initial priority queue (manual downloads)

1.  – Plasma/Saliva/Urine healthy cohort (multi-fluid baseline).
2. `EXR-TTUSC1gCrGDH-AN` – Serum vs. EDTA plasma longitudinal reproducibility series.
3. `EXR-LLAUR1AVB5CS-AN` & `EXR-LLAUR1BF5QLW-AN` – Diverse biofluid isolation method comparisons.
4. `EXR-ANACC1S6lJ1C-AN` – Healthy biofluids and surrogate tissues (cross-tissue contrast).

As these are downloaded, save the artefacts under `data/raw/exrna_manual/<EXR-ID>/` using the convention:
```
<EXR-ID>/
  raw_counts.txt            # “Raw miRNA Counts” download
  summary.zip               # “All Summary Files” archive
  samples.csv               # exported sample metadata (from the Samples modal)
  external_links.txt        # URLs from the external references popover (optional)
  README.md                 # acceptance date, consent notes, observations
```

## Recording decisions

Whenever we accept a dataset into the working set, capture the reasoning in `docs/exrna_dataset_log.md` (create if absent). Include:
- Date of selection and person responsible.
- Key metadata (fluids, donor counts, cohort health status).
- Any caveats (limited replicates, missing QC metrics).
- Link to the portal card and saved files.

This audit trail keeps the chain-of-custody clear and prevents redundant curation later.

## Re-evaluating as the Atlas updates

The Atlas is a living resource. Re-run the enrichment script periodically to detect new IDs. For each addition:
- Merge the new rows into `exrna_atlas_catalog.csv`.
- Re-apply the selection criteria.
- Update `dataset_manifest.csv` only after confirming download automation or documenting a manual consent workflow.

By keeping catalog, manifest, and decision log in sync, we can scale curation while preserving reproducibility.

## Manual note: EXR-LLAUR1AVB5CS-AN

The dataset **"RNA Isolation Methods - Diverse Biofluids" (PI: Louise Laurent)** could not be fetched via automation (enrichment script or portal APIs). Consent-gated downloads were manually retrieved through the exRNA Atlas interface:

- miRNA counts: `LLAUR01-RNAIsoBiofluidPool-2023-08-21_exceRpt_miRNA_ReadCounts.txt`
- Metadata exports: biosample, experiment, and donor TSVs

All artefacts now reside under `data/raw/exrna_manual/EXR-LLAUR1AVB5CS-AN/LLAUR01-RNAIsoBiofluidPool-2023-08-21/`.
## Manual note: EXR-ANACC1S6lJ1C-AN

Dataset **"Small non-coding RNA profiling in human biofluids and surrogate tissues" (PI: Alessio Naccarati)** lacks automation hooks. Manual retrieval on Sep 29, 2025 captured the biosample, experiment, and donor metadata TSVs after accepting the ERCC data policy, but the expected miRNA count matrix remains missing. Attempts to fetch `ANACC1-NORM_Normal_samples_sncRNA_Analysis-2018-06-12_exceRpt_miRNA_ReadCounts.txt` via the documented FTPS endpoint now return `550 File not found` or trigger connection resets (`curl` exit 56) even when using explicit FTPS, passive mode, or anonymous credentials. The per-sample `CORE_RESULTS_v4.6.2.tgz` archives are still listed in the portal manifest, yet the aggregate miRNA counts are no longer exposed via FTP.

Action items:
- Continue monitoring the portal for a reinstated processed counts download (escalate to ERCC helpdesk if no resolution this week).
- If the counts remain unavailable, pivot to a substitute healthy multi-fluid cohort (see candidate below) so harmonisation work can proceed.


### Substitute candidate while ANACC1 counts are missing

`EXR-KWANG1jo8Fqz-AN` (PI: Kai Wang) still advertises downloadable processed counts for 47 healthy-donor specimens spanning four biofluids (plasma, urine, saliva, cerebrospinal fluid). The Atlas catalog (`config/exrna_atlas_catalog.csv:41`) lists it under the same U01 programme as other successfully retrieved cohorts. Next manual pull should focus on grabbing the cohort-level miRNA read-count matrix plus QC summaries. If the portal exposes only sample-level `CORE_RESULTS` archives, plan to script batch extraction so the harmonised counts table can be rebuilt locally.

Rationale for the swap:
- Maintains a multi-fluid healthy baseline to contrast with forensic unknowns.
- Sample size (n=47) is manageable for downstream harmonisation and mirrors ANACC1’s design goals.
- Shares processing pipeline version (exceRpt v4.x) with existing manual downloads, simplifying normalisation.

## Harmonisation queue (Sep 29, 2025)

- `EXR-KJENS1RID1-AN` – Ready. Cohort-level exceRpt TGZ includes miRNA counts plus QC tables. Next: unpack to `tmp/exrna_manual/EXR-KJENS1RID1-AN/`, copy out `*_miRNA_ReadCounts.txt`, and align sample IDs with the saved biosample metadata export.
- `EXR-TTUSC1gCrGDH-AN` – Ready. Same exceRpt bundle structure; after extraction mirror the KJENS join logic and verify timepoint metadata for the reproducibility series.
- `EXR-LLAUR1AVB5CS-AN` – Ready. Count matrix already unpacked alongside biosample/experiment/donor TSVs. Next: standardise column names (Biofluid, Isolation Method, Donor) and flag any QC FAIL rows before merging.
- `EXR-ANACC1S6lJ1C-AN` – Blocked. Metadata TSVs are saved, but the portal no longer exposes the aggregate `exceRpt_miRNA_ReadCounts.txt`. Re-check portal/FTP weekly and capture any ERCC responses; harmonisation waits on this file or a replacement cohort.

Proceeding with the first three datasets still yields useful coverage for harmonisation experiments: KJENS provides plasma/saliva/urine baselines, TTUSC supplies serum vs. EDTA plasma replicates for stability checks, and LLAUR offers cross-biofluid isolation-method contrasts. The main gap is the missing surrogate tissue profiles from ANACC1, so downstream models will lack that cross-tissue anchor until the count matrix is recovered or a substitute cohort is added.

## Sanity check status (Sep 29, 2025)

## Analysis environment status (Sep 29, 2025) ✅ RESOLVED

- **Environment fixed**: venv at `env/` now has numpy 2.3.3, pandas 2.3.2, matplotlib 3.10.6, seaborn 0.13.2, scipy 1.16.2, and scikit-learn 1.7.2 installed and working.
- All imports verified functional. Harmonization scripts can now proceed.

## Initial signal workup outputs (Sep 29, 2025)
## Dataset-level modelling checklist (queued Sep 29, 2025)

- **Feature filtering (per dataset)** – Apply CPM ≥ 1 in ≥20% of samples and remove near-zero variance miRNAs prior to modelling to avoid inflating noise.
- **Within-study models** – For each cohort run platform-appropriate workflows (exceRpt counts → TMM + log2; limma/voom design ~ biofluid) to extract logFC, moderated SE, AUC, and candidate thresholds.
- Applied CPM/variance filters (`analysis/filter_features_per_dataset.py`): retained 609 miRNAs (KJENS), 729 (TTUSC), 454 (LLAUR). Filtered artefacts stored under `results/derived/<EXR-ID>/filtered/` with updated counts/CPM/log2 matrices and JSON summaries.
- **R environment ready** (Sep 29, 2025): Successfully installed edgeR 4.6.3 and limma 3.64.1 via BiocManager on R 4.5.0. TMM normalization and voom modeling now unblocked.
- **✅ TMM+voom differential expression complete** (Sep 29, 2025): Ran `analysis/tmm_voom_models.R` across all three cohorts. Results saved under `results/derived/<EXR-ID>/differential_expression/` with per-fluid DE tables, TMM-normalized CPM matrices, and summary statistics. Key findings:
  - **KJENS**: 551 miRNAs significant for Plasma (228 upregulated), 327 for Saliva (215 up), 537 for Urine (307 up). Top markers (highest AUC, upregulated): miR-486-5p (Plasma, logFC=7.01, AUC=0.993), miR-223-3p (Saliva, logFC=6.19, AUC=0.989), miR-30c-2-3p (Urine, logFC=7.40, AUC=0.999).
  - **TTUSC**: 463 miRNAs differentiate Plasma vs. Serum in both directions.
  - **LLAUR**: 19 miRNAs for Plasma, 200 for Serum, 365 for Urine (more variable cohort; one zero-count sample removed).
  - **Reproducibility**: Each dataset includes `reproducibility.json` (script MD5 `7c7d6805d4d3cd464dad4d543b1538c4`, R 4.5.0, edgeR 4.6.3, limma 3.64.1, top marker selection logic) and `sessionInfo.txt` (full session details) for forensic audit trail. See `docs/REPRODUCIBILITY.md`.
- **✅ QC diagnostics complete** (Sep 29, 2025): Ran `analysis/qc_diagnostics.py` to generate PCA plots, library size distributions, detection rates, and TMM factor visualizations. Key findings:
  - **KJENS**: PC1 explains 34.7% variance (biofluid separation), PC2 8.5%. Median library size 239K, detection range 51-604 miRNAs/sample.
  - **TTUSC**: PC1 17.5%, PC2 8.1%. Cleaner cohort with TMM factors 0.30-2.47 (vs KJENS 0.05-8.15).
  - **LLAUR**: PC1 30.2%, PC2 6.7%. Higher variability (TMM factors 0.25-63.3), one sample with only 3 counts post-filter.
  - All plots saved to `results/qc/<EXR-ID>/` as PNG/PDF pairs with accompanying TSV tables (PCA coordinates, variance explained, QC metrics).
- **✅ LLAUR outlier interrogation complete** (Sep 29, 2025): Ran `analysis/llaur_outlier_interrogation.py` to assess whether extreme TMM factors represent technical failures or forensically valuable diversity. **PRELIMINARY FINDING**: 100 samples (51%) flagged as outliers, but they cluster by biofluid **better** than inliers (silhouette 0.153 vs 0.077). **Preliminary Decision: RETAIN OUTLIERS** for cross-cohort validation. They represent protocol diversity and quality variation that mirrors real-world forensic conditions. Initial marker concordance analysis (using fold-change proxy, not formal re-analysis) suggests:
  - **Urine markers**: 74% concordance → potentially robust across quality (requires validation)
  - **Plasma/Serum markers**: 2% concordance → potentially quality-sensitive (requires validation)
  - **IMPORTANT CAVEATS**: This is exploratory analysis. Tier 1/Tier 2 classifications are hypotheses to test via LODO validation and formal inlier-only DE re-analysis, not final conclusions. Silhouette scores are low overall (<0.2), and concordance estimates are based on simple fold-change, not limma/voom.
  - Full analysis saved to `results/outlier_analysis/EXR-LLAUR1AVB5CS-AN/`. Decision may be revised after cross-cohort validation.
- **✅ Cross-cohort harmonization complete** (Sep 29, 2025): Ran `analysis/cross_cohort_harmonization.R` to merge TMM-normalized log₂-CPM matrices and apply ComBat batch correction. Key results:
  - **364 shared miRNAs** across all three datasets (intersection of KJENS, TTUSC, LLAUR post-filtering)
  - **936 total samples**: 428 KJENS, 312 TTUSC, 196 LLAUR (outliers retained)
  - **Biofluid distribution**: 479 Plasma, 239 Urine, 173 Serum, 45 Saliva
  - **Batch correction success**: PC1 variance increased 25.3% → 33.7% (biofluid signal enhanced), PC2 decreased 15.4% → 8.7% (batch effects removed)
  - **Outputs**: `results/derived/cross_cohort/tmm_log2cpm_batch_corrected.tsv` (USE FOR LODO), PCA coordinates before/after, diagnostic plots
  - See `results/derived/cross_cohort/HARMONIZATION_SUMMARY.md` for full analysis details
- **✅ LODO cross-validation complete** (Sep 29, 2025): Ran `analysis/lodo_validation.py` using batch-corrected matrix to test biofluid signature generalization. Key findings:
  - **Logistic regression outperforms random forest**: 81.2% ± 10.4% accuracy vs 64.6% ± 8.2%
  - **Quality variation impacts accuracy**: LLAUR (outliers) 67.3% vs clean cohorts 88.1% avg (-20.8%)
  - **Tier 1 validated (Urine)**: 91-97% F1 across all datasets including LLAUR outliers → court-ready robustness
  - **Tier 2 confirmed (Serum)**: Excellent on clean samples (TTUSC: 88% F1) but collapses on LLAUR (23% recall) → quality-sensitive
  - **Plasma over-calls on LLAUR**: 95% recall but 59% precision (many false positives under quality stress)
  - **Saliva zero-shot failed**: No samples in LLAUR/TTUSC training sets, cannot detect in KJENS test set
  - **Consensus markers**: miR-543, miR-1246, miR-3614-5p appear in top 10 across multiple folds (primarily Plasma/Serum distinction)
  - **Outputs**: Confusion matrices, ROC curves, feature importances, per-sample predictions for all 3 folds × 2 models
  - See `results/lodo/LODO_SUMMARY.md` for Daubert assessment and forensic recommendations
- **✅ Consensus marker identification complete** (Sep 29, 2025): Ran `analysis/marker_consensus.py` to identify miRNAs upregulated (logFC>0, FDR<0.05) in ≥2 cohorts for the same biofluid. Selection criteria and findings:
  - **Selection rules**: FDR < 0.05, logFC > 0, present in ≥2 datasets per biofluid, ranked by mean AUC descending
  - **226 total consensus markers**: 111 Urine, 76 Plasma, 39 Serum, 0 Saliva (insufficient data)
  - **Tier 1 (Court-Ready) - Urine**: 111 markers, top 20 panel saved (AUC 0.89-0.98). Robust to quality variation (LODO: 97% F1 on LLAUR outliers). Top markers: miR-30c-2-3p, miR-204-5p, miR-30a-3p, miR-200b-3p, miR-204-3p
  - **Tier 2 (Quality-Controlled) - Plasma/Serum**: 115 markers total, top 30 panel saved (AUC 0.81-0.95). Excellent on clean samples but degrades under quality stress (Serum: LODO 23% recall on LLAUR). Top Plasma: miR-106b-3p, miR-144-3p, miR-25-3p. Top Serum: miR-223-5p, miR-744-5p, miR-146a-5p
  - **Tier 3 (Insufficient Data) - Saliva**: Only present in KJENS (n=45, 215 upregulated markers), zero-shot LODO detection failed. Requires multi-cohort study before panel development
  - **Protocol caution**: Serum markers require controlled sample collection/processing. Not validated for degraded crime scene conditions
  - **Outputs**: `marker_consensus.tsv` (full table), `marker_tiers.json` (tier assignments + rationale), `tier1_panel_urine.tsv`, `tier2_panel_plasma_serum.tsv`


- Executed `source env/bin/activate && python analysis/initial_signal_workup.py`. Per-dataset artefacts now live under `results/derived/EXR-KJENS1RID1-AN/`, `EXR-TTUSC1gCrGDH-AN/`, and `EXR-LLAUR1AVB5CS-AN/` (counts, CPM, log2 CPM, metadata tables).
- Harmonised 1,417-miRNA intersection exported to `results/derived/harmonized/log2_cpm_intersection.tsv` with companion `sample_metadata.tsv` and `summary.json`.
- `summary.json` snapshot: `EXR-KJENS1RID1-AN` 2068 miRNAs × 428 samples (136 low-count), `EXR-TTUSC1gCrGDH-AN` 2124 × 312 (23 low-count), `EXR-LLAUR1AVB5CS-AN` 1536 × 197 (66 low-count).
- Next actions per harmonization plan: filter low-count / `qc_status = FAIL` samples, then begin cross-cohort normalization diagnostics and feature selection.
- Applied low-count / QC filters via `analysis/filter_low_quality_samples.py`; retained 710 of 937 samples (KJENS −136, TTUSC −23, LLAUR −68). Filtered matrices: `results/derived/harmonized/log2_cpm_intersection.filtered.tsv` and `sample_metadata.filtered.tsv`; exclusions logged in `removed_samples.tsv`.


- **File integrity** – Staged copies under `tmp/exrna_manual/<EXR-ID>/selected/` match the originals (sha256 parity for counts, RPM, QC, and metadata files).
- **Sample IDs** – Column headers in each miRNA count matrix align with the available metadata exports: 428 samples for `EXR-KJENS1RID1-AN`, 312 for `EXR-TTUSC1gCrGDH-AN`, and 197 for `EXR-LLAUR1AVB5CS-AN` (using the earlier `18_19_25` biosample export; the later `18_34_34` pull is truncated and should be ignored).
- **Feature overlap** – The three cohorts share 1,417 mature miRNA features. KJENS and TTUSC each carry ~2000 assayed miRNAs (leaving 651–707 features not seen in LLAUR), while LLAUR reports 1,536 total with 119 not present in the other two. Expect to harmonise on the intersection and track cohort-specific miRNAs separately.
- **QC review** – KJENS shows wide coverage (median miRNA reads 2.4×10^5) but 136 samples fall below 1×10^5 miRNA counts; TTUSC has 23 such low libraries (median 9.1×10^5). LLAUR metadata flags 25 biosamples as `FAIL` (vs 172 `PASS`). Tag these low-quality samples before downstream normalisation.

## Harmonisation plan once counts are in hand

1. **Stage per-study archives.** For each TGZ in `data/raw/exrna_manual/<EXR-ID>/`, extract to a temporary scratch directory (`tmp/exrna_manual/<EXR-ID>/`) preserving the sample-level folder layout. Retain the original archives for provenance by copying out only the `exceRpt_miRNA_ReadCounts.txt` and QC TSVs.
2. **Build unified count matrices.** Concatenate the per-sample miRNA counts into a wide matrix keyed by `miRNA_ID`. Maintain raw counts, RPM, and any pipeline-supplied normalised columns separately. Document version info (`exceRpt` release, genome build) alongside the matrix.
3. **Merge with metadata.** Join the count table to biosample metadata (`Biofluid Name`, `Disease Type`, `Donor ID`) and experiment metadata (`Library Prep`, `QC status`). Lift donor-level attributes (sex, age) onto the sample rows to enable batch correction later.
4. **Initial QC and normalisation.** Filter flagged samples (e.g., `QC status != PASS` or low mapped reads), then compute library-size normalisation (CPM, TMM via edgeR) and variance-stabilising transforms (log2(CPM+1), VST). Capture diagnostic plots (library size, detected miRNAs, PCA) under `reports/exrna/manual/`.
5. **Document outputs.** Record the processed file locations and QC observations in `docs/exrna_dataset_log.md` with timestamps, and update the dataset manifest with a reproducible ingestion command once the workflow is scripted.


