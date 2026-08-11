CONFIG ?= config.json
ENV_FILE ?= .env

UV := $(shell command -v uv 2>/dev/null)

uv:
	@if command -v uv >/dev/null 2>&1; then \
		echo "uv is already installed: $$(uv --version)"; \
	else \
		echo "uv not found. Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		echo "uv installed. Please restart your shell and run 'make install' again."; \
		exit 1; \
	fi

install: uv
	uv sync
	$(MAKE) env

env:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "Creating $(ENV_FILE)..."; \
		printf '%s\n' \
			'PYTHONUNBUFFERED=1' \
			'PYTHONDONTWRITEBYTECODE=1' \
			> "$(ENV_FILE)"; \
	else \
		echo "$(ENV_FILE) already exists."; \
	fi

run: install
	uv run pac-man.py $(CONFIG)

debug: install
	uv run -m pdb pac-man.py $(CONFIG)

test: install
	uv run pytest tests/

lint: install
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs

lint-strict: install
	uv run flake8 .
	uv run mypy . --strict

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache

.PHONY: install run debug clean lint lint-strict test env uv