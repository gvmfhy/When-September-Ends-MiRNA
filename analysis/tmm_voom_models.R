#!/usr/bin/env Rscript
#
# TMM normalization + limma-voom differential expression for exRNA cohorts
#
# For each dataset (KJENS, TTUSC, LLAUR):
#   1. Load filtered counts and metadata
#   2. Build DGEList and calculate TMM normalization factors
#   3. Apply voom transformation to model mean-variance relationship
#   4. Fit limma models for each biofluid (target vs. rest)
#   5. Extract logFC, moderated statistics, and AUC estimates
#   6. Export results to results/derived/<EXR-ID>/differential_expression/
#
# This follows standard RNA-seq best practices for count-based differential
# expression with empirical Bayes moderation.

suppressPackageStartupMessages({
  library(edgeR)
  library(limma)
})

# Directory structure
# Get script location and derive project root
script_path <- commandArgs(trailingOnly = FALSE)
script_path <- sub("^--file=", "", script_path[grep("^--file=", script_path)])
if (length(script_path) > 0) {
  ROOT <- normalizePath(file.path(dirname(script_path), ".."))
} else {
  # Fallback: assume we're running from analysis/ directory
  ROOT <- normalizePath("..")
}
RESULTS <- file.path(ROOT, "results", "derived")

# Dataset configurations
datasets <- list(
  list(
    id = "EXR-KJENS1RID1-AN",
    name = "KJENS",
    fluids = c("Plasma", "Saliva", "Urine")
  ),
  list(
    id = "EXR-TTUSC1gCrGDH-AN",
    name = "TTUSC",
    fluids = c("Plasma", "Serum")
  ),
  list(
    id = "EXR-LLAUR1AVB5CS-AN",
    name = "LLAUR",
    fluids = c("plasma", "saliva", "urine", "serum", "csf")
  )
)

#' Load filtered counts and metadata for a dataset
load_dataset <- function(dataset_id) {
  filtered_dir <- file.path(RESULTS, dataset_id, "filtered")
  parent_dir <- file.path(RESULTS, dataset_id)

  counts_path <- file.path(filtered_dir, "miRNA_counts.filtered.tsv")

  # Try filtered metadata first, fall back to parent directory
  metadata_path_filtered <- file.path(filtered_dir, "sample_metadata.filtered.tsv")
  metadata_path_unfiltered <- file.path(parent_dir, "sample_metadata.tsv")

  if (!file.exists(counts_path)) {
    stop(sprintf("Counts file not found: %s", counts_path))
  }

  counts <- read.table(counts_path, header = TRUE, sep = "\t",
                       row.names = 1, check.names = FALSE)

  # Load metadata from whichever location exists
  if (file.exists(metadata_path_filtered)) {
    metadata_path <- metadata_path_filtered
  } else if (file.exists(metadata_path_unfiltered)) {
    metadata_path <- metadata_path_unfiltered
  } else {
    stop(sprintf("Metadata file not found in %s or %s",
                 metadata_path_filtered, metadata_path_unfiltered))
  }

  metadata <- read.table(metadata_path, header = TRUE, sep = "\t",
                         row.names = 1, check.names = FALSE,
                         stringsAsFactors = FALSE)

  # Filter metadata to only samples present in filtered counts
  common_samples <- intersect(rownames(metadata), colnames(counts))
  metadata <- metadata[common_samples, , drop = FALSE]
  counts <- counts[, common_samples, drop = FALSE]

  list(counts = as.matrix(counts), metadata = metadata)
}

