# bibtidy — Feature Specification

A single, open-source, offline-first BibTeX manager: parser, CLI, and GUI in one Python
package, built to replace JabRef. Primary author/user is @mapuys; built open source with
a high quality bar (tests, coverage, strict typing).

## Motivation

JabRef's maintenance situation is unreliable. bibtidy is a from-scratch replacement,
designed around one non-negotiable principle:

> **The `.bib` file is the only source of truth.** No sidecar database, no external
> config. Tags, collections, and any other bibtidy-specific metadata live as custom
> fields directly inside BibTeX entries, so the file stays fully portable and diffable
> in git.

## Interfaces

One package (`bibtidy`), three ways to use it:

1. **Python module** — import `bibtidy` directly and script against the core library.
2. **CLI** — scriptable, unix-philosophy commands (built with **Typer**).
3. **GUI** — desktop app (built with **Flet**), packaged as an optional extra
   (`pip install bibtidy[gui]`) so the core/CLI install stays lightweight.

Internal layout keeps these cleanly separated even within one repo:
- `bibtidy/core/` — data model, parser, canonical writer, dedup, validation, search,
  sorting, key generation. No CLI/GUI dependencies.
- `bibtidy/cli/` — Typer app, thin wrapper over `core`.
- `bibtidy/gui/` — Flet app, thin wrapper over `core`. Only imported/installed via the
  `gui` extra.

## Core features

### Parsing & data model
- Parses standard BibTeX entries: braces or quotes as delimiters, nested braces,
  escaped characters, numeric values.
- UTF-8 only. No LaTeX accent/escape normalization (e.g. `{\'e}`) — input files are
  assumed to already be UTF-8, values are kept as-is.
- **Out of scope for v1** (explicitly deferred, not silently unsupported): `@string`
  macro definitions/expansion, `@preamble`, `@comment` blocks, `crossref`/`xdata`
  inheritance.

### Canonical writer (diff-friendly) — top priority
- Every save rewrites the **entire file** in canonical form. No partial preservation of
  original formatting — this is intentional, so the file's shape never depends on
  editing history.
- Field order within an entry: fixed priority order for common fields (author, title,
  journal/booktitle, year, ...), remaining fields alphabetical.
- Entry order in the file: always re-sorted deterministically (by citation key), not
  insertion order.
- Value delimiters: braces `{}` only. Any quote-delimited (`"..."`) values encountered
  on read are converted to braces on write.

### Validation
- Required/optional fields per entry type follow a **BibLaTeX-style extended** type
  system (`@online`, `@report`, `@thesis`, `@software`, `@dataset`, etc.), not just
  classic BibTeX — chosen to fit modern references (preprints, software, datasets).
- Reports missing required fields per entry.

### Deduplication
- Detects likely-duplicate entries using DOI matching and fuzzy title matching.
- **Algorithm design is an open item** — deliberately deferred to a dedicated follow-up
  design session (the matching/scoring approach deserves its own discussion).

