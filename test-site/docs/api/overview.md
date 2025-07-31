# API Overview

The LLMsTxt plugin provides a comprehensive API for customizing LLM-friendly documentation generation.

## Plugin Configuration

The plugin accepts the following configuration options:

### Core Options

- `sections` (dict): Maps section names to file patterns
- `enable_markdown_urls` (bool): Enable .md URL serving (default: true)
- `enable_llms_txt` (bool): Generate llms.txt (default: true)
- `enable_llms_full` (bool): Generate llms-full.txt (default: true)
- `enable_copy_button` (bool): Add copy button (default: true)

### UI Options

- `copy_button_text` (str): Text for copy button (default: "Copy Markdown")
- `markdown_description` (str): Optional description for llms.txt

## File Patterns

File patterns support glob syntax:

```yaml
sections:
  "API Reference":
    - api/*.md          # All .md files in api/
    - api/**/*.md       # All .md files in api/ and subdirectories
    - specific-file.md  # Single specific file
```

## Generated Files

The plugin generates:

1. **llms.txt** - Concise index with links to markdown versions
2. **llms-full.txt** - Complete documentation content
3. **Individual .md files** - Original markdown served at page.md URLs