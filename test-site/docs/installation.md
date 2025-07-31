# Installation Guide

Detailed installation and configuration instructions.

## Requirements

- Python 3.8+
- MkDocs 1.4+

## Installation Methods

### PyPI (Recommended)

```bash
pip install mkdocs-llms-txt
```

### Development Install

```bash
git clone https://github.com/yourusername/mkdocs-llms-txt
cd mkdocs-llms-txt
pip install -e .
```

## Configuration

### Basic Configuration

```yaml
plugins:
  - llms-txt:
      sections:
        "Getting Started":
          - index.md
          - quickstart.md
```

### Advanced Configuration

```yaml
plugins:
  - llms-txt:
      enable_markdown_urls: true
      enable_llms_txt: true  
      enable_llms_full: true
      enable_copy_button: true
      copy_button_text: "Copy Markdown"
      markdown_description: "Custom description for llms.txt"
      sections:
        "API Documentation":
          - api/*.md
        "Tutorials":
          - tutorials/basic.md: "Basic tutorial"
          - tutorials/advanced.md: "Advanced concepts"
```

## Troubleshooting

Common issues and solutions:

- **Missing site_url**: Ensure `site_url` is set in your MkDocs config
- **Files not found**: Check that file patterns match your actual files
- **Copy button not working**: Verify JavaScript is enabled in your browser