### Sorting
- Deterministic entry sorting (drives the canonical writer's entry order).

### Key generation
- JabRef-style pattern: `[auth][year]` (e.g. `Smith2020`).
- Collision disambiguation via suffix: `Smith2020a`, `Smith2020b`, ...

### Search
- Small query syntax over metadata fields, e.g. `author:smith year:2020
  tag:reading-list`. Not full-text (no note/abstract body search — metadata only).

### Tags & Collections (Groups)
- Both stored as custom BibTeX fields on each entry (not reusing the standard
  `keywords` field, to keep bibtidy's own concepts explicit and separate).
- A "collection"/"group" is a label an entry can belong to within a single library
  (JabRef "groups"-style), not a separate file per collection.
- Grouping feature presents entries organized by these tag/collection fields.

### Merge
- Combines multiple `.bib` files into a single collection/library. Not a general
  multi-source conflict-resolution engine — dedup detection is the mechanism for
  handling overlaps after merging.

## Explicit non-goals (v1)

- No external enrichment: fully offline, no DOI/CrossRef/arXiv/Scholar/Semantic
  Scholar lookups.
- No PDF handling: no downloading, no linking to local PDF files.
- No LaTeX workflow integration (no `.tex` project watching, no citation-usage
  reports).
- No editor integrations (VS Code/Vim) for now — standalone tool only.
- No full-text search (notes/abstracts) — metadata search only.

## Architecture & repo

- Single repo, single PyPI package: **bibtidy**.
- Distribution: pip-installable; likely also packaged as a single binary
  (e.g. PyInstaller/Nuitka) for the CLI+GUI use case — to be finalized when GUI work
  starts.
- GUI dependencies isolated behind the `gui` extra.

## Toolchain & quality bar

- Packaging/env: **Poetry**.
- Testing: **pytest** + coverage.
- Linting: **pylint**.
- Type checking: **ty**.
- CI: GitHub Actions running lint/type-check/tests on every PR (specifics TBD when the
  repo is scaffolded).
- Python version floor: TBD — should be confirmed based on `ty`'s minimum supported
  Python version when the repo is set up.

## Roadmap

Ordered so the core library — parsing and canonical writing — lands first and is solid
before anything is built on top of it. Each milestone should be shippable/testable on
its own before starting the next.

### M0 — Core library MVP (parser + canonical writer)
- Starting point: the field-parsing approach in
  `~/Documents/perso/cv/cv/formatters/bibtexFormatter.py` (brace-counting value
  extraction, quote/brace handling, escape handling) — ported into `bibtidy/core` and
  stripped of everything CV-specific (no HTML/Typst/Markdown rendering, no hardcoded
  author highlighting, no ranking-aware venue logic).
- Data model: `Entry` (type, key, fields) and `Library` (a collection of entries).
- Parses standard BibTeX per the v1 scope (braces/quotes, nested braces, escapes,
  numeric values; no `@string`/`@preamble`/`@comment`/`crossref`).
- New vs. the old code: a canonical writer (fixed field order, deterministic
  key-based entry sorting, braces-only output, full-file rewrite on every save).
- BibLaTeX-style entry type + required-field table, with a `validate()` that reports
  missing required fields per entry.
- Full test suite + coverage from day one; round-trip parse → write → parse tests are
  the key correctness signal, alongside fixtures for malformed/edge-case input.
- **Exit criteria**: loads a real-world `.bib` file, validates it, and rewrites it in
  canonical form with zero unintended diff on a second save (idempotent write).

### M1 — Library operations
- Key generation (`[auth][year]` + `a`/`b`/`c` disambiguation).
- Sorting exposed as a standalone operation (in addition to the writer's built-in
  ordering).
- Search: the `author:`/`year:`/`tag:`/... query syntax over metadata.
- Tags & collections: read/write the custom fields, group-by helpers.
- Merge: combine multiple `Library` instances into one, surfacing key collisions and
  a (stub) dedup hook to flag likely overlaps.

### M2 — CLI
- Typer app wrapping M0/M1 operations, e.g. `bibtidy validate`, `bibtidy fmt`,
  `bibtidy sort`, `bibtidy search`, `bibtidy merge`, `bibtidy keygen`, `bibtidy tag`,
  `bibtidy group`.
- Scriptable: correct exit codes, stdin/stdout piping where it makes sense.
- `CliRunner`-based tests for every command.

### M3 — Dedup
- Dedicated design session for the DOI + fuzzy-title matching algorithm (see Open
  Items — deliberately not designed yet).
- Implement once designed; expose via both the core API and `bibtidy dedup`.

### M4 — GUI
- Flet app behind the `gui` extra: entry table (filter/sort/search), detail/edit
  panel, tag/collection management.
- Built entirely on M0–M3 core/CLI operations — no business logic lives only in the
  GUI layer.

### M5 — Packaging & release
- Single-binary packaging decision executed (PyInstaller vs Nuitka).
- GitHub Actions CI finalized (lint/type-check/tests), Python version floor confirmed.
- First PyPI release, after the name-collision check.

## Open items for future sessions

- Dedup matching/scoring algorithm (DOI + fuzzy title matching) — dedicated design
  session.
- Confirm "bibtidy" has no conflicting PyPI package name or GitHub repo before first
  push.
- Python version floor, GitHub Actions workflow details.
- Single-binary packaging approach (PyInstaller vs Nuitka) — decide once GUI work
  starts.
