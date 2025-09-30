#!/usr/bin/env Rscript
# Cross-cohort harmonization with ComBat batch correction
# Purpose: Merge TMM-normalized log2-CPM matrices and apply batch correction
#          to enable LODO validation across datasets

library(sva)

# Dataset identifiers
datasets <- c(
  "EXR-KJENS1RID1-AN",
  "EXR-TTUSC1gCrGDH-AN",
  "EXR-LLAUR1AVB5CS-AN"
)

base_dir <- file.path("results", "derived")
out_dir <- file.path(base_dir, "cross_cohort")
if (!dir.exists(out_dir)) dir.create(out_dir, recursive = TRUE)

cat("Loading TMM-normalized log2-CPM matrices...\n")

# Load each dataset's TMM-normalized expression and metadata
expr_list <- list()
meta_list <- list()

for (dataset_id in datasets) {
  cat("  Loading", dataset_id, "...\n")

  # Load TMM log2-CPM
  tmm_file <- file.path(base_dir, dataset_id, "differential_expression", "tmm_log2cpm.tsv")
  expr <- read.delim(tmm_file, row.names = 1, check.names = FALSE)

  # Load metadata (from parent directory, not filtered subdirectory)
  meta_file <- file.path(base_dir, dataset_id, "sample_metadata.tsv")
  meta <- read.delim(meta_file, row.names = 1, check.names = FALSE)

  # Align samples (intersection of expr columns and meta rows)
  shared_samples <- intersect(colnames(expr), rownames(meta))
  expr <- expr[, shared_samples]
  meta <- meta[shared_samples, ]

  # Add dataset ID to metadata
  meta$dataset_id <- dataset_id

  expr_list[[dataset_id]] <- expr
  meta_list[[dataset_id]] <- meta
}

# Find miRNA intersection across all datasets
cat("\nFinding miRNA intersection...\n")
miRNA_intersection <- Reduce(intersect, lapply(expr_list, rownames))
cat("  Shared miRNAs:", length(miRNA_intersection), "\n")

# Subset to shared miRNAs
expr_list <- lapply(expr_list, function(x) x[miRNA_intersection, ])

# Merge expression matrices
cat("\nMerging expression matrices...\n")
expr_merged <- do.call(cbind, expr_list)

# Find common metadata columns before merging
common_cols <- Reduce(intersect, lapply(meta_list, colnames))
cat("  Common metadata columns:", paste(common_cols, collapse = ", "), "\n")

# Subset metadata to common columns
meta_list <- lapply(meta_list, function(x) x[, common_cols])
meta_merged <- do.call(rbind, meta_list)

cat("  Combined dimensions:", nrow(expr_merged), "miRNAs x", ncol(expr_merged), "samples\n")

# Save pre-correction matrix
cat("\nSaving pre-correction matrix...\n")
write.table(
  cbind(miRNA = rownames(expr_merged), expr_merged),
  file.path(out_dir, "tmm_log2cpm_merged.tsv"),
  sep = "\t", quote = FALSE, row.names = FALSE
)
write.table(
  cbind(sample_id = rownames(meta_merged), meta_merged),
  file.path(out_dir, "sample_metadata_merged.tsv"),
  sep = "\t", quote = FALSE, row.names = FALSE
)

# PCA before batch correction
cat("\nComputing PCA (pre-correction)...\n")
pca_before <- prcomp(t(expr_merged), scale. = TRUE)
variance_before <- (pca_before$sdev^2 / sum(pca_before$sdev^2)) * 100

# Prepare batch correction
cat("\nPreparing ComBat batch correction...\n")
batch <- factor(meta_merged$dataset_id)
biofluid <- factor(meta_merged$biofluid)

# Create model matrix to preserve biofluid effects
mod <- model.matrix(~ biofluid)

cat("  Batch levels:", levels(batch), "\n")
cat("  Biofluid levels:", levels(biofluid), "\n")

# Apply ComBat
cat("\nApplying ComBat batch correction...\n")
expr_corrected <- ComBat(
  dat = as.matrix(expr_merged),
  batch = batch,
  mod = mod,
  par.prior = TRUE,
  prior.plots = FALSE
)

# PCA after batch correction
cat("\nComputing PCA (post-correction)...\n")
pca_after <- prcomp(t(expr_corrected), scale. = TRUE)
variance_after <- (pca_after$sdev^2 / sum(pca_after$sdev^2)) * 100

# Save batch-corrected matrix
cat("\nSaving batch-corrected matrix...\n")
write.table(
  cbind(miRNA = rownames(expr_corrected), expr_corrected),
  file.path(out_dir, "tmm_log2cpm_batch_corrected.tsv"),
  sep = "\t", quote = FALSE, row.names = FALSE
)

