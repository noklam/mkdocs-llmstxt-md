# mkdocs-llmstxt-md

MkDocs plugin for LLM-friendly documentation that provides:

1. **Direct markdown serving** - Access original markdown at `page.md` URLs
2. **llms.txt generation** - Concise index file for LLM context
3. **llms-full.txt generation** - Complete documentation in single file
4. **Copy-to-markdown button** - Easy copying of source markdown

## Features

- 🚀 **Source-first approach** - Works with original markdown, no HTML parsing
- 🤖 **LLM optimized** - Token-efficient formats for AI consumption
- 📋 **Copy button** - One-click markdown copying for developers
- 🔗 **Dual URLs** - Both human-readable HTML and LLM-friendly markdown

This plugin is inspired by `mkdocs-llmstxt`, the key difference is that `mkdocs-llmstxt` take the parsing HTML approach which can be used with injected HTML. This plugin focus on the raw markdown approach, which makes things simpler if you only need to work with markdown content.
## Installation

```bash
uv pip install mkdocs-llmstxt-md
# or with pip
pip install mkdocs-llmstxt-md
```


## Usage

Add to your `mkdocs.yml`:

```yaml
plugins:
  - llms-txt:
      sections:
        "Getting Started":
          - index.md: "Introduction to the project"
          - quickstart.md
        "API Reference":
          - api/*.md
```

## Configuration

- `sections`: Dict of section names to file patterns
- `enable_markdown_urls`: Enable .md URL serving (default: true)
- `enable_llms_txt`: Generate llms.txt (default: true)
- `enable_llms_full`: Generate llms-full.txt (default: true)
- `enable_copy_button`: Add copy button to pages (default: true)

## Developer Setup

### Prerequisites

- Python 3.8+
- uv (recommended) or pip

### Installation for Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mkdocs-llmstxt-md
   ```

2. Install in development mode:
   ```bash
   uv pip install -e .
   # or with pip
   pip install -e .
   ```

3. Verify installation:
   ```bash
   uv pip list | grep mkdocs-llmstxt-md
   # or with pip
   pip list | grep mkdocs-llmstxt-md
   ```

### Testing with the Test Site

The project includes a complete test site in `test-site/` to validate all plugin features:

1. **Build the test site:**
   ```bash
   cd test-site
   mkdocs build
   ```

2. **Serve the test site locally:**
   ```bash
   mkdocs serve
   ```
   Visit http://localhost:8000 to see the documentation

3. **Validate generated files:**
   After building, check the `test-site/site/` directory for:
   - `llms.txt` - Index file with markdown URLs
   - `llms-full.txt` - Complete documentation
   - `*.md` files alongside HTML pages (e.g., `index.md`, `quickstart/index.md`)
   - Copy button on each page (top-right corner)

4. **Test markdown URL access:**
   - Visit http://localhost:8000/index.md to see raw markdown
   - Visit http://localhost:8000/quickstart/index.md for quickstart markdown
   - Compare with HTML versions at http://localhost:8000/ and http://localhost:8000/quickstart/

### Test Site Structure

The test site demonstrates all plugin features:

```
test-site/
├── mkdocs.yml          # Plugin configuration example
└── docs/
    ├── index.md        # Homepage with tables and code
    ├── quickstart.md   # Getting started guide
    ├── installation.md # Detailed setup instructions
    ├── api/
    │   ├── overview.md # API documentation
    │   └── functions.md# Function reference
    └── advanced/
        └── configuration.md # Advanced config examples
```

### Running Tests

Currently manual testing via the test site. Future versions will include automated tests.

### Making Changes

1. Modify code in `src/mkdocs_llms_txt/`
2. Test changes: `cd test-site && mkdocs build`
3. Validate all features work as expected
4. Check generated files in `test-site/site/`