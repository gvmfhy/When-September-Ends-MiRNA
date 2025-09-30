# Quality Control Summary - exRNA Datasets

**Date**: 2025-09-29
**Pipeline**: `analysis/qc_diagnostics.py`
**Datasets**: EXR-KJENS1RID1-AN, EXR-TTUSC1gCrGDH-AN, EXR-LLAUR1AVB5CS-AN

---

## Overview

All three exRNA Atlas datasets passed quality control after filtering for low-count samples and low-variance miRNAs. PCA analysis shows clear biofluid separation in all cohorts, with PC1 capturing 17-35% of variance. TMM normalization successfully corrected for library size differences, though LLAUR exhibits higher technical variability.

---

## Dataset-Specific Findings

### EXR-KJENS1RID1-AN (KJENS)
**Cohort**: Plasma/Saliva/Urine baseline
**Samples**: 428 (after QC filtering)
**miRNAs**: 609 (CPM≥1 in ≥20% samples)

**PCA Results**:
- PC1: 34.7% variance explained
- PC2: 8.5% variance explained
- **Interpretation**: Strong biofluid separation, primarily driven by PC1. Plasma and urine clusters are well-separated; saliva shows intermediate positioning.

**Library Metrics**:
- Range: 762 - 27.6M counts
- Median: 239K counts
- **Assessment**: Wide dynamic range suggests diverse sampling depths. All samples above minimum threshold for reliable quantification.

**Detection Rates**:
- Range: 51 - 604 detected miRNAs per sample
- Median: 301 miRNAs/sample
- **Assessment**: Consistent detection across samples. Lower end (51 miRNAs) indicates some low-complexity samples retained after filtering.

**TMM Normalization**:
- Factor range: 0.048 - 8.147
- **Assessment**: Wide range indicates substantial library size differences. One or more samples required large normalization factors (>8×), suggesting either very low or very high library complexity.

---

### EXR-TTUSC1gCrGDH-AN (TTUSC)
**Cohort**: Serum vs. EDTA plasma longitudinal series
**Samples**: 312 (after QC)
**miRNAs**: 729

**PCA Results**:
- PC1: 17.5% variance
- PC2: 8.1% variance
- **Interpretation**: Moderate separation between plasma and serum. Lower PC1 variance suggests greater technical homogeneity or smaller biological differences between these closely related fluids.

**Library Metrics**:
- Median: ~900K counts (estimated from plots)
- **Assessment**: Higher median library size than KJENS, indicating deeper sequencing or different extraction protocol.

**Detection Rates**:
- Higher overall detection (729 miRNAs retained vs. 609 in KJENS)
- **Assessment**: Suggests better overall data quality or less stringent pre-filtering.

**TMM Normalization**:
- Factor range: 0.301 - 2.468
- **Assessment**: Tightest normalization range of the three cohorts. Indicates highly consistent library preparation and sequencing depth. This is the "cleanest" technical cohort.

---

### EXR-LLAUR1AVB5CS-AN (LLAUR)
**Cohort**: Diverse biofluid isolation method comparisons
**Samples**: 196 (after QC; 1 sample removed for zero counts)
**miRNAs**: 454

**PCA Results**:
- PC1: 30.2% variance
- PC2: 6.7% variance
- **Interpretation**: Strong PC1 separation (likely fluid type), but lower PC2 contribution suggests isolation method effects are secondary or confounded with fluid type.

**Library Metrics**:
- Range: 3 - 7.9M counts
- Median: 355K counts
- **Warning**: Minimum library size of 3 counts indicates a near-failure sample that survived filtering. Review sample `<ID>` for exclusion from downstream modeling.

**Detection Rates**:
- Range: 2 - 441 detected miRNAs
- Median: 286 miRNAs/sample
- **Assessment**: Broader range than other cohorts, reflecting diverse isolation protocols. Minimum of 2 detected miRNAs correlates with the 3-count sample.

**TMM Normalization**:
- Factor range: 0.246 - **63.277**
- **Assessment**: Extreme maximum factor (63×) is a red flag. This sample requires >60-fold adjustment to normalize to cohort median, indicating either:
  1. Failed library prep
  2. Extremely low RNA input
  3. Isolation method incompatibility
- **Recommendation**: Flag sample with TMM factor >10 for sensitivity analysis or exclusion.

---

## Cross-Cohort Observations

### Strengths
1. **Clear biofluid signatures**: PCA shows separation in all cohorts, validating biological signal over technical noise.
2. **TTUSC as technical benchmark**: Tight TMM range (0.3-2.5) establishes expected variability for well-controlled experiments.
3. **Adequate sample sizes**: All cohorts have sufficient N per biofluid for within-study differential expression.

