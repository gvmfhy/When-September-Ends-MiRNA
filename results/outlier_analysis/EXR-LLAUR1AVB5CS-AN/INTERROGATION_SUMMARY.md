# LLAUR Outlier Interrogation - Key Findings

**Date**: 2025-09-29
**Status**: **PRELIMINARY ANALYSIS** - Hypotheses to validate, not final conclusions
**Provisional Decision**: RETAIN OUTLIERS for cross-cohort validation

---

## The Critical Discovery

**Outliers cluster by biofluid BETTER than inliers:**
- Silhouette score (outliers): **0.153**
- Silhouette score (inliers): **0.077**
- Silhouette score (all samples): **0.092**

### What This Means
The 100 "outlier" samples (51% of LLAUR) are **not technical failures**. They represent:
1. Diverse isolation protocols (study's explicit purpose)
2. Range of sample quality (forensically realistic)
3. **Stronger biofluid signal** than "clean" samples

This is exactly what we need for forensic validation.

---

## The Quality-Robustness Trade-Off

### Marker Concordance Analysis

When comparing top 50 markers (all samples vs. inliers-only):

| Biofluid | Concordance | Interpretation |
|----------|-------------|----------------|
| **Urine** | 74% (37/50) | **Tier 1: Forensically Robust** |
| Plasma | 2% (1/50) | Tier 2: Quality-Dependent |
| Serum | 2% (1/50) | Tier 2: Quality-Dependent |

### The Forensic Insight

**Urine markers are robust to quality variation.** They remain significant whether you include:
- Failed library preps (14 counts)
- Protocol extremes (TMM 0.25-63.3)
- Mixed QC status (PASS/FAIL)

**Plasma/Serum markers collapse under quality stress.** Only 1 of top 50 markers survives when outliers are excluded. This means:
- These markers work in pristine lab conditions
- They **will fail on crime scene samples**
- Not court-ready without heavy caveats

---

## Sample Characteristics

### Outlier Breakdown (100 samples)
- **Plasma**: 38 outliers
- **Serum**: 35 outliers
- **Urine**: 27 outliers

### Why They're Flagged
Review of outlier sample list reveals:

**Category 1: Genuinely Failed (n≈5-10)**
- Library size <100 counts (e.g., sample_BFPmiRNeasy2_62: 14 counts)
- QC status: FAIL
- TMM factor >20

**Category 2: Isolation Method Effects (n≈60-70)**
- Library size 5K-100K (below median but detectable)
- QC status: Mixed (many are PASS!)
- TMM factor 3-10
- Cluster correctly by biofluid despite low yield

**Category 3: High-Quality Outliers (n≈20-30)**
- Library size >1M (very clean)
- QC status: PASS
- TMM factor <0.4 (flagged for being TOO clean relative to median)
- Examples: Exiqon method samples with 1.2-1.8M counts

### Key Observation
Most outliers are **PASS QC status** with moderate library sizes (5K-100K). They're not technical failures—they're protocol diversity, which is exactly what LLAUR was designed to capture.

---

## Forensic Implications

### Why This Matters for Court

**Daubert Challenge Scenario:**

> **Defense Attorney**: "Your assay only works on pristine lab samples. How do you know it works on degraded crime scene evidence?"

**Our Response (with outliers included):**
> "We validated markers across 196 samples spanning 14 to 7.9 million counts—a 560,000-fold range. Samples included multiple isolation protocols and variable quality. Tier 1 markers (Urine panel) remained significant across this entire range, demonstrating robustness to real-world forensic conditions."

**Our Response (if we dropped outliers):**
> "We validated on 96 high-quality samples with consistent protocols."
>
> [Defense attorney destroys us in cross-examination]

### The Trade-Off

**Keeping outliers:**
- ✅ Forensically defensible ("tested on degraded samples")
- ✅ Identifies truly robust markers (Tier 1)
- ✅ Documents protocol sensitivity (Tier 2)
- ✅ Better biofluid clustering (silhouette 0.153 vs 0.077)
- ⚠️ Higher technical noise in Plasma/Serum contrasts

**Dropping outliers:**
- ✅ Cleaner statistical results for publication
- ✅ More Plasma/Serum markers reach significance
- ❌ Markers won't generalize to crime scenes
- ❌ Vulnerable to Daubert challenge
- ❌ Loses protocol-robustness information

---

## Decision: Keep Outliers, Tiered Marker Reporting

### Tier 1: Forensically Robust (Court-Ready)
**Criteria**: Significant with FDR<0.05 in **both** analyses:
- All samples (n=196, including outliers)
- Inliers only (n=96)

**Expected markers**: Primarily Urine panel (74% concordance)

**Marketing**: "Validated across 560,000-fold quality range"

### Tier 2: Lab-Grade (Research Use)
**Criteria**: Significant in inliers-only OR all-samples, but **not both**

**Expected markers**: Most Plasma/Serum markers (2% concordance)

**Marketing**: "Requires controlled sample collection protocols"

### Tier 3: Cohort-Specific (Exclude)
**Criteria**: Only significant in LLAUR, not in KJENS or TTUSC

**Action**: Document as platform/protocol artifacts

---

## Recommended Next Steps

### 1. Immediate (Today)
- [x] Document decision in `docs/exrna_dataset_strategy.md`
- [ ] Update QC_SUMMARY.md with outlier retention rationale
- [ ] Flag Category 1 samples (n<100 counts) for sensitivity check

### 2. Short-Term (This Week)
- [ ] Re-run LLAUR DE with outliers explicitly included (confirm current results)
- [ ] Generate Tier 1 vs Tier 2 marker lists
- [ ] Cross-reference Tier 1 markers with KJENS/TTUSC (multi-cohort validation)

### 3. Medium-Term (Cross-Cohort Validation)
- [ ] LODO with stratification:
  - Train on KJENS+TTUSC → Test on LLAUR (all)
  - Train on KJENS+TTUSC → Test on LLAUR (inliers only)
  - Train on KJENS+LLAUR → Test on TTUSC
- [ ] Quantify Tier 1 AUC drop between clean and messy test sets
- [ ] Document robustness in supplementary materials

---

## What We Learned

1. **"Outliers" with better biofluid signal than "inliers" are not failures** - they're forensic gold.

2. **Plasma/Serum markers are quality-fragile** - 98% of top markers disappear when quality varies. This is a **showstopper for field deployment** without protocol standardization.

3. **Urine markers are robust** - 74% concordance means they survive quality variation. These go to court.

4. **LLAUR's "mess" is its value** - isolation method diversity tests exactly what crime scenes will throw at us.

5. **Stratified reporting prevents overpromising** - Tier 1 vs Tier 2 sets honest expectations and survives expert scrutiny.

---

## Conclusion - PRELIMINARY

**LLAUR outliers retained for now, pending validation.** The 2% Plasma/Serum vs 74% Urine concordance pattern is suggestive but requires confirmation via:

1. **Formal re-analysis**: Re-run LLAUR DE with inliers-only using limma/voom (not fold-change proxy)
2. **Cross-cohort check**: Test if Urine robustness pattern appears in KJENS/TTUSC
3. **LODO validation**: Train on clean cohorts, test on LLAUR (stratified by quality)

**Current hypothesis** (to be tested):
- Urine markers may be robust across quality variation → forensic panel candidates
- Plasma/Serum markers may be quality-sensitive → protocol-controlled use only

**What we know for certain**:
- Outliers cluster by biofluid (silhouette 0.153 vs 0.077 for inliers)
- Outliers represent protocol diversity (study's explicit purpose)
- Keeping them enables testing marker robustness across forensically realistic conditions

**What requires validation**:
- Whether 74% vs 2% concordance pattern holds under formal statistical analysis
- Whether pattern generalizes across cohorts (KJENS/TTUSC)
- Whether Tier 1/Tier 2 classification is reproducible

This is exploratory analysis informing next steps, not final marker selection.

---

**Analysis Pipeline**: `analysis/llaur_outlier_interrogation.py`
**Visualizations**: `results/outlier_analysis/EXR-LLAUR1AVB5CS-AN/`
**Decision Matrix**: `decision_matrix.json`