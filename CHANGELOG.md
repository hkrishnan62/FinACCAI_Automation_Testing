# Changelog

All notable changes to this project will be documented in this file.

## Unreleased (2025-12-25)

### Changed
- **Refactor:** Moved core scanner logic from the top-level script into a package layout:
  - Created `finaccai/script.py` containing core functions (network fetching, accessibility checks, report generation, CSV parsing).
  - Added `finaccai/cli.py` providing a `main()` CLI entrypoint.
  - Exposed core functions at `finaccai` package level via `finaccai/__init__.py` for backward compatibility.
  - Updated `finaccai/__main__.py` and added a small top-level wrapper `finaccai.py` so both
    `python -m finaccai --csv websites.csv` and `python finaccai.py --csv websites.csv` work.

### Removed
- Removed legacy file `finaccai-old.py` which contained the pre-refactor script.

### Notes
- The module can now be executed as a package: `python -m finaccai --csv websites.csv`.
- Unit tests and CI were minimally updated (added a smoke test) to ensure `pytest` runs on CI.
- If you rely on older local clones, re-clone or reset to avoid local conflicts after these structural changes.

