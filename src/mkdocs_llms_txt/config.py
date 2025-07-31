"""Configuration for the LLMsTxt plugin."""

from mkdocs.config import config_options
from mkdocs.config.base import Config


class LLMsTxtConfig(Config):
    """Configuration options for the LLMsTxt plugin."""

    sections = config_options.Type(dict, default={})
    """Dictionary mapping section names to lists of file patterns."""

    enable_markdown_urls = config_options.Type(bool, default=True)
    """Whether to serve original markdown at .md URLs."""

    enable_llms_txt = config_options.Type(bool, default=True)
    """Whether to generate llms.txt file."""

    enable_llms_full = config_options.Type(bool, default=True)
    """Whether to generate llms-full.txt file."""

    enable_copy_button = config_options.Type(bool, default=True)
    """Whether to add copy-to-markdown button on pages."""

    copy_button_text = config_options.Type(str, default="Copy Markdown")
    """Text for the copy button."""

    copy_button_position = config_options.Type(
        dict, default={"top": "80px", "right": "20px", "z_index": "1100"}
    )
    """Position and z-index settings for the copy button."""

    copy_button_style = config_options.Type(
        dict,
        default={
            "background": "#007acc",
            "color": "white",
            "border": "none",
            "padding": "8px 16px",
            "border_radius": "4px",
            "font_size": "14px",
            "box_shadow": "0 2px 4px rgba(0,0,0,0.2)",
        },
    )
    """CSS styling options for the copy button."""

    markdown_description = config_options.Optional(config_options.Type(str))
    """Optional description to include in llms.txt."""
