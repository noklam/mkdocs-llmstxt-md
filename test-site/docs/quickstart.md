# Quick Start Guide

Get started with the LLMsTxt plugin in just a few steps.

## Installation

1. Install the plugin:
   ```bash
   pip install mkdocs-llms-txt
   ```

2. Add to your `mkdocs.yml`:
   ```yaml
   plugins:
     - llms-txt:
         sections:
           "Documentation":
             - "*.md"
   ```

3. Build your site:
   ```bash
   mkdocs build
   ```

## Verification

After building, you should have:

- `llms.txt` - Index file for LLMs
- `llms-full.txt` - Complete documentation  
- `.md` files alongside HTML pages
- Copy button on each page

## Next Steps

- Check the [installation guide](installation.md) for advanced setup
- Review the [API reference](api/overview.md) for detailed configuration