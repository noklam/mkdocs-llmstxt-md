# Design: Auto-derive llms.txt sections from mkdocs `nav`

Resolves: https://github.com/nikita-volkov/mkdocs-llmstxt-md/issues/1

## Problem

`sections:` in the plugin config is a fully separate list from mkdocs.yml's `nav:`.
Nothing keeps them in sync, so a page added to `nav` silently doesn't reach
`llms.txt`/`llms-full.txt` until someone remembers to add it to `sections` too.

## Goal

If `sections` is omitted, or a page isn't listed in any section, derive that
page's title/grouping from `nav` automatically, so `nav` becomes the single
source of truth. `sections` remains available as an optional override for
custom titles/grouping/descriptions.

## Behavior

Precedence: an explicit `sections` entry for a page always wins. Only pages
*not* claimed by any `sections` entry are auto-derived from `nav`.

Nav-derivation rules, applied to the resolved mkdocs `Navigation` tree:

- A `Section` (e.g. `Getting Started: [...]`) becomes a section heading equal
  to its title. All `Page` leaves nested under it — including leaves under
  nested sub-sections — are flattened into that one heading, preserving nav
  order. Nesting depth beyond one level is not reflected in the heading
  structure (matches the existing flat `sections` dict shape).
- A top-level `Page` not wrapped in any `Section` (e.g. `Home: index.md`)
  becomes its own section, headed by that page's own resolved title. (A
  page's title may come from an explicit nav label or, if absent, from the
  page's first `H1`, which mkdocs only resolves when the page is read — after
  `on_nav` runs. These are tracked as pending "singleton" sections and
  resolved once the real title is known, in `on_page_markdown`.)
- Nav `Link` entries (external URLs) are skipped.
- If a nav-derived section name collides with an existing (explicit or
  already-created nav-derived) section name, pages are merged into that same
  heading instead of creating a duplicate.
- Nav-derived descriptions are empty (nav carries no description text).

Output order: explicit `sections` entries first (unchanged from current
behavior), then nav-derived sections/singletons appended in nav traversal
order.

## Implementation sketch

All changes confined to `src/mkdocs_llmstxt_md/plugin.py`:

- Add an `on_nav(nav, config, files)` hook that runs after `on_files` (which
  still populates `self.pages_data` from explicit `sections`, unchanged) and
  before pages are read.
  - Collect the set of `src_uri`s already covered by `self.pages_data`.
  - Recursively walk `nav.items`:
    - `Section`: flatten all `Page` descendants; for any leaf not covered,
      append `{"src_uri": ..., "description": ""}` to
      `self.pages_data[section.title]` (creating the key if new).
    - top-level `Page` not covered: record `src_uri` in a new
      `self.singleton_src_uris: List[str]`, in encounter order.
    - `Link`: skip.
- Extend `on_page_markdown` (which already updates the matching page dict
  when a page's markdown/title becomes known) to also check
  `self.singleton_src_uris`: when a covered singleton page is read, store its
  resolved title alongside the markdown so generation can use it as the
  section heading.
- At generation time (`_generate_llms_txt` / `_generate_llms_full_txt`),
  after iterating `self.pages_data`, also iterate the resolved singleton
  entries, emitting one heading (`page title`) per entry containing just that
  page — skipping any singleton that never got read (e.g. excluded from
  build) same as the existing "only add section if it has pages" guard.

`config.py` requires no changes — `sections` already defaults to `{}`, so it
is already optional at the schema level; this change makes it optional in
practice too.

## Testing

No automated test suite exists in this repo today (manual test-site builds
only) — staying consistent with that. Validation plan using `test-site/`:

1. Build with `sections` removed entirely from `test-site/mkdocs.yml` —
   confirm `llms.txt`/`llms-full.txt` contain all nav pages, grouped by nav
   section titles, with the top-level `Home` page as its own section.
2. Build with `sections` covering only a subset of pages (e.g. drop the
   `"Advanced Topics"` entry) — confirm the remaining nav section
   (`Advanced`) is auto-derived and appended after the explicit sections,
   and that explicitly-covered pages are not duplicated.
3. Spot-check that a page's nav-derived title matches the manually-set title
   in the explicit-`sections` case, to confirm no regression there.

## Documentation

Update `README.md`'s Configuration section to describe the new default
(nav-derived) behavior and clarify `sections` as an optional override.
