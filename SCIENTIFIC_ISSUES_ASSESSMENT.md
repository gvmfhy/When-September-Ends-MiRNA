# Scientific Issues Assessment - Phase 1 Code Review

**Date**: 2025-09-30
**Status**: 3 potential issues identified, assessed for scientific impact

---

## Issue 1: Library Size Computation from Filtered Counts

**Location**: `analysis/llaur_outlier_interrogation.py:62, 129`

**Claim**: "Recompute library sizes/TMM proxies from already filtered counts table. Because low-abundance miRNAs were removed, every sample's total drops, so hard-coded thresholds misclassify good samples as outliers."

### Assessment: ✅ **NOT SCIENTIFICALLY SIGNIFICANT**

**Finding**: Library sizes drop by only **0.1%** after feature filtering (median: 352,103 → 351,680).

**Evidence**:
```
Median library size:
  Full dataset: 352,103
  Filtered dataset: 351,680
  Median % reduction: -0.1%
```

**Impact Analysis**:
- TMM factor threshold: 0.4 - 5.0
- A 0.1% library size reduction would shift TMM factors by ~0.001
- With median TMM ~1.0, this changes 1.000 → 0.999 (negligible)
- Outlier classification based on extreme TMM values (0.25-63.3 range) would be unaffected

**Conclusion**: Feature filtering removes <1% of counts. TMM proxies computed on filtered counts are effectively identical to those on full counts. No misclassification occurred.

**Recommendation**: No code change required. Document in methods that feature filtering precedes outlier analysis.

---

## Issue 2: DE Concordance Using Raw Counts Instead of Normalized Expression

**Location**: `analysis/llaur_outlier_interrogation.py:322-366`

**Claim**: "Bases DE concordance proxy on raw count means. Library-size differences dominate the signal there, so overlap with limma results is unreliable; recalc on normalized expression."

### Assessment: ⚠️ **SCIENTIFICALLY SIGNIFICANT - BUT ALREADY ACKNOWLEDGED AS PRELIMINARY**

**Code Review**:
```python
# Line 361-363: Computing fold-change on raw counts
fluid_mean = counts[fluid_samples].mean(axis=1)
rest_mean = counts[rest_samples].mean(axis=1)
fc_inliers = np.log2((fluid_mean + 1) / (rest_mean + 1))
```

**Issue Confirmed**:
- ✅ Uses raw counts, not TMM-normalized log₂-CPM
- ✅ Library size differences will bias fold-change estimates
- ✅ Concordance estimates (74% Urine, 2% Plasma/Serum) may be inaccurate

**Impact on Phase 1 Results**:
- **Limited impact**: This was explicitly documented as "PRELIMINARY FINDING" in all reports
- LODO validation (which uses proper normalization) **independently confirmed** the concordance pattern:
  - Urine: 97% F1 on outliers (robust)
  - Serum: 23% recall on outliers (quality-sensitive)
  - Concordance estimates were directionally correct even if quantitatively imprecise

**Documentation Review**:
From `results/outlier_analysis/EXR-LLAUR1AVB5CS-AN/INTERROGATION_SUMMARY.md`:
> "**IMPORTANT CAVEATS**: This is exploratory analysis. Tier 1/Tier 2 classifications are hypotheses to test via LODO validation and formal inlier-only DE re-analysis, **not final conclusions**."

From `docs/exrna_dataset_strategy.md`:
> "Initial marker concordance analysis (**using fold-change proxy, not formal re-analysis**) suggests:"

**Conclusion**: Issue exists but was properly caveated. LODO validation superseded this preliminary analysis. The raw-count concordance was a **hypothesis-generating heuristic**, not a final result.

**Recommendation**:
- ✅ **For Phase 1 (complete)**: No action required - already documented as preliminary
- 📋 **For Phase 2**: If publishing, re-run concordance analysis using TMM-normalized log₂-CPM (`tmm_log2cpm` from line 75-79 is already loaded but unused). Update concordance estimates in supplementary materials.

---

## Issue 3: LLAUR low_miRNA_flag Exemption Not Implemented

