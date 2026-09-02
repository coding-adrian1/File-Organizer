"""
Batch renaming with a template pattern, e.g. "vacation_{n:03d}{ext}"
or "{date}_{name}{ext}". Kept separate from organize so either
feature can be used on its own.
"""
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class RenamePlan:
    source: Path
    destination: Path


def plan_rename(
    directory: Path,
    pattern: str,
    start: int = 1,
    include_hidden: bool = False,
) -> list[RenamePlan]:
    """
    Build a rename plan for every file directly in `directory`.

    Pattern placeholders:
      {n}      sequence number (supports format specs, e.g. {n:03d})
      {name}   original filename without extension
      {ext}    original extension, including the dot
      {date}   file's last-modified date as YYYY-MM-DD
    """
    files = sorted(
        [f for f in directory.iterdir() if f.is_file() and (include_hidden or not f.name.startswith("."))]
    )

    plans: list[RenamePlan] = []
    used_names: set[str] = set()

    for i, f in enumerate(files, start=start):
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        new_name = pattern.format(n=i, name=f.stem, ext=f.suffix, date=mtime.strftime("%Y-%m-%d"))

        candidate = directory / new_name
        candidate = _dedupe(candidate, used_names)
        used_names.add(candidate.name)

        plans.append(RenamePlan(source=f, destination=candidate))

    return plans


def apply_rename(plans: list[RenamePlan]) -> list[tuple[Path, Path]]:
    """Execute a rename plan. Returns (source, destination) pairs that succeeded."""
    done = []
    for plan in plans:
        plan.source.rename(plan.destination)
        done.append((plan.source, plan.destination))
    return done


def _dedupe(path: Path, used_names: set[str]) -> Path:
    if path.name not in used_names and not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    counter = 1
    while True:
        candidate = path.parent / f"{stem}-{counter}{suffix}"
        if candidate.name not in used_names and not candidate.exists():
            return candidate
        counter += 1
