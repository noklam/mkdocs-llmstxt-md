# Nav-derived llms.txt sections Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `mkdocs.yml`'s `nav:` the single source of truth for which pages appear in `llms.txt`/`llms-full.txt`, so pages added to `nav` are picked up automatically without needing a matching `sections:` entry.

**Architecture:** Add an `on_nav` plugin hook that runs after the existing `on_files`-driven explicit-`sections` handling. It walks the resolved `mkdocs` `Navigation` tree and registers any page not already covered by `sections`: pages under a nav `Section` are flattened into that section's heading; a top-level `Page` not wrapped in any `Section` becomes its own section, headed by its own title (resolved later, once `on_page_markdown` reads it). Generation and markdown-writing code is extended to also emit these nav-derived entries.

**Tech Stack:** Python, `mkdocs` plugin API (`mkdocs.structure.nav.{Navigation,Section,Link}`, `mkdocs.structure.pages.Page`).

## Global Constraints

- Single file touched for logic: `src/mkdocs_llmstxt_md/plugin.py`. `config.py` is unchanged.
- No automated test suite is being introduced — validate manually via `test-site/` builds, per repo convention (see `README.md` "Currently manual testing via the test site").
- Explicit `sections:` entries always take precedence over nav-derivation for a given page.
- Nav `Link` items (external URLs) are never included — they have no source file.
- Ruff lint/format must pass (`ruff check` / `ruff format --check`), matching this repo's existing style (see `pyproject.toml` `[tool.ruff]`).

---

### Task 1: Implement nav-derived section/page registration in the plugin

**Files:**
- Modify: `src/mkdocs_llmstxt_md/plugin.py`

**Interfaces:**
- Consumes: nothing new from outside this file — uses `mkdocs.structure.nav.Navigation`, `mkdocs.structure.nav.Section`, `mkdocs.structure.nav.Link` (all part of the `mkdocs` dependency already required by `pyproject.toml`), and the existing `Page`, `Files`, `MkDocsConfig` imports already in the file.
- Produces (for later tasks / README docs to reference):
  - `self.singleton_src_uris: List[str]` — ordered list of `src_uri`s for top-level nav pages not covered by any section, populated in `on_nav`.
  - `self.singleton_pages: Dict[str, Dict[str, Any]]` — `src_uri -> page_data` dict populated once each singleton page's markdown/title is read in `on_page_markdown`. Each `page_data` has the same shape as entries in `self.pages_data`'s lists: `src_uri`, `description`, `title`, `markdown`, `dest_path`, `dest_uri`.
  - `self._write_markdown_file(self, site_dir: Path, page_data: Dict[str, Any]) -> None` — new private helper used by `_generate_markdown_files` for both explicit and singleton pages.

This task is not independently splittable — the nav-walk, title-resolution, generation, and markdown-writing changes all share the same two new attributes and must land together for the plugin to work; there's no meaningful midpoint to review separately.

- [ ] **Step 1: Add imports and initialize new instance attributes**

In `src/mkdocs_llmstxt_md/plugin.py`, update the `mkdocs.structure.nav` import (currently there is none) and `__init__`:

```python
from mkdocs.structure.nav import Link, Navigation, Section
```

Add this alongside the existing imports at the top of the file (after the existing `from mkdocs.structure.pages import Page` line).

Update `__init__`:

```python
    def __init__(self):
        super().__init__()
        self.mkdocs_config: MkDocsConfig = None
        self.pages_data: Dict[str, List[Dict[str, Any]]] = {}
        self.source_files: Dict[str, str] = {}
        self.singleton_src_uris: List[str] = []
        self.singleton_pages: Dict[str, Dict[str, Any]] = {}
```

- [ ] **Step 2: Reset the new attributes on each config load**

In `on_config`, alongside the existing `self.pages_data = ...` reset, add resets for the two new attributes so rebuilds (e.g. `mkdocs serve` live reload) don't accumulate stale entries:

