"""
Command-line interface.

    organizer organize ~/Downloads
    organizer organize ~/Downloads --dry-run
    organizer undo ~/Downloads
    organizer rename ~/Downloads/Images "trip_{n:03d}{ext}"
"""
import argparse
import sys
from pathlib import Path

from organizer.core import plan_organization, apply_plan
from organizer.manifest import write_manifest, latest_manifest, undo_manifest
from organizer.rename import plan_rename, apply_rename


def main(argv=None):
    parser = argparse.ArgumentParser(prog="organizer", description="Organize and batch-rename files.")
    sub = parser.add_subparsers(dest="command", required=True)

    organize_p = sub.add_parser("organize", help="Sort files into category subfolders")
    organize_p.add_argument("directory", type=Path)
    organize_p.add_argument("--dry-run", action="store_true", help="Show what would happen without moving anything")
    organize_p.add_argument("--include-hidden", action="store_true", help="Include dotfiles")

    undo_p = sub.add_parser("undo", help="Reverse the most recent organize run in a directory")
    undo_p.add_argument("directory", type=Path)

    rename_p = sub.add_parser("rename", help="Batch-rename files using a pattern")
    rename_p.add_argument("directory", type=Path)
    rename_p.add_argument("pattern", help='e.g. "trip_{n:03d}{ext}" or "{date}_{name}{ext}"')
    rename_p.add_argument("--start", type=int, default=1)
    rename_p.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)

    if not args.directory.is_dir():
        print(f"Error: {args.directory} is not a directory", file=sys.stderr)
        return 1

    if args.command == "organize":
        return _run_organize(args)
    elif args.command == "undo":
        return _run_undo(args)
    elif args.command == "rename":
        return _run_rename(args)


def _run_organize(args) -> int:
    plans = plan_organization(args.directory, include_hidden=args.include_hidden)
    if not plans:
        print("Nothing to organize — no loose files found.")
        return 0

    if args.dry_run:
        print(f"Would move {len(plans)} file(s):")
        for p in plans:
            print(f"  {p.source.name}  →  {p.category}/{p.destination.name}")
        return 0

    results = apply_plan(plans)
    moved = [r for r in results if r.status == "moved"]
    errors = [r for r in results if r.status == "error"]

    write_manifest(args.directory, results)

    print(f"Moved {len(moved)} file(s) into {len(set(r.category for r in moved))} categories.")
    for r in errors:
        print(f"  Skipped {r.source.name}: {r.reason}", file=sys.stderr)

    if moved:
        print("Run 'organizer undo <directory>' to reverse this.")
    return 1 if errors else 0


def _run_undo(args) -> int:
    manifest_path = latest_manifest(args.directory)
    if manifest_path is None:
        print("No previous organize run found to undo.")
        return 1

    results = undo_manifest(manifest_path)
    moved = [r for r in results if r.status == "moved"]
    problems = [r for r in results if r.status != "moved"]

    print(f"Restored {len(moved)} file(s).")
    for r in problems:
        print(f"  Could not restore {r.source.name}: {r.reason}", file=sys.stderr)
    return 1 if problems else 0


def _run_rename(args) -> int:
    plans = plan_rename(args.directory, args.pattern, start=args.start)
    if not plans:
        print("No files to rename.")
        return 0

    if args.dry_run:
        print(f"Would rename {len(plans)} file(s):")
        for p in plans:
            print(f"  {p.source.name}  →  {p.destination.name}")
        return 0

    apply_rename(plans)
    print(f"Renamed {len(plans)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
