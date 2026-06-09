PYTHON = python3
MAIN = pac-man.py
CONFIG = config.json
VENV = .venv
DEPS_STAMP = $(VENV)/.deps-installed
.DEFAULT_GOAL = help

help:
	@echo "Usage: make <target>"
	@echo "  install - Install/sync dependencies from pyproject.toml + uv.lock"
	@echo "  run - Run program without reinstalling dependencies each time"
	@echo "  debug - Run with pdb debugger"
	@echo "  build - Build wheel and .tar.gz distributions"
	@echo "  lint - Run flake8 and mypy"
	@echo "  lint-strict - Run flake8 and mypy --strict"
	@echo "  lint-strict2 - Run flake8 and mypy --strict --ignore-missing-imports"
	@echo "  clean - Remove cache files"

install:
	UV_SKIP_WHEEL_FILENAME_CHECK=1 uv sync --frozen --link-mode=copy
	@touch $(DEPS_STAMP)

$(DEPS_STAMP): pyproject.toml uv.lock
	UV_SKIP_WHEEL_FILENAME_CHECK=1 uv sync --frozen --link-mode=copy
	@touch $(DEPS_STAMP)

run: $(DEPS_STAMP)
	$(VENV)/bin/python $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

build:
	uv build

lint:
	flake8 .
	mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

lint-strict2:
	flake8 .
	mypy . --ignore-missing-imports --strict

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

clean-env:
	rm -f $(DEPS_STAMP)
	rm -rf $(VENV)

.PHONY: install run debug build lint lint-strict lint-strict2 clean clean-env