```python
        self.mkdocs_config = config
        self.pages_data = {section: [] for section in self.config.sections.keys()}
        self.singleton_src_uris = []
        self.singleton_pages = {}
        return config
```

- [ ] **Step 3: Add the nav-flattening helper and `on_nav` hook**

Add these two methods to `LlmsTxtPlugin`, placed after `on_files` and before `on_page_markdown`:

```python
    def _flatten_section_pages(self, section: Section) -> List[Page]:
        """Recursively collect all Page leaves nested under a nav Section."""
        pages: List[Page] = []
        for child in section.children:
            if isinstance(child, Section):
                pages.extend(self._flatten_section_pages(child))
            elif isinstance(child, Page):
                pages.append(child)
            # Link children are skipped: no source file to render.
        return pages

    def on_nav(
        self, nav: Navigation, *, config: MkDocsConfig, files: Files
    ) -> Navigation:
        """Derive sections/pages from nav for any page not already covered
        by the explicit `sections` config."""
        covered_src_uris = {
            page_data["src_uri"]
            for pages in self.pages_data.values()
            for page_data in pages
        }

        for item in nav.items:
            if isinstance(item, Section):
                new_leaves = [
                    page
                    for page in self._flatten_section_pages(item)
                    if page.file.src_uri not in covered_src_uris
                ]
                if not new_leaves:
                    continue
                section_pages = self.pages_data.setdefault(item.title, [])
                for page in new_leaves:
                    section_pages.append(
                        {"src_uri": page.file.src_uri, "description": ""}
                    )
                    covered_src_uris.add(page.file.src_uri)
            elif isinstance(item, Page):
                if item.file.src_uri not in covered_src_uris:
                    self.singleton_src_uris.append(item.file.src_uri)
                    covered_src_uris.add(item.file.src_uri)
            # Link items are skipped: no source file to render.

        return nav
```

Note: `Link` is imported but never referenced by name in this code — it's used implicitly by the `isinstance` checks excluding it (neither `Section` nor `Page` matches a `Link`). Remove the unused import warning risk by keeping the import only if ruff's `F401` doesn't flag it; if it does, drop the `Link` import since it's not directly referenced. (Ruff will be run in Step 8 to confirm either way.)

- [ ] **Step 4: Resolve singleton titles in `on_page_markdown`**

Modify `on_page_markdown` to also populate `self.singleton_pages` when a singleton page is read:

```python
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

        # Check if this page is a nav-derived singleton section
        if src_uri in self.singleton_src_uris:
            self.source_files[src_uri] = markdown
            self.singleton_pages[src_uri] = {
                "src_uri": src_uri,
                "description": "",
                "title": page.title or src_uri,
                "markdown": markdown,
                "dest_path": page.file.dest_path,
                "dest_uri": page.file.dest_uri,
            }

        return markdown
```

- [ ] **Step 5: Add `_write_markdown_file` helper and use it from `_generate_markdown_files`**

Replace `_generate_markdown_files` with:

```python
    def _write_markdown_file(self, site_dir: Path, page_data: Dict[str, Any]) -> None:
        """Write a single page's markdown content to its .md URL location."""
        if "markdown" not in page_data or "dest_path" not in page_data:
            return

        html_path = Path(page_data["dest_path"])
        md_path = site_dir / html_path.with_suffix(".md")

        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(page_data["markdown"], encoding="utf-8")

    def _generate_markdown_files(self, site_dir: Path) -> None:
        """Generate individual .md files for each page."""
        for section_pages in self.pages_data.values():
            for page_data in section_pages:
                self._write_markdown_file(site_dir, page_data)

        for page_data in self.singleton_pages.values():
            self._write_markdown_file(site_dir, page_data)
```

- [ ] **Step 6: Emit singleton sections in `_generate_llms_txt`**

Replace `_generate_llms_txt` with:

```python
    def _generate_llms_txt(self, site_dir: Path, config: MkDocsConfig) -> None:
        """Generate the llms.txt index file."""
        llms_txt_path = site_dir / "llms.txt"

        content = f"# {config.site_name}\n\n"

        if config.site_description:
            content += f"> {config.site_description}\n\n"

        if self.config.markdown_description:
            content += f"{self.config.markdown_description}\n\n"

        base_url = config.site_url.rstrip("/")

        def format_page_link(page_data: Dict[str, Any]) -> str:
            title = page_data.get("title", page_data["src_uri"])
            dest_uri = page_data.get("dest_uri", "")
            description = page_data.get("description", "")

            md_url = urljoin(
                base_url + "/",
                dest_uri.replace(".html", ".md")
                if dest_uri.endswith(".html")
                else dest_uri + ".md",
            )

            desc_text = f": {description}" if description else ""
            return f"- [{title}]({md_url}){desc_text}\n"

        for section_name, pages in self.pages_data.items():
            if pages:  # Only add section if it has pages
                content += f"## {section_name}\n\n"
                for page_data in pages:
                    content += format_page_link(page_data)
                content += "\n"

        for src_uri in self.singleton_src_uris:
            page_data = self.singleton_pages.get(src_uri)
            if not page_data:
                continue

            content += f"## {page_data['title']}\n\n"
            content += format_page_link(page_data)
            content += "\n"

        llms_txt_path.write_text(content.strip(), encoding="utf-8")
```

(This also factors the repeated link-formatting block into `format_page_link` to avoid duplicating it for the new singleton loop.)

- [ ] **Step 7: Emit singleton sections in `_generate_llms_full_txt`**

Replace `_generate_llms_full_txt` with:

```python
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

        for src_uri in self.singleton_src_uris:
            page_data = self.singleton_pages.get(src_uri)
            if not page_data or "markdown" not in page_data:
                continue

            content += f"# {page_data['title']}\n\n"
            content += f"{page_data['markdown']}\n\n"

        llms_full_path.write_text(content.strip(), encoding="utf-8")
```

- [ ] **Step 8: Set up a dev virtualenv and lint**

```bash
python3 -m venv .venv
.venv/bin/pip install -q -e . ruff
.venv/bin/ruff check src/mkdocs_llmstxt_md/plugin.py
.venv/bin/ruff format --check src/mkdocs_llmstxt_md/plugin.py
```

Expected: both commands report no issues. If `ruff check` flags the `Link` import as unused (`F401`), remove `Link` from the `from mkdocs.structure.nav import ...` line in Step 1 (keep `Navigation, Section`) and re-run both commands until clean. If `ruff format --check` reports a diff, run `.venv/bin/ruff format src/mkdocs_llmstxt_md/plugin.py` and re-check.

- [ ] **Step 9: Manual validation — pure nav-derivation (no `sections` at all)**

```bash
cp test-site/mkdocs.yml /tmp/mkdocs.yml.bak
python3 - <<'EOF'
import re
path = "test-site/mkdocs.yml"
text = open(path).read()
text = text.replace(
    """plugins:
  - llmstxt-md:
      sections:
        "Getting Started":
          - index.md: "Welcome to our documentation"
          - quickstart.md: "Quick start guide"
          - installation.md: "Installation instructions"
        "API Reference":
          - api/*.md
        "Advanced Topics":
          - advanced/*.md
      markdown_description: "Complete documentation for the test project with API reference and advanced topics."
""",
    """plugins:
  - llmstxt-md:
      markdown_description: "Complete documentation for the test project with API reference and advanced topics."
""",
)
open(path, "w").write(text)
EOF
cd test-site && ../.venv/bin/mkdocs build --strict && cd ..
cat test-site/site/llms.txt
```

