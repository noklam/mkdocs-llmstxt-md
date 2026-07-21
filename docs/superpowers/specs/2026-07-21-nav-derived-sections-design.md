# Design: Auto-derive llms.txt sections from mkdocs `nav`

Resolves: https://github.com/nikita-volkov/mkdocs-llmstxt-md/issues/1

## Problem

`sections:` in the plugin config is a fully separate list from mkdocs.yml's `nav:`.
Nothing keeps them in sync, so a page added to `nav` silently doesn't reach
`llms.txt`/`llms-full.txt` until someone remembers to add it to `sections` too.

## Goal

If `sections` is omitted (empty), derive all sections/pages from `nav`
automatically, so `nav` becomes the single source of truth. `sections`
remains available as an explicit override for full manual control over
titles/grouping/descriptions.

## Behavior (revised — all-or-nothing switch)

> **Revision note (2026-07-21):** the original version of this design used
> a per-page merge — explicit `sections` entries won individually, and any
> page they didn't cover fell back to nav-derivation, both feeding into the
> same output. Whole-branch review of the first implementation surfaced
> that maintaining nav traversal order across two separate data structures
> (explicit sections + deferred-title singletons) put derived top-level
> pages after all sections, contradicting the spec text. Discussing the
> fix, the simpler and equally issue-satisfying design below was chosen:
> the switch is per-build, not per-page. This still fully resolves issue
> #1's core complaint (nav drift going undetected) for the common case
> ("just mirror my nav" — ship with no `sections` block, or delete it to
> stop maintaining a manual list) while keeping a fully-manual escape
> hatch. It trades the "mix explicit overrides with nav-derived pages in
> one build" capability for a correct, simple, single-pass implementation.
> If per-page merging is wanted later, it's a separate, additive feature.

- If `sections` is **empty** (the default, or explicitly `{}`): every page
  in `nav` is included, grouped and ordered by walking `nav.items` in a
  single pass, in nav order:
  - A `Section` (e.g. `Getting Started: [...]`) becomes a heading equal to
    its title. All `Page` leaves nested under it — including leaves under
    nested sub-sections — are flattened into that one heading. Nesting
    depth beyond one level is not reflected in the heading structure
    (matches the flat `sections` dict shape).
  - A top-level `Page` not wrapped in any `Section` (e.g. `Home: index.md`)
    becomes its own heading, named after that page's own resolved title.
    (A page's title may come from an explicit nav label or, if absent,
    from the page's first `H1`, which mkdocs only resolves when the page
    is read — after `on_nav` runs. These are tracked with a deferred name,
    resolved once the real title is known, in `on_page_markdown`.)
  - `Link` entries (external URLs) are skipped — no source file to render.
  - Derived descriptions are empty (nav carries no description text).
- If `sections` is **non-empty**: behavior is unchanged from before this
  feature — only the pages explicitly listed in `sections` are included;
  `nav` is not consulted at all. This preserves full manual control for
  anyone who wants custom titles/grouping/descriptions.

Output order in the nav-derived case is exactly nav traversal order —
sections and top-level pages interleave in the order they appear in `nav`.

## Implementation sketch

All changes confined to `src/mkdocs_llmstxt_md/plugin.py`:

- Add an `on_nav(nav, config, files)` hook that runs after `on_files` and
  before pages are read. If `self.config.sections` is non-empty, it
  returns immediately (no nav-derivation). Otherwise it walks `nav.items`
  once and appends one entry per top-level item, in order, to a new
  `self.nav_groups: List[Dict[str, Any]]`:
  - `Section`: `{"name": section.title, "pages": [...]}` — one dict per
    flattened `Page` leaf (via a recursive `_flatten_section_pages`
    helper), each `{"src_uri": ..., "description": ""}`.
  - top-level `Page`: `{"name": None, "pages": [{"src_uri": ..., "description": ""}]}`
    — `name` is resolved once the page is read.
  - `Link`: skipped.
- Extend `on_page_markdown` to also scan `self.nav_groups` (alongside the
  existing `self.pages_data` scan for explicit sections) for a matching
  `src_uri`; when found, fill in `title`/`markdown`/`dest_path`/`dest_uri`
  on that page dict, and if the owning group's `name` is still `None`, set
  it to the resolved title.
- Generation (`_generate_markdown_files`, `_generate_llms_txt`,
  `_generate_llms_full_txt`) each gain a second loop over `self.nav_groups`
  (after their existing loop over `self.pages_data`), skipping any group
  with no read pages (e.g. excluded from the build). Since the two configs
  are mutually exclusive, at most one of `self.pages_data` /
  `self.nav_groups` is ever non-empty in a given build, but looping both
  unconditionally is simpler than branching and is harmless.

`config.py` requires no changes — `sections` already defaults to `{}`.

## Testing

No automated test suite exists in this repo today (manual test-site builds
only) — staying consistent with that. Validation plan using `test-site/`:

1. Build with `sections` removed entirely from `test-site/mkdocs.yml` —
   confirm `llms.txt`/`llms-full.txt` contain all nav pages, in nav order:
   `Home` (top-level page, own heading) first, then `Getting Started`,
   `API Reference`, `Advanced` (nav section headings), matching the exact
   order pages appear in `nav:`.
2. Build with `sections` covering only a subset of nav pages (e.g. only
   `"Getting Started"`) — confirm the output contains *only* those pages
   (with their custom descriptions), and that pages outside `sections`
   (`API Reference`, `Advanced`) are absent, since a non-empty `sections`
   disables nav-derivation entirely.
3. Spot-check that a page's nav-derived title matches the manually-set
   title in the explicit-`sections` case, to confirm no regression there.

## Documentation

Update `README.md`'s Configuration section to describe `sections` as an
all-or-nothing switch: leave it empty/omitted to mirror `nav` automatically,
or provide it to take full manual control (nav is then ignored).
