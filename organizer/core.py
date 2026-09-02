"""
Core file-organizing logic.

Split into "plan" (pure, side-effect-free — decide what should move
where) and "apply" (actually perform the moves) so the plan can be
previewed with --dry-run and tested without touching the filesystem
beyond what pytest's tmp_path already isolates.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from organizer.categories import category_for


@dataclass
class PlannedMove:
    source: Path
    destination: Path
    category: str


@dataclass
class MoveResult:
    source: Path
    destination: Optional[Path]
    category: str
    status: str  # "moved", "skipped", "error"
    reason: Optional[str] = None


def plan_organization(directory: Path, include_hidden: bool = False) -> list[PlannedMove]:
    """
    Decide where every file in `directory` should go, without moving
    anything. Subdirectories are left alone — only files directly in
    `directory` are considered, so re-running the tool on an already
    organized folder is a no-op.
    """
    plans: list[PlannedMove] = []

    for entry in sorted(directory.iterdir()):
        if not entry.is_file():
            continue
        if entry.name.startswith(".") and not include_hidden:
            continue

        category = category_for(entry.suffix)
        target_dir = directory / category
        destination = _unique_destination(target_dir / entry.name)
        plans.append(PlannedMove(source=entry, destination=destination, category=category))

    return plans


def apply_plan(plans: list[PlannedMove]) -> list[MoveResult]:
    """Execute a plan, moving each file. Never raises — failures are
    captured per-file as a MoveResult so one bad file doesn't abort
    the whole batch."""
    results: list[MoveResult] = []

    for move in plans:
        try:
            move.destination.parent.mkdir(parents=True, exist_ok=True)
            move.source.rename(move.destination)
            results.append(
                MoveResult(
                    source=move.source,
                    destination=move.destination,
                    category=move.category,
                    status="moved",
                )
            )
        except OSError as exc:
            results.append(
                MoveResult(
                    source=move.source,
                    destination=None,
                    category=move.category,
                    status="error",
                    reason=str(exc),
                )
            )

    return results


def _unique_destination(path: Path) -> Path:
    """If `path` already exists, append ' (1)', ' (2)', etc. before the
    extension until a free name is found, instead of silently
    overwriting an existing file."""
    if not path.exists():
        return path

    stem, suffix, parent = path.stem, path.suffix, path.parent
    counter = 1
    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1