### Concerns
1. **LLAUR extreme outlier**: Sample(s) with TMM factors >60 and <10 counts should be excluded or analyzed separately.
2. **KJENS library size heterogeneity**: 170-fold range (762 to 27.6M) may reflect batch effects or variable sample quality.
3. **Low PC2 variance in LLAUR**: Only 6.7% suggests isolation method effects are weak or confounded, limiting the study's ability to assess protocol robustness.

### Implications for Cross-Cohort Harmonization
- **Batch correction needed**: ComBat or similar methods required to merge KJENS/TTUSC/LLAUR for meta-analysis.
- **Leave-one-dataset-out (LODO) validation**: Essential to assess whether markers generalize across platforms/protocols.
- **Conservative filtering**: Consider removing samples with TMM factors >10 or library sizes <1000 counts before harmonization.

---

## LLAUR Outlier Decision (Sep 29, 2025) - PRELIMINARY

**Analysis Performed**: Interrogated 100 LLAUR samples (51%) flagged as outliers (TMM <0.4 or >5.0, library size <1000)

**Key Finding**: Outliers cluster by biofluid **better** than inliers (silhouette 0.153 vs 0.077), suggesting they represent protocol diversity rather than technical failures.

**Preliminary Decision**: **RETAIN OUTLIERS** for primary analysis

**Rationale**:
- Outlier silhouette score (0.153) > inlier score (0.077) indicates stronger biofluid signal
- Marker concordance analysis suggests quality-robustness differences:
  - Urine: 74% top-marker overlap between all-samples and inliers-only → potentially robust
  - Plasma/Serum: 2% overlap → potentially quality-sensitive
- Outliers represent forensically realistic conditions (protocol variation, quality range)

**IMPORTANT CAVEATS - PRELIMINARY ANALYSIS**:

⚠️ **This is exploratory analysis, not final validation**:
1. Concordance estimates based on simple fold-change proxy, **not re-run limma/edgeR**
2. Analysis limited to **single dataset** (LLAUR) - patterns may not generalize
3. **No cross-cohort validation yet** - need to check if Urine robustness holds in KJENS/TTUSC
4. Silhouette scores are low across the board (<0.2) - weak clustering overall
5. Sample size for inlier-only subgroups is small (Plasma n=45, Serum n=42, Urine n=9)

**What This Means**:
- Outliers will be **included** in cross-cohort harmonization and LODO validation
- Tier 1/Tier 2 marker classifications are **hypotheses to test**, not conclusions
- Final marker panel requires multi-cohort validation and sensitivity analysis

**Next Steps Required to Validate**:
1. **Re-run LLAUR DE formally** with inliers-only using limma/voom (not fold-change proxy)
2. **Cross-cohort concordance**: Check if Urine robustness pattern appears in KJENS/TTUSC
3. **LODO validation stratified by quality**: Train on clean cohorts, test on LLAUR (all vs inliers)
4. **Sensitivity analysis**: Quantify AUC/accuracy drop when quality varies
5. **Protocol-specific effects**: Analyze whether outlier clustering is driven by isolation method

**Status**: Outliers retained pending validation. Decision may be revised after LODO and cross-cohort analysis.

---

## Next Steps

1. ~~**Identify extreme outliers**~~: ✅ Complete (100 samples characterized, decision: retain pending validation)
2. **Cross-cohort PCA**: Merge all three datasets (post-TMM normalization) and visualize batch/cohort effects.
3. **LODO cross-validation**: Train classifiers on 2 cohorts, test on 3rd; repeat for all permutations. Stratify by quality (LLAUR all vs inliers).
4. **Marker consensus**: Identify miRNAs significant across ≥2 cohorts for core forensic panel.
5. **Formal sensitivity analysis**: Re-run LLAUR DE with inliers-only using proper statistical framework (not fold-change proxy).

---

## Files Generated

Each dataset directory (`results/qc/<EXR-ID>/`) contains:
- `<ID>_pca.png/pdf` - PCA scatter (PC1 vs PC2) + scree plot
- `<ID>_library_sizes.png/pdf` - Boxplot and histogram by biofluid
- `<ID>_detection_rates.png/pdf` - Detected miRNAs per sample
- `<ID>_tmm_factors.png/pdf` - Normalization factor distribution
- `<ID>_pca_coordinates.tsv` - PC1-10 sample coordinates
- `<ID>_pca_variance.tsv` - Variance explained per component
- `<ID>_qc_summary.json` - Quantitative metrics

---

**Pipeline reproducibility**: See `docs/REPRODUCIBILITY.md` for Python environment (numpy 2.3.3, pandas 2.3.2, scikit-learn 1.7.2, seaborn 0.13.2).