Expected `llms.txt` output: a `## Home` section containing the `index.md` link (since `Home: index.md` is a top-level nav page, not inside a `Section`), followed by `## Getting Started` (from the nav `Section` grouping `quickstart.md`/`installation.md`), `## API Reference` (`api/overview.md`, `api/functions.md`), and `## Advanced` (`advanced/configuration.md` — note this is titled "Advanced" here, matching the nav Section title, not "Advanced Topics" which was only the `sections:`-config name previously). All four should be present with no manual `sections:` config at all.

Also confirm no build errors/warnings from `mkdocs build --strict` (which fails the build on any warning, e.g. broken links) and that `test-site/site/index.md`, `test-site/site/quickstart/index.md`, etc. exist.

Restore the original file:

```bash
cp /tmp/mkdocs.yml.bak test-site/mkdocs.yml
```

- [ ] **Step 10: Manual validation — partial `sections` override**

```bash
python3 - <<'EOF'
path = "test-site/mkdocs.yml"
text = open(path).read()
text = text.replace(
    """      sections:
        "Getting Started":
          - index.md: "Welcome to our documentation"
          - quickstart.md: "Quick start guide"
          - installation.md: "Installation instructions"
        "API Reference":
          - api/*.md
        "Advanced Topics":
          - advanced/*.md
""",
    """      sections:
        "Getting Started":
          - index.md: "Welcome to our documentation"
          - quickstart.md: "Quick start guide"
          - installation.md: "Installation instructions"
""",
)
open(path, "w").write(text)
EOF
cd test-site && ../.venv/bin/mkdocs build --strict && cd ..
cat test-site/site/llms.txt
```

Expected: `## Getting Started` appears first (explicit `sections`, with the custom descriptions "Welcome to our documentation" etc. — proving explicit entries still win and aren't duplicated), followed by nav-derived `## API Reference` and `## Advanced` sections (auto-derived, `description` empty since nav carries none). No page should appear twice.

Restore the original file:

```bash
cp /tmp/mkdocs.yml.bak test-site/mkdocs.yml
rm /tmp/mkdocs.yml.bak
```

- [ ] **Step 11: Clean up the dev virtualenv and commit**

```bash
rm -rf .venv test-site/site
git status
```

Confirm `git status` shows only `src/mkdocs_llmstxt_md/plugin.py` modified (and `test-site/mkdocs.yml` back to its original committed state — should show no diff).

```bash
git add src/mkdocs_llmstxt_md/plugin.py
git commit -m "Derive llms.txt sections from mkdocs nav when not covered by sections config"
```

---

### Task 2: Update README documentation

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: nothing (documentation-only task).
- Produces: nothing consumed by other tasks.

- [ ] **Step 1: Update the Configuration section**

In `README.md`, find this line (in the `## Configuration` section):

```markdown
- `sections`: Dict of section names to file patterns
```

Replace it with:

```markdown
- `sections`: Optional dict of section names to file patterns, for custom titles/grouping/descriptions. Any page in `nav` that isn't covered by `sections` is included automatically, grouped by its `nav` structure (a `nav` `Section` becomes a heading; a top-level page not inside any section becomes its own heading, named after the page).
```

- [ ] **Step 2: Update the Usage example to show the override use case**

Find the `## Usage` section's example block:

```markdown
Add to your `mkdocs.yml`:

```yaml
plugins:
  - llmstxt-md:
      sections:
        "Getting Started":
          - index.md: "Introduction to the project"
          - quickstart.md
        "API Reference":
          - api/*.md
```
```

Replace it with:

```markdown
Add to your `mkdocs.yml`. At its simplest, no configuration is needed — sections are derived from your `nav`:

```yaml
plugins:
  - llmstxt-md
```

To customize titles, descriptions, or grouping for specific pages, add `sections` — it overrides nav-derivation only for the pages it lists; everything else still comes from `nav`:

```yaml
plugins:
  - llmstxt-md:
      sections:
        "Getting Started":
          - index.md: "Introduction to the project"
          - quickstart.md
```
```

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "Document nav-derived sections as the default behavior"
```
