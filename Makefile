.SHELL := /bin/bash

.PHONY: data data-py untar clean-downloads

DATA_ROOT ?= data

# Default download entry point (uses curl-based shell script)
data:
	./scripts/download_datasets.sh $(DATA_ROOT)

# Alternate downloader that uses Python's urllib stack
data-py:
	./scripts/download_datasets.py $(DATA_ROOT)

# Extract any *.tar archives in data/raw into per-archive directories untarred next to the tarball
untar:
	@if compgen -G "$(DATA_ROOT)/raw/*.tar" > /dev/null; then \
	  find $(DATA_ROOT)/raw -name '*.tar' -print0 | while IFS= read -r -d '' archive; do \
	    target="$${archive%.tar}"; \
	    echo "[untar ] $$archive -> $$target"; \
	    mkdir -p "$$target"; \
	    tar -xf "$$archive" -C "$$target"; \
	  done; \
	else \
	  echo "[untar ] no tar archives found under $(DATA_ROOT)/raw"; \
	fi

# Utility to remove downloaded artifacts (be careful!)
clean-downloads:
	rm -rf $(DATA_ROOT)/raw $(DATA_ROOT)/processed $(DATA_ROOT)/meta
