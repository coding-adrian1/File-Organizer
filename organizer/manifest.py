"""
Records every run as a JSON manifest so it can be undone later.
This is what makes the tool safe to actually run on a real folder —
a batch move you can't reverse is a batch move people won't trust.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from organizer.core import MoveResult

MANIFEST_DIRNAME = ".organizer_history"


def manifest_dir(directory: Path) -> Path:
    return directory / MANIFEST_DIRNAME


def write_manifest(directory: Path, results: list[MoveResult]) -> Path:
    """Write a timestamped manifest of a completed run. Returns the path written."""
    hist_dir = manifest_dir(directory)
    hist_dir.mkdir(exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    manifest_path = hist_dir / f"run-{timestamp}.json"

    moved = [
        {"source": str(r.source), "destination": str(r.destination), "category": r.category}
        for r in results
        if r.status == "moved"
    ]
    manifest_path.write_text(json.dumps({"moves": moved}, indent=2))
    return manifest_path


def latest_manifest(directory: Path) -> Path | None:
    hist_dir = manifest_dir(directory)
    if not hist_dir.exists():
        return None
    runs = sorted(hist_dir.glob("run-*.json"))
    return runs[-1] if runs else None


def undo_manifest(manifest_path: Path) -> list[MoveResult]:
    """Reverse every move recorded in a manifest. Files that were since
    renamed, deleted, or moved again are reported as skipped rather
    than causing the whole undo to fail."""
    data = json.loads(manifest_path.read_text())
    results: list[MoveResult] = []

    for move in reversed(data["moves"]):
        source = Path(move["destination"])  # currently lives at what was the destination
        destination = Path(move["source"])  # goes back to where it started
        category = move["category"]

        if not source.exists():
            results.append(
                MoveResult(source, None, category, "skipped", reason="file no longer at recorded location")
            )
            continue
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            source.rename(destination)
            results.append(MoveResult(source, destination, category, "moved"))
        except OSError as exc:
            results.append(MoveResult(source, None, category, "error", reason=str(exc)))

    manifest_path.unlink()
    return results
