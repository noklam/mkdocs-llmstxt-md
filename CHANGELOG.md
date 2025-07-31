# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-07-31

### Added
- Initial release of mkdocs-llmstxt-md plugin
- Generate `llms.txt` index file with markdown URLs for LLM consumption
- Generate `llms-full.txt` with complete documentation in single file
- Serve original markdown files at `.md` URLs alongside HTML versions
- Copy-to-markdown button functionality on documentation pages
- Support for glob patterns in section configuration
- Theme-aware positioning for copy button
- Configurable sections with file descriptions

### Features
- **Markdown URL serving**: Access original markdown content at `.md` URLs
- **LLM-friendly indexes**: Auto-generated `llms.txt` and `llms-full.txt` files
- **Copy functionality**: One-click copy of markdown content to clipboard
- **Flexible configuration**: Glob patterns and custom descriptions
- **Theme compatibility**: Works with Material, MkDocs, ReadTheDocs themes

### Configuration Options
- `enable_markdown_urls`: Enable/disable `.md` URL serving
- `enable_llms_txt`: Enable/disable `llms.txt` generation
- `enable_llms_full`: Enable/disable `llms-full.txt` generation
- `enable_copy_button`: Enable/disable copy button injection
- `copy_button_text`: Customizable button text
- `copy_button_position`: Configurable button positioning
- `copy_button_style`: Customizable button styling
- `markdown_description`: Optional description for llms.txt header

[0.1.0]: https://github.com/noklam/mkdocs-llmstxt-md/releases/tag/v0.1.0