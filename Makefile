.PHONY: help install lint format test serve build clean

help:
	@echo "Available commands:"
	@echo "  install    - Install the package in development mode"
	@echo "  lint       - Run ruff linting"
	@echo "  format     - Format code with ruff"
	@echo "  test       - Build test documentation and verify outputs"
	@echo "  serve      - Serve test documentation locally"
	@echo "  build      - Build test documentation"
	@echo "  clean      - Clean build artifacts"

install:
	uv pip install -e .

lint:
	ruff check --fix

format:
	ruff format

test: build
	@echo "Building test documentation..."
	cd test-site && mkdocs build
	@echo "Verifying generated files..."
	@test -f test-site/site/llms.txt || (echo "ERROR: llms.txt not found" && exit 1)
	@test -f test-site/site/llms-full.txt || (echo "ERROR: llms-full.txt not found" && exit 1)
	@echo "Test documentation built successfully!"

serve:
	cd test-site && mkdocs serve

build:
	cd test-site && mkdocs build

clean:
	rm -rf test-site/site/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/