# Save PCA coordinates
pca_coords_before <- data.frame(
  sample_id = rownames(pca_before$x),
  pca_before$x[, 1:10],
  check.names = FALSE
)
write.table(
  pca_coords_before,
  file.path(out_dir, "pca_coordinates_before.tsv"),
  sep = "\t", quote = FALSE, row.names = FALSE
)

pca_coords_after <- data.frame(
  sample_id = rownames(pca_after$x),
  pca_after$x[, 1:10],
  check.names = FALSE
)
write.table(
  pca_coords_after,
  file.path(out_dir, "pca_coordinates_after.tsv"),
  sep = "\t", quote = FALSE, row.names = FALSE
)

# Save variance explained
variance_df <- data.frame(
  PC = paste0("PC", 1:10),
  variance_before = variance_before[1:10],
  variance_after = variance_after[1:10]
)
write.table(
  variance_df,
  file.path(out_dir, "pca_variance_comparison.tsv"),
  sep = "\t", quote = FALSE, row.names = FALSE
)

# Generate diagnostic plots
cat("\nGenerating diagnostic plots...\n")
pdf(file.path(out_dir, "batch_correction_diagnostics.pdf"), width = 12, height = 6)

# Before correction
par(mfrow = c(1, 2))
plot(
  pca_before$x[, 1], pca_before$x[, 2],
  col = as.numeric(batch),
  pch = 19,
  xlab = sprintf("PC1 (%.1f%%)", variance_before[1]),
  ylab = sprintf("PC2 (%.1f%%)", variance_before[2]),
  main = "Before Batch Correction (colored by dataset)"
)
legend("topright", legend = levels(batch), col = 1:3, pch = 19, cex = 0.8)

plot(
  pca_before$x[, 1], pca_before$x[, 2],
  col = as.numeric(biofluid),
  pch = 19,
  xlab = sprintf("PC1 (%.1f%%)", variance_before[1]),
  ylab = sprintf("PC2 (%.1f%%)", variance_before[2]),
  main = "Before Batch Correction (colored by biofluid)"
)
legend("topright", legend = levels(biofluid), col = 1:length(levels(biofluid)), pch = 19, cex = 0.8)

# After correction
plot(
  pca_after$x[, 1], pca_after$x[, 2],
  col = as.numeric(batch),
  pch = 19,
  xlab = sprintf("PC1 (%.1f%%)", variance_after[1]),
  ylab = sprintf("PC2 (%.1f%%)", variance_after[2]),
  main = "After Batch Correction (colored by dataset)"
)
legend("topright", legend = levels(batch), col = 1:3, pch = 19, cex = 0.8)

plot(
  pca_after$x[, 1], pca_after$x[, 2],
  col = as.numeric(biofluid),
  pch = 19,
  xlab = sprintf("PC1 (%.1f%%)", variance_after[1]),
  ylab = sprintf("PC2 (%.1f%%)", variance_after[2]),
  main = "After Batch Correction (colored by biofluid)"
)
legend("topright", legend = levels(biofluid), col = 1:length(levels(biofluid)), pch = 19, cex = 0.8)

dev.off()

# Save summary statistics
summary_stats <- list(
  n_miRNAs = nrow(expr_corrected),
  n_samples = ncol(expr_corrected),
  datasets = as.character(unique(batch)),
  samples_per_dataset = as.list(table(batch)),
  biofluids = as.character(unique(biofluid)),
  samples_per_biofluid = as.list(table(biofluid)),
  variance_explained = list(
    before_correction = list(
      PC1 = variance_before[1],
      PC2 = variance_before[2]
    ),
    after_correction = list(
      PC1 = variance_after[1],
      PC2 = variance_after[2]
    )
  )
)

cat("\n=== Batch Correction Summary ===\n")
cat("miRNAs:", summary_stats$n_miRNAs, "\n")
cat("Samples:", summary_stats$n_samples, "\n")
cat("\nSamples per dataset:\n")
print(summary_stats$samples_per_dataset)
cat("\nSamples per biofluid:\n")
print(summary_stats$samples_per_biofluid)
cat("\nPC1 variance explained:\n")
cat("  Before:", sprintf("%.1f%%", variance_before[1]), "\n")
cat("  After:", sprintf("%.1f%%", variance_after[1]), "\n")
cat("\nPC2 variance explained:\n")
cat("  Before:", sprintf("%.1f%%", variance_before[2]), "\n")
cat("  After:", sprintf("%.1f%%", variance_after[2]), "\n")

# Save JSON summary
library(jsonlite)
write_json(
  summary_stats,
  file.path(out_dir, "batch_correction_summary.json"),
  pretty = TRUE,
  auto_unbox = TRUE
)

cat("\nBatch correction complete. Outputs saved to:", out_dir, "\n")