#' Save reproducibility manifest with script hash and session info
save_reproducibility_manifest <- function(out_dir, dataset_id) {
  # Get script path
  script_path_args <- commandArgs(trailingOnly = FALSE)
  script_file <- sub("^--file=", "", script_path_args[grep("^--file=", script_path_args)])

  if (length(script_file) == 0) {
    script_file <- file.path(ROOT, "analysis", "tmm_voom_models.R")
  }

  # Calculate script hash (SHA256)
  script_hash <- NA
  if (file.exists(script_file)) {
    script_hash <- as.character(tools::md5sum(script_file))
  }

  # Capture session info
  si <- sessionInfo()

  # Build manifest
  manifest <- list(
    script = list(
      name = basename(script_file),
      path = normalizePath(script_file, mustWork = FALSE),
      md5_hash = script_hash,
      run_timestamp = format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z")
    ),
    dataset = list(
      id = dataset_id,
      analysis_type = "TMM normalization + limma-voom differential expression"
    ),
    r_environment = list(
      r_version = paste(si$R.version$major, si$R.version$minor, sep = "."),
      platform = si$platform,
      running = si$running,
      locale = si$locale,
      base_packages = unname(si$basePkgs),
      loaded_packages = lapply(si$otherPkgs, function(pkg) {
        list(
          package = pkg$Package,
          version = as.character(pkg$Version),
          date = as.character(pkg$Date)
        )
      })
    ),
    input_data = list(
      counts_file = "filtered/miRNA_counts.filtered.tsv",
      metadata_file = "sample_metadata.tsv"
    ),
    methods = list(
      normalization = "TMM (edgeR::calcNormFactors)",
      transformation = "voom with precision weights",
      differential_expression = "limma::lmFit + eBayes",
      multiple_testing_correction = "Benjamini-Hochberg FDR",
      top_marker_selection = "Highest AUC among miRNAs with logFC>0 and adj.P.Val<0.05"
    ),
    outputs = list(
      differential_expression_tables = TRUE,
      tmm_normalized_cpm = TRUE,
      summary_statistics = TRUE
    )
  )

  # Write manifest
  manifest_file <- file.path(out_dir, "reproducibility.json")
  writeLines(jsonlite::toJSON(manifest, pretty = TRUE, auto_unbox = TRUE),
             manifest_file)

  # Also save full sessionInfo as text
  session_file <- file.path(out_dir, "sessionInfo.txt")
  capture.output(print(si), file = session_file)

  return(invisible(manifest))
}

#' Calculate AUC for a given miRNA across two groups
calculate_auc <- function(values, group) {
  require(stats)

  pos_vals <- values[group == 1]
  neg_vals <- values[group == 0]

  if (length(pos_vals) < 2 || length(neg_vals) < 2) {
    return(NA_real_)
  }

  # Wilcoxon rank-sum statistic normalized to [0,1]
  w <- wilcox.test(pos_vals, neg_vals, exact = FALSE)$statistic
  auc <- w / (length(pos_vals) * length(neg_vals))

  return(as.numeric(auc))
}

