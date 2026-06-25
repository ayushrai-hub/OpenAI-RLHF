#!/usr/bin/env python3
"""List indexed tasks from TASKS.json with optional filters."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "TASKS.json"


def load_manifest(path: Path) -> dict:
    if not path.is_file():
        raise SystemExit(f"Manifest not found: {path}\nRun: python scripts/generate_task_manifest.py")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="List tasks from TASKS.json")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--track", choices=["months", "colosseum", "all"], default="all")
    parser.add_argument("--domain", help="Filter by domain (finance, ml, web, ...)")
    parser.add_argument("--month", help="Filter Months tasks by month folder (e.g. Month6)")
    parser.add_argument("--has-tests", action="store_true", help="Months only: tasks with test files")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of table")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    rows: list[dict] = []

    if args.track in ("months", "all"):
        for task in manifest.get("months", []):
            if args.month and task.get("month") != args.month:
                continue
            if args.domain and task.get("domain") != args.domain:
                continue
            if args.has_tests and not task.get("has_tests"):
                continue
            rows.append(task)

    if args.track in ("colosseum", "all"):
        for task in manifest.get("colosseum", []):
            if args.domain and task.get("domain") != args.domain:
                continue
            rows.append(task)

    if args.json:
        print(json.dumps(rows, indent=2))
        return

    if not rows:
        print("No tasks matched filters.")
        return

    print(f"{'TRACK':<10} {'DOMAIN':<14} {'NAME':<28} PATH")
    print("-" * 90)
    for row in rows:
        track = row.get("track", "?")
        domain = row.get("domain", "?")
        name = row.get("name", "?")[:28]
        path = row.get("path", "?")
        print(f"{track:<10} {domain:<14} {name:<28} {path}")

    print(f"\nTotal: {len(rows)}")


if __name__ == "__main__":
    main()
