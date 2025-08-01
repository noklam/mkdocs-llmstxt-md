# API Functions

Detailed reference for the plugin's internal functions and methods.

## LlmsTxtPlugin Class

Main plugin class that handles all functionality.

### Methods

#### `__init__()`
Initialize the plugin with empty state.

#### `on_config(config: MkDocsConfig) -> MkDocsConfig`
Process MkDocs configuration and validate settings.

**Parameters:**
- `config`: MkDocs configuration object

**Returns:**
- Modified or original config

**Raises:**
- `ValueError`: If site_url is not configured

#### `on_files(files: Files, *, config: MkDocsConfig) -> Files`
Process files and expand glob patterns in sections.

**Parameters:**
- `files`: Collection of MkDocs files
- `config`: MkDocs configuration

**Returns:**
- Modified or original files collection

#### `on_page_markdown(markdown: str, *, page: Page, config: MkDocsConfig, files: Files) -> str`
Store original markdown content for processing.

**Parameters:**
- `markdown`: Original markdown content
- `page`: Current page object
- `config`: MkDocs configuration
- `files`: Files collection

**Returns:**
- Unmodified markdown content

#### `on_page_content(html: str, *, page: Page, config: MkDocsConfig, files: Files) -> str`
Inject copy button into page HTML if enabled.

**Parameters:**
- `html`: Rendered HTML content
- `page`: Current page object
- `config`: MkDocs configuration
- `files`: Files collection

**Returns:**
- Modified HTML with copy button or original HTML

#### `on_post_build(*, config: MkDocsConfig) -> None`
Generate all output files (llms.txt, llms-full.txt, .md files).

**Parameters:**
- `config`: MkDocs configuration

## Helper Functions

### `_generate_markdown_files(site_dir: Path) -> None`
Generate individual .md files for each page.

### `_generate_llms_txt(site_dir: Path, config: MkDocsConfig) -> None`
Generate the llms.txt index file.

### `_generate_llms_full_txt(site_dir: Path, config: MkDocsConfig) -> None`
Generate the complete llms-full.txt file.

### `_get_copy_button_html() -> str`
Generate HTML/CSS/JavaScript for the copy button.