#' Run TMM + voom + limma for one dataset
run_differential_expression <- function(dataset_config) {
  cat(sprintf("\n=== Processing %s ===\n", dataset_config$id))

  # Load data
  data <- load_dataset(dataset_config$id)
  counts <- data$counts
  metadata <- data$metadata

  cat(sprintf("Loaded %d miRNAs × %d samples\n", nrow(counts), ncol(counts)))

  # Check biofluid column
  if (!"biofluid" %in% colnames(metadata)) {
    stop("Metadata missing 'biofluid' column")
  }

  # Identify present biofluids (case-insensitive match with expected fluids)
  present_fluids <- unique(metadata$biofluid)
  present_fluids <- present_fluids[!is.na(present_fluids) & present_fluids != "Unknown"]

  # Normalize fluid names for matching
  normalize_fluid <- function(x) tolower(trimws(x))
  expected_normalized <- normalize_fluid(dataset_config$fluids)
  present_normalized <- normalize_fluid(present_fluids)

  # Match present fluids to expected
  matched_fluids <- present_fluids[present_normalized %in% expected_normalized]

  if (length(matched_fluids) < 2) {
    cat(sprintf("  WARNING: Only %d biofluid(s) found, skipping DE analysis\n",
                length(matched_fluids)))
    return(NULL)
  }

  cat(sprintf("  Biofluids detected: %s\n", paste(matched_fluids, collapse = ", ")))

  # Filter out samples with zero library size or NA biofluid before creating DGEList
  lib_sizes <- colSums(counts)
  valid_samples <- lib_sizes > 0 & !is.na(metadata$biofluid)

  if (sum(!valid_samples) > 0) {
    cat(sprintf("  Removing %d samples with zero counts or missing biofluid\n",
                sum(!valid_samples)))
    counts <- counts[, valid_samples, drop = FALSE]
    metadata <- metadata[valid_samples, , drop = FALSE]
  }

  # Create DGEList
  dge <- DGEList(counts = counts, samples = metadata)

  # Calculate TMM normalization factors
  dge <- calcNormFactors(dge, method = "TMM")

  cat(sprintf("  TMM factors: min=%.3f, median=%.3f, max=%.3f\n",
              min(dge$samples$norm.factors),
              median(dge$samples$norm.factors),
              max(dge$samples$norm.factors)))

  # Prepare output directory
  out_dir <- file.path(RESULTS, dataset_config$id, "differential_expression")
  dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

  # Export TMM-normalized CPM for reference
  tmm_cpm <- cpm(dge, log = FALSE, normalized.lib.sizes = TRUE)
  tmm_log2cpm <- cpm(dge, log = TRUE, normalized.lib.sizes = TRUE, prior.count = 1)

  write.table(tmm_cpm,
              file = file.path(out_dir, "tmm_cpm.tsv"),
              sep = "\t", quote = FALSE, col.names = NA)
  write.table(tmm_log2cpm,
              file = file.path(out_dir, "tmm_log2cpm.tsv"),
              sep = "\t", quote = FALSE, col.names = NA)

  # Run differential expression for each biofluid vs. rest
  all_results <- list()

  for (target_fluid in matched_fluids) {
    cat(sprintf("  Running DE: %s vs. rest\n", target_fluid))

    # Create binary group vector (case-insensitive match)
    group <- ifelse(normalize_fluid(metadata$biofluid) == normalize_fluid(target_fluid), 1, 0)
    n_target <- sum(group == 1)
    n_rest <- sum(group == 0)

    cat(sprintf("    Target n=%d, Rest n=%d\n", n_target, n_rest))

    if (n_target < 3 || n_rest < 3) {
      cat("    WARNING: Insufficient samples, skipping\n")
      next
    }

    # Design matrix
    design <- model.matrix(~ group)
    colnames(design) <- c("Intercept", "TargetVsRest")

    # voom transformation
    v <- voom(dge, design, plot = FALSE)

    # Fit linear model
    fit <- lmFit(v, design)
    fit <- eBayes(fit)

    # Extract results
    results <- topTable(fit, coef = "TargetVsRest", number = Inf, sort.by = "none")

    # Calculate AUC for each miRNA
    auc_values <- sapply(rownames(v$E), function(mirna) {
      calculate_auc(v$E[mirna, ], group)
    })

    results$AUC <- auc_values[rownames(results)]

    # Add metadata columns
    results$biofluid <- target_fluid
    results$n_target <- n_target
    results$n_rest <- n_rest
    results$miRNA <- rownames(results)

    # Reorder columns for clarity
    results <- results[, c("miRNA", "biofluid", "logFC", "AveExpr", "t",
                           "P.Value", "adj.P.Val", "B", "AUC",
                           "n_target", "n_rest")]

    # Save per-fluid results
    fluid_safe <- gsub("[^A-Za-z0-9]", "_", target_fluid)
    outfile <- file.path(out_dir, sprintf("de_%s_vs_rest.tsv", fluid_safe))
    write.table(results, file = outfile, sep = "\t",
                quote = FALSE, row.names = FALSE)

    cat(sprintf("    Saved: %s\n", basename(outfile)))
    cat(sprintf("    Significant (FDR<0.05): %d miRNAs\n",
                sum(results$adj.P.Val < 0.05, na.rm = TRUE)))

    # Store in combined list
    all_results[[target_fluid]] <- results
  }

  # Combine all results into a single table
  if (length(all_results) > 0) {
    combined <- do.call(rbind, all_results)
    combined_file <- file.path(out_dir, "de_all_fluids.tsv")
    write.table(combined, file = combined_file, sep = "\t",
                quote = FALSE, row.names = FALSE)

    cat(sprintf("  Combined results: %s\n", basename(combined_file)))
  }

  # Summary statistics
  summary_file <- file.path(out_dir, "summary.json")

  # Helper function to select top marker
  select_top_marker <- function(res) {
    # Prefer highest AUC among upregulated significant miRNAs
    upregulated_sig <- res[res$logFC > 0 & res$adj.P.Val < 0.05 & !is.na(res$AUC), ]

    if (nrow(upregulated_sig) > 0) {
      top_idx <- which.max(upregulated_sig$AUC)
      list(
        miRNA = upregulated_sig$miRNA[top_idx],
        logFC = upregulated_sig$logFC[top_idx],
        AUC = upregulated_sig$AUC[top_idx],
        adj_P_Val = upregulated_sig$adj.P.Val[top_idx],
        selection_criteria = "highest AUC among upregulated (logFC>0, FDR<0.05)"
      )
    } else {
      # Fallback: most significant by FDR regardless of direction
      top_idx <- which.min(res$adj.P.Val)
      list(
        miRNA = res$miRNA[top_idx],
        logFC = res$logFC[top_idx],
        AUC = ifelse(!is.na(res$AUC[top_idx]), res$AUC[top_idx], NA),
        adj_P_Val = res$adj.P.Val[top_idx],
        selection_criteria = "lowest FDR (no upregulated significant markers)"
      )
    }
  }

  summary <- list(
    dataset_id = dataset_config$id,
    n_miRNAs = nrow(counts),
    n_samples = ncol(counts),
    biofluids_tested = matched_fluids,
    tmm_factor_range = range(dge$samples$norm.factors),
    top_marker_selection_criteria = "Highest AUC among miRNAs with logFC>0 and FDR<0.05; fallback to lowest FDR if none upregulated",
    analyses = lapply(names(all_results), function(fluid) {
      res <- all_results[[fluid]]
      top_marker <- select_top_marker(res)

      list(
        biofluid = fluid,
        n_target = unique(res$n_target),
        n_rest = unique(res$n_rest),
        n_significant_fdr05 = sum(res$adj.P.Val < 0.05, na.rm = TRUE),
        n_logFC_gt2 = sum(abs(res$logFC) > 2, na.rm = TRUE),
        n_upregulated_sig = sum(res$logFC > 0 & res$adj.P.Val < 0.05, na.rm = TRUE),
        top_marker = top_marker
      )
    })
  )

  writeLines(jsonlite::toJSON(summary, pretty = TRUE, auto_unbox = TRUE),
             summary_file)

  cat(sprintf("  Summary: %s\n", basename(summary_file)))

  # Save reproducibility manifest
  save_reproducibility_manifest(out_dir, dataset_config$id)
  cat(sprintf("  Reproducibility manifest: reproducibility.json\n"))

  return(all_results)
}

# Main execution
cat("TMM + voom differential expression pipeline\n")
cat("===========================================\n")

# Check jsonlite availability for summary export
if (!require(jsonlite, quietly = TRUE)) {
  cat("Installing jsonlite for JSON export...\n")
  install.packages("jsonlite", repos = "https://cloud.r-project.org", quiet = TRUE)
  library(jsonlite)
}

# Process each dataset
results <- lapply(datasets, function(ds) {
  tryCatch({
    run_differential_expression(ds)
  }, error = function(e) {
    cat(sprintf("\nERROR processing %s: %s\n", ds$id, e$message))
    return(NULL)
  })
})

cat("\n=== Pipeline complete ===\n")
cat("Results saved under results/derived/<EXR-ID>/differential_expression/\n")