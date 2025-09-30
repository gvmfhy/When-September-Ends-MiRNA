# LLAUR Outlier Interrogation Report

**Date**: 2025-09-29 21:59
**Dataset**: EXR-LLAUR1AVB5CS-AN (Diverse biofluid isolation methods)
**Analysis**: Robustness assessment for forensic marker validation

---

## Executive Summary

**Total samples**: 196
**Outliers identified**: 100 (51.0%)
**Outlier criteria**: TMM factor <0.4 or >5.0, OR library size <1000

**Decision**: STRATIFIED ANALYSIS - Mixed quality

**Recommendation**: Report markers in tiers: Tier 1 (significant with outliers), Tier 2 (significant without outliers). Document robustness.

---

## Outlier Characterization

### By Biofluid
- **Plasma**: 38 outliers
- **Serum**: 35 outliers
- **Urine**: 27 outliers


### Clustering Metrics (Silhouette Score)
- **All samples**: 0.092
- **Inliers only**: 0.077
- **Outliers only**: 0.153

**Interpretation**:
- Silhouette > 0.5: Strong biofluid separation (outliers are valid)
- Silhouette 0.3-0.5: Moderate separation (mixed quality)
- Silhouette < 0.3: Weak/no separation (likely technical failures)

---

## Differential Expression Concordance

Overlap between top 50 upregulated markers (all samples) vs. inliers-only:

- **Plasma**: 1/50 (2.0% concordance)
- **Serum**: 1/50 (2.0% concordance)
- **Urine**: 37/50 (74.0% concordance)


**Interpretation**:
- >80% concordance: Markers are robust to outliers (Tier 1)
- 60-80%: Moderate sensitivity to quality (Tier 2)
- <60%: Quality-dependent markers (exclude or document)

---

## Forensic Implications

### If Outliers Cluster by Biofluid (Keep Them):
Crime scene samples will be degraded, diluted, or protocol-variable. Outliers that still cluster correctly represent **real-world forensic conditions**. Markers validated on this subset are:
- More likely to survive Daubert challenges
- Defensible under cross-examination ("tested on degraded samples")
- Deployable for field use

**Action**: Keep outliers. Report markers as "Tier 1 (robust)" if significant with outliers included.

### If Outliers Scatter Randomly (Exclude Them):
Random scatter indicates technical failure (failed library prep, contamination). These samples add noise without biological signal.

**Action**: Exclude from primary analysis. Document exclusion rationale. Run sensitivity analysis to confirm marker stability.

---

## Next Steps

1. **Review PCA plots** (`pca_outliers_highlighted.png`): Do outliers cluster by biofluid or scatter?
2. **Check isolation method** (if outliers cluster by method): Document as protocol-dependent, but keep for robustness.
3. **Stratified validation**: Run LODO with/without outliers to quantify marker robustness.
4. **Update harmonization plan**: If keeping outliers, ensure batch correction doesn't over-correct biological variability.

---

## Files Generated

- `outlier_characteristics.png/pdf` - Distribution of TMM factors, library sizes, biofluids
- `pca_outliers_highlighted.png/pdf` - PCA with outliers marked
- `outlier_sample_list.tsv` - Full metadata for outlier samples
- `de_concordance_analysis.tsv` - Marker overlap between all vs. inliers-only
- `decision_matrix.json` - Quantitative decision criteria

---

**Analysis script**: `analysis/llaur_outlier_interrogation.py`
**For questions**: See `docs/REPRODUCIBILITY.md` for environment details
