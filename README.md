# bibtidy

A single, open-source, offline-first BibTeX manager: parser, canonical writer, and
validation in one Python package, built to replace JabRef.

> **The `.bib` file is the only source of truth.** No sidecar database, no external
> config — bibtidy-specific metadata lives as custom fields directly inside entries,
> so the file stays fully portable and diffable in git.

See [`FEATURES.md`](FEATURES.md) for the full specification and roadmap.

## Status

**M0 — Core library MVP.** Import (parse), manipulate (data model), and export
(canonical, idempotent write) BibTeX, plus BibLaTeX-style required-field validation.

```python
import bibtidy

library = bibtidy.parse_file("refs.bib")
for issue in bibtidy.validate(library):
    print(issue)
bibtidy.write_file(library, "refs.bib")   # canonical, deterministic, idempotent
```

## Development

```sh
poetry install
poetry run pytest        # tests + coverage
poetry run pylint bibtidy
poetry run ty check
```
