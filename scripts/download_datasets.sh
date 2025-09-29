#!/usr/bin/env bash
set -euo pipefail

TARGET_ROOT=${1:-data}
RAW_DIR="${TARGET_ROOT%/}/raw"
PROC_DIR="${TARGET_ROOT%/}/processed"
META_DIR="${TARGET_ROOT%/}/meta"

mkdir -p "$RAW_DIR" "$PROC_DIR" "$META_DIR"

log() {
  printf '[download] %s\n' "$1"
}

fetch() {
  local url="$1"
  local dest="$2"
  local label="$3"

  if [ -f "$dest" ]; then
    log "Skipping $label (already exists)"
    return
  fi

  log "Fetching $label"
  curl -fsSL "$url" -o "$dest"
}

# --- GEO / public datasets ---
fetch "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE153135&format=file&file=GSE153135_series_matrix.txt.gz" \
      "$PROC_DIR/GSE153135_series_matrix.txt.gz" \
      "GSE153135 processed matrix"

fetch "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE153135&format=file&file=GSE153135_RAW.tar" \
      "$RAW_DIR/GSE153135_RAW.tar" \
      "GSE153135 raw archive"

fetch "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE49630&format=file&file=GSE49630_series_matrix.txt.gz" \
      "$PROC_DIR/GSE49630_series_matrix.txt.gz" \
      "GSE49630 processed matrix"

fetch "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE49630&format=file&file=GSE49630_RAW.tar" \
      "$RAW_DIR/GSE49630_RAW.tar" \
      "GSE49630 raw archive"

fetch "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE85830&format=file&file=GSE85830_miR_NGS_read_Data_-_all_32_body_fluids.csv.gz" \
      "$PROC_DIR/GSE85830_processed_counts.csv.gz" \
      "GSE85830 processed counts"

fetch "https://www.ncbi.nlm.nih.gov/geo/download/?acc=GSE85830&format=file&file=GSE85830_series_matrix.txt.gz" \
      "$META_DIR/GSE85830_series_matrix.txt.gz" \
      "GSE85830 series matrix"

log "Note: raw FASTQ files for GSE85830 are available via the SRA Run Selector at https://www.ncbi.nlm.nih.gov/Traces/study/?acc=PRJNA339520"
log "      Use 'prefetch'/'fasterq-dump' (SRA Toolkit) or download mirrored FASTQs from ENA."

log "Datasets requiring registration (manual step):"
log "  - exRNA Atlas: register at https://www.exrna-atlas.org/exat/ to download processed counts."
log "  - ICPSR 38391: create an ICPSR account to download CSV bundles."
log "  - dbGaP phs001258: submit controlled-access request if needed."
log "  - ENA PRJEB83455: browse runs and fetch FASTQs as needed."