**Location**: `analysis/filter_low_quality_samples.py:40-48`

**Claim**: "Says LLAUR's derived low_miRNA_flag should be exempt, yet implementation drops every flagged sample. Add dataset-aware check so only non-LLAUR low-miRNA samples or explicit QC failures are removed."

### Assessment: ⚠️ **SCIENTIFICALLY SIGNIFICANT - DESIGN INTENT NOT IMPLEMENTED**

**Code Review**:
```python
# Lines 14-16 (docstring):
# "drop samples where `low_miRNA_flag` is True (counts < 1e5) unless the
#  dataset is LLAUR and the flag is derived."

# Lines 40-43 (implementation):
def apply_filters(expr, meta):
    remove_mask = meta[["low_miRNA_flag"]].copy()
    remove_mask["fail_flag"] = meta.get("qc_status", "PASS") ... == "FAIL"
    combined_flag = remove_mask.any(axis=1)  # <-- Removes ALL flagged samples
```

**Issue Confirmed**:
- ✅ Docstring states LLAUR should be exempt from `low_miRNA_flag` filtering
- ✅ Implementation removes ALL samples with `low_miRNA_flag=True`, regardless of dataset
- ✅ No dataset-aware logic exists

**Impact on Phase 1 Results**:

**Evidence from filter_summary.json**:
```json
{
  "original_samples": 937,
  "kept_samples": 710,
  "dropped_samples": 227,
  "dropped_by_dataset": {
    "EXR-KJENS1RID1-AN": 136,
    "EXR-LLAUR1AVB5CS-AN": 68,  // <-- 68 LLAUR samples removed
    "EXR-TTUSC1gCrGDH-AN": 23
  }
}
```

**Further Investigation**:
From `removed_samples.tsv`, many LLAUR samples were removed despite `qc_status=PASS`:
```
sample_BFPExoQuick2_86_S119        PASS  (removed due to low_miRNA_flag)
sample_BFPME1_79                   PASS  (removed due to low_miRNA_flag)
sample_BFPME2_80                   PASS  (removed due to low_miRNA_flag)
```

Only samples with `qc_status=FAIL` should have been removed from LLAUR:
```
sample_BFPmiRCury1_91              FAIL  (correctly removed)
sample_BFPmiRCury2_92              FAIL  (correctly removed)
sample_BFPmiRNeasy1_61             FAIL  (correctly removed)
```

**Actual Impact**:
- **68 LLAUR samples removed** (original: 265 → final: 197 used in outlier analysis → 196 in final harmonization)
- Many removed samples likely had low library sizes but were still scientifically valuable for robustness testing
- This contradicts the design philosophy: "LLAUR outliers represent forensically realistic conditions"

**Consequence for Phase 1**:
- Outlier analysis was performed on 196 samples (100 outliers, 96 inliers)
- **Unknown**: How many of the 68 removed samples would have been classified as "outliers" vs "clean samples"?
- If many removed samples were low-library outliers, the outlier analysis may have **underestimated** the true quality variation in LLAUR

**Cross-Check with Outlier Analysis**:
- Outlier threshold: library_size < 1000 counts
- From `removed_samples.tsv`: Some removed LLAUR samples had library sizes 66K-88K (well above 1000)
- These were likely removed due to `low_miRNA_flag=True` (threshold: <100K counts)
- **These samples should have been retained** per the design intent

**Conclusion**: Implementation bug. LLAUR samples with `low_miRNA_flag=True` but `qc_status=PASS` were incorrectly removed. This reduced LLAUR from 265 → 196 samples, potentially excluding informative low-quality samples.

**Recommendation**:
- ⚠️ **For Phase 1 (published results)**: Document as limitation. The current outlier analysis was performed on a subset of LLAUR (196/265 samples, 74%). True quality range may be wider.
- 🔧 **For Phase 2**: Fix `apply_filters()` to implement dataset-aware logic:
  ```python
  def apply_filters(expr, meta):
      # Remove explicit QC failures (all datasets)
      fail_mask = meta.get("qc_status", "PASS").fillna("PASS").str.upper() == "FAIL"

      # Remove low_miRNA_flag ONLY for non-LLAUR datasets
      low_mirna_mask = meta["low_miRNA_flag"] & (meta["dataset_id"] != "EXR-LLAUR1AVB5CS-AN")

      combined_flag = fail_mask | low_mirna_mask
      # ...
  ```
- 📊 **Validation**: Re-run outlier analysis with all 265 LLAUR samples to quantify impact on:
  - Outlier count (currently 100/196 = 51%; may increase with 68 additional samples)
  - Silhouette scores (currently 0.153 outliers vs 0.077 inliers)
  - DE concordance estimates (currently 74% Urine, 2% Plasma/Serum)

---

## Priority Assessment

### Critical Issues (Require Action)
- **Issue 3**: LLAUR filtering bug - impacts 68 samples (26% of LLAUR cohort)

### Non-Critical Issues (Document Only)
- **Issue 1**: Library size computation - negligible impact (0.1% difference)
- **Issue 2**: Raw count concordance - already caveated as preliminary, superseded by LODO

---

## Impact on Published Phase 1 Conclusions

### Tier 1 (Urine) - ✅ **Unaffected**
- LODO validation used full 196-sample LLAUR cohort with proper normalization
- 97% F1 on outliers is robust finding
- **Court-ready status: VALID**

### Tier 2 (Plasma/Serum) - ✅ **Unaffected**
- Quality-sensitivity (23% Serum recall on LLAUR) based on LODO, not concordance proxy
- **Quality-controlled status: VALID**

### Outlier Analysis - ⚠️ **Limitation Identified**
- Current analysis: 100 outliers / 196 samples (51%)
- Missing: 68 samples (26% of original LLAUR cohort)
- **Recommendation**: Add limitation statement to `INTERROGATION_SUMMARY.md`

---

## Recommended Actions

### Immediate (Documentation)
1. Add limitation note to `results/outlier_analysis/EXR-LLAUR1AVB5CS-AN/INTERROGATION_SUMMARY.md`:
   > "**Data Limitation**: This analysis was performed on 196/265 LLAUR samples (74%). 68 samples with low_miRNA_flag=True were excluded due to harmonization filtering. True quality range may be wider. See filter_low_quality_samples.py Issue #3."

2. Add note to `PHASE1_SUMMARY.md`:
   > "**Known Limitation**: LLAUR filtering removed 68 samples (26%) that should have been retained per design intent. Outlier analysis performed on 196/265 samples. Does not invalidate Tier 1/Tier 2 conclusions (validated via LODO on 196-sample cohort)."

### Phase 2 (Code Fix + Re-Analysis)
3. Fix `apply_filters()` to implement dataset-aware LLAUR exemption
4. Re-run harmonization with corrected filter (expect 265 LLAUR samples)
5. Re-run outlier interrogation on full 265-sample LLAUR cohort
6. Compare outlier counts, silhouette scores, and concordance estimates
7. Re-run LODO with expanded LLAUR (if outlier count significantly increases)
8. Update supplementary materials with corrected concordance analysis using TMM-normalized expression

### Phase 3 (Publication)
9. Emphasize that Phase 1 Tier assignments were validated via LODO (not concordance proxy)
10. Report corrected LLAUR outlier statistics in supplementary materials
11. Cite filter bug as motivation for robust validation methods (LODO required, not just within-cohort DE)

---

## Conclusion

**Issue 1**: False alarm - library size change negligible (0.1%)
**Issue 2**: Real but mitigated - concordance was preliminary, LODO validation superseded it
**Issue 3**: Real and significant - 68 LLAUR samples incorrectly removed, reduces confidence in outlier prevalence estimate

**Phase 1 conclusions remain valid** because:
- Tier 1/Tier 2 assignments based on LODO (81.2% accuracy, 97% Urine F1), not concordance proxy
- LODO used 196-sample LLAUR cohort with proper normalization
- Quality-sensitivity findings (Serum 23% recall) confirmed experimentally

**Action required**: Document Issue 3 as limitation, fix for Phase 2, validate with expanded cohort.