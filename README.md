# File Organizer CLI

A command-line tool that sorts a messy folder into category subfolders
(Images, Documents, Audio, Archives, Code, ...), with a dry-run preview,
safe conflict handling, and a genuine **undo** — because a batch move
you can't reverse is a tool nobody actually runs on a real folder.

Also includes a batch-rename command for turning `IMG_2847.jpg`,
`IMG_2848.jpg`... into `trip_001.jpg`, `trip_002.jpg`, ...

## Install

```bash
pip install -e .
```

This registers an `organizer` command on your PATH (via
`[project.scripts]` in `pyproject.toml` — no manual `python path/to/script.py`
needed).

## Usage

```bash
# Preview what would happen — nothing is moved
organizer organize ~/Downloads --dry-run

# Actually organize it
organizer organize ~/Downloads

# Changed your mind?
organizer undo ~/Downloads

# Batch rename files in a folder
organizer rename ~/Downloads/Images "trip_{n:03d}{ext}"
organizer rename ~/Downloads/Images "{date}_{name}{ext}"   # e.g. 2026-08-14_sunset.jpg
```

### Rename pattern placeholders

| Placeholder | Meaning |
|---|---|
| `{n}` | Sequence number — supports format specs, e.g. `{n:03d}` → `001` |
| `{name}` | Original filename without its extension |
| `{ext}` | Original extension, including the dot |
| `{date}` | File's last-modified date, `YYYY-MM-DD` |

## How it works

```
file-organizer/
├── organizer/
│   ├── cli.py          # argparse subcommands: organize / undo / rename
│   ├── core.py         # plan_organization() / apply_plan() — the sorting logic
│   ├── categories.py   # extension → category mapping
│   ├── manifest.py     # writes/reads run history so undo is possible
│   └── rename.py       # batch rename planning + execution
├── tests/               # 19 pytest tests, run against tmp_path (never your real files)
└── pyproject.toml
```

**Plan vs. apply, on purpose.** `plan_organization()` decides where every
file *should* go without touching the filesystem; `apply_plan()` is the
only function that actually moves anything. This is what makes
`--dry-run` trivial (just don't call apply) and what makes the tests
fast and safe.

**Undo, not just delete-protection.** Every real run writes a manifest
(`.organizer_history/run-<timestamp>.json`) listing every move. `organizer
undo` reads the most recent one and reverses it — and if a file was
manually moved again since, that one file is reported as skipped rather
than silently failing the whole undo.

**Duplicate names never overwrite.** If `Documents/report.pdf` already
exists, the incoming file becomes `report (1).pdf`, `report (2).pdf`,
etc. — matching the convention most OSes already use.

**One bad file doesn't kill the batch.** If a file can't be moved
(permissions, in use, etc.), that one entry is recorded as an error and
the rest of the batch still completes.

## Running tests

```bash
pip install pytest
pytest -v
```

19 tests, covering: category mapping, hidden-file handling, files with
no extension, duplicate-name collisions, undo (including the case
where a file moved again since), and rename pattern edge cases
(collisions, custom start offsets).

## What I'd add next

- A `--categories` flag to load a custom extension mapping from JSON
- Recursive mode (currently only sorts files directly inside the
  target directory, on purpose — so it's safe to point at a folder
  with existing subfolders)
- A minimal Tkinter GUI wrapping the same `core.py` functions
