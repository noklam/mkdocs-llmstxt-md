"""Main plugin class for LLMsTxt MkDocs plugin."""

import fnmatch
import mimetypes
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urljoin

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page

from .config import LLMsTxtConfig


class LLMsTxtPlugin(BasePlugin[LLMsTxtConfig]):
    """MkDocs plugin for LLM-friendly documentation."""

    def __init__(self):
        super().__init__()
        self.mkdocs_config: MkDocsConfig = None
        self.pages_data: Dict[str, List[Dict[str, Any]]] = {}
        self.source_files: Dict[str, str] = {}

    def on_config(self, config: MkDocsConfig) -> MkDocsConfig:
        """Store MkDocs configuration and validate settings."""
        if not config.site_url:
            raise ValueError(
                "site_url must be set in MkDocs config for llms-txt plugin"
            )

        # Configure MIME type for .md files so they display in browser instead of downloading
        if self.config.enable_markdown_urls:
            mimetypes.add_type("text/plain", ".md")

        self.mkdocs_config = config
        self.pages_data = {section: [] for section in self.config.sections.keys()}
        return config

    def on_files(self, files: Files, *, config: MkDocsConfig) -> Files:
        """Process files and expand glob patterns in sections."""
        all_src_paths = [f.src_uri for f in files]

        # Expand glob patterns in sections configuration
        for section_name, file_patterns in self.config.sections.items():
            if isinstance(file_patterns, list):
                for pattern in file_patterns:
                    if isinstance(pattern, dict):
                        file_path = list(pattern.keys())[0]
                        description = list(pattern.values())[0]
                    else:
                        file_path = pattern
                        description = ""

                    # Handle glob patterns
                    if "*" in file_path:
                        matches = fnmatch.filter(all_src_paths, file_path)
                        for match in matches:
                            if match not in [
                                p["src_uri"] for p in self.pages_data[section_name]
                            ]:
                                self.pages_data[section_name].append(
                                    {"src_uri": match, "description": description}
                                )
                    else:
                        if file_path in all_src_paths:
                            if file_path not in [
                                p["src_uri"] for p in self.pages_data[section_name]
                            ]:
                                self.pages_data[section_name].append(
                                    {"src_uri": file_path, "description": description}
                                )

        return files

    def on_page_markdown(
        self, markdown: str, *, page: Page, config: MkDocsConfig, files: Files
    ) -> str:
        """Store original markdown content for later use."""
        src_uri = page.file.src_uri

        # Check if this page is in any of our sections
        for _section_name, page_list in self.pages_data.items():
            for page_data in page_list:
                if page_data["src_uri"] == src_uri:
                    self.source_files[src_uri] = markdown
                    page_data.update(
                        {
                            "title": page.title or src_uri,
                            "markdown": markdown,
                            "dest_path": page.file.dest_path,
                            "dest_uri": page.file.dest_uri,
                        }
                    )
                    break

        return markdown

    def on_page_content(
        self, html: str, *, page: Page, config: MkDocsConfig, files: Files
    ) -> str:
        """Inject copy button if enabled."""
        if not self.config.enable_copy_button:
            return html

        src_uri = page.file.src_uri
        if src_uri in self.source_files:
            # Inject copy button HTML and JavaScript
            copy_button_html = self._get_copy_button_html(config)
            # Insert before closing body tag if present, otherwise at end
            if "</body>" in html:
                html = html.replace("</body>", f"{copy_button_html}</body>")
            else:
                html += copy_button_html

        return html

    def on_post_build(self, *, config: MkDocsConfig) -> None:
        """Generate llms.txt, llms-full.txt, and markdown files."""
        site_dir = Path(config.site_dir)

        # Generate individual markdown files if markdown URLs are enabled
        if self.config.enable_markdown_urls:
            self._generate_markdown_files(site_dir)

        # Generate llms.txt
        if self.config.enable_llms_txt:
            self._generate_llms_txt(site_dir, config)

        # Generate llms-full.txt
        if self.config.enable_llms_full:
            self._generate_llms_full_txt(site_dir, config)

    def _generate_markdown_files(self, site_dir: Path) -> None:
        """Generate individual .md files for each page."""
        for section_pages in self.pages_data.values():
            for page_data in section_pages:
                if "markdown" in page_data and "dest_path" in page_data:
                    # Create .md version alongside HTML
                    html_path = Path(page_data["dest_path"])
                    md_path = site_dir / html_path.with_suffix(".md")

                    # Ensure directory exists
                    md_path.parent.mkdir(parents=True, exist_ok=True)

                    # Write markdown content
                    md_path.write_text(page_data["markdown"], encoding="utf-8")

    def _generate_llms_txt(self, site_dir: Path, config: MkDocsConfig) -> None:
        """Generate the llms.txt index file."""
        llms_txt_path = site_dir / "llms.txt"

        content = f"# {config.site_name}\n\n"

        if config.site_description:
            content += f"> {config.site_description}\n\n"

        if self.config.markdown_description:
            content += f"{self.config.markdown_description}\n\n"

        base_url = config.site_url.rstrip("/")

        for section_name, pages in self.pages_data.items():
            if pages:  # Only add section if it has pages
                content += f"## {section_name}\n\n"

                for page_data in pages:
                    title = page_data.get("title", page_data["src_uri"])
                    dest_uri = page_data.get("dest_uri", "")
                    description = page_data.get("description", "")

                    # Create markdown URL
                    md_url = urljoin(
                        base_url + "/",
                        dest_uri.replace(".html", ".md")
                        if dest_uri.endswith(".html")
                        else dest_uri + ".md",
                    )

                    desc_text = f": {description}" if description else ""
                    content += f"- [{title}]({md_url}){desc_text}\n"

                content += "\n"

        llms_txt_path.write_text(content.strip(), encoding="utf-8")

    def _generate_llms_full_txt(self, site_dir: Path, config: MkDocsConfig) -> None:
        """Generate the llms-full.txt complete documentation file."""
        llms_full_path = site_dir / "llms-full.txt"

        content = f"# {config.site_name}\n\n"

        if config.site_description:
            content += f"> {config.site_description}\n\n"

        if self.config.markdown_description:
            content += f"{self.config.markdown_description}\n\n"

        for section_name, pages in self.pages_data.items():
            if pages:  # Only add section if it has pages
                content += f"# {section_name}\n\n"

                for page_data in pages:
                    if "markdown" in page_data:
                        title = page_data.get("title", page_data["src_uri"])
                        content += f"## {title}\n\n"
                        content += f"{page_data['markdown']}\n\n"

        llms_full_path.write_text(content.strip(), encoding="utf-8")

    def _get_theme_adjustments(self, config: MkDocsConfig) -> Dict[str, str]:
        """Get theme-specific adjustments for copy button positioning."""
        theme_name = (
            config.theme.name if hasattr(config.theme, "name") else str(config.theme)
        )

        # Theme-specific defaults
        theme_adjustments = {
            "material": {"top": "64px", "z_index": "2000"},  # Material has tall header
            "mkdocs": {"top": "80px", "z_index": "1100"},  # Default MkDocs theme
            "readthedocs": {"top": "60px", "z_index": "1100"},
            "bootstrap": {"top": "70px", "z_index": "1100"},
            "windmill": {"top": "50px", "z_index": "1000"},
        }

        return theme_adjustments.get(theme_name, {"top": "80px", "z_index": "1100"})

    def _get_copy_button_html(self, config: MkDocsConfig) -> str:
        """Generate HTML for the copy button with inline CSS and JavaScript."""
        # Get theme adjustments
        theme_defaults = self._get_theme_adjustments(config)

        # Get positioning configuration, with theme-aware defaults
        position = self.config.copy_button_position
        top = position.get("top", theme_defaults.get("top", "80px"))
        right = position.get("right", "20px")
        left = position.get("left", "")
        bottom = position.get("bottom", "")
        z_index = position.get("z_index", theme_defaults.get("z_index", "1100"))

        # Build position style
        position_style = f"position: fixed; z-index: {z_index};"
        if top:
            position_style += f" top: {top};"
        if right:
            position_style += f" right: {right};"
        if left:
            position_style += f" left: {left};"
        if bottom:
            position_style += f" bottom: {bottom};"

        # Get styling configuration
        style = self.config.copy_button_style
        button_style = "cursor: pointer;"
        for css_prop, value in style.items():
            # Convert snake_case to kebab-case for CSS
            css_property = css_prop.replace("_", "-")
            button_style += f" {css_property}: {value};"

        return rf"""
        <div id="llms-copy-button" style="{position_style}">
            <button onclick="copyMarkdownToClipboard()" style="{button_style}">{self.config.copy_button_text}</button>
        </div>
        <script>
        async function copyMarkdownToClipboard() {{
            try {{
                const currentPath = window.location.pathname;
                const mdPath = currentPath.endsWith('/') ? currentPath + 'index.md' : currentPath.replace(/\.html$/, '.md');

                const response = await fetch(mdPath);
                if (response.ok) {{
                    const markdown = await response.text();
                    await navigator.clipboard.writeText(markdown);
                    // Show feedback
                    const button = document.querySelector('#llms-copy-button button');
                    const originalText = button.textContent;
                    button.textContent = 'Copied!';
                    button.style.background = '#28a745';
                    setTimeout(() => {{
                        button.textContent = originalText;
                        button.style.background = '#007acc';
                    }}, 2000);
                }} else {{
                    throw new Error('Markdown file not found');
                }}
            }} catch (err) {{
                console.error('Failed to copy markdown:', err);
                alert('Failed to copy markdown content');
            }}
        }}
        </script>
        """
