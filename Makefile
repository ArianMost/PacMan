.PHONY: install run debug clean lint lint-strict test

CONFIG ?= config.json

install:
	uv sync

run:
	uv run pac-man.py $(CONFIG)

debug:
	uv run -m pdb pac-man.py $(CONFIG)

test:
	uv run pytest tests/

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache