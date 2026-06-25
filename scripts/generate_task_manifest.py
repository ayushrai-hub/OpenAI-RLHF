#!/usr/bin/env python3
"""Scan the repository and emit TASKS.json — a machine-readable task index."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

MONTHS_TEST_NAMES = {"tests.py", "test.py", "test_ideal_completion.py"}
COLOSSEUM_COMPLETION_DIRS = {"CompletionA", "CompletionB", "completionA", "completionB"}
TURN_RE = re.compile(r"^Turn(\d+)$", re.IGNORECASE)


def _rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _has_any(directory: Path, names: set[str]) -> bool:
    return any((directory / name).is_file() for name in names)


def _infer_domain(name: str, files: list[str]) -> str:
    lower = name.lower()
    keywords = {
        "finance": ("bond", "libor", "bank", "finance", "trading", "swap"),
        "ml": ("model", "kernel", "xgboost", "torch", "tensorflow", "pytorch", "crf"),
        "web": ("html", "selenium", "playwright", "electron", "flask", "django"),
        "algorithms": ("puzzle", "graph", "tsp", "lagrangian", "monte", "sort"),
        "data": ("csv", "json", "pandas", "arima", "geocode", "wind"),
        "nlp": ("langchain", "openai", "embedding", "sentence"),
        "visualization": ("matplotlib", "plot", "tkinter", "gui"),
        "systems": ("cpp", "java", "swift", "firmware", "uart"),
    }
    blob = lower + " " + " ".join(f.lower() for f in files)
    for domain, terms in keywords.items():
        if any(t in blob for t in terms):
            return domain
    return "general"


def discover_months_tasks() -> list[dict]:
    months_root = REPO_ROOT / "Months"
    if not months_root.is_dir():
        return []

    tasks: list[dict] = []
    for ideal in sorted(months_root.rglob("ideal_completion.py")):
        task_dir = ideal.parent
        test_files = [
            f.name
            for f in task_dir.iterdir()
            if f.is_file() and (f.name in MONTHS_TEST_NAMES or f.name.startswith("test"))
        ]
        extra = [f.name for f in task_dir.iterdir() if f.is_file() and f.suffix == ".py"]
        parts = task_dir.relative_to(months_root).parts
        month = parts[0] if parts else "unknown"

        tasks.append(
            {
                "id": _rel(task_dir).replace("/", "__"),
                "track": "months",
                "month": month,
                "name": task_dir.name,
                "path": _rel(task_dir),
                "ideal_completion": _rel(ideal),
                "test_files": sorted(test_files),
                "has_tests": bool(test_files),
                "domain": _infer_domain(task_dir.name, extra),
                "languages": sorted({f.suffix.lstrip(".") for f in task_dir.iterdir() if f.is_file()}),
            }
        )
    return tasks


def discover_colosseum_tasks() -> list[dict]:
    col_root = REPO_ROOT / "Colosseum"
    if not col_root.is_dir():
        return []

    seen: set[str] = set()
    tasks: list[dict] = []

    for turn_dir in sorted(col_root.rglob("Turn*")):
        if not turn_dir.is_dir() or not TURN_RE.match(turn_dir.name):
            continue

        task_name = turn_dir.parent.name
        branch_parts = turn_dir.relative_to(col_root).parts
        branch = branch_parts[0] if branch_parts else "unknown"
        turn_num = int(TURN_RE.match(turn_dir.name).group(1))
        task_key = _rel(turn_dir.parent)

        completions = []
        for comp_dir_name in COLOSSEUM_COMPLETION_DIRS:
            comp_dir = turn_dir / comp_dir_name
            if not comp_dir.is_dir():
                continue
            py_files = sorted(p.name for p in comp_dir.glob("*.py"))
            if py_files:
                completions.append(
                    {
                        "variant": comp_dir_name,
                        "path": _rel(comp_dir),
                        "files": py_files,
                    }
                )

        if not completions:
            continue

        if task_key not in seen:
            seen.add(task_key)
            tasks.append(
                {
                    "id": task_key.replace("/", "__"),
                    "track": "colosseum",
                    "branch": branch,
                    "name": task_name,
                    "path": task_key,
                    "turns": [],
                    "domain": _infer_domain(
                        task_name,
                        [f for c in completions for f in c["files"]],
                    ),
                }
            )

        for task in tasks:
            if task["path"] == task_key:
                task["turns"].append({"turn": turn_num, "completions": completions})
                task["turns"] = sorted(task["turns"], key=lambda t: t["turn"])
                break

    return tasks


def discover_other() -> list[dict]:
    items = []
    test_root = REPO_ROOT / "test"
    if test_root.is_dir():
        items.append(
            {
                "id": "test__django_stub",
                "track": "test",
                "name": "django_stub",
                "path": "test",
                "domain": "web",
                "description": "Minimal Django Task/Attachment models scaffold",
            }
        )
    triton_root = REPO_ROOT / "triton"
    if triton_root.is_dir() and not any(triton_root.iterdir()):
        items.append(
            {
                "id": "triton__empty",
                "track": "triton",
                "name": "triton",
                "path": "triton",
                "domain": "systems",
                "description": "Empty placeholder directory",
            }
        )
    return items


def build_manifest() -> dict:
    months = discover_months_tasks()
    colosseum = discover_colosseum_tasks()
    other = discover_other()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository": "OpenAI-RLHF",
        "description": "Coding evaluation task archive with Months (gold+tests) and Colosseum (A/B completions)",
        "summary": {
            "months_tasks": len(months),
            "colosseum_tasks": len(colosseum),
            "other": len(other),
            "total_indexed": len(months) + len(colosseum) + len(other),
        },
        "months": months,
        "colosseum": colosseum,
        "other": other,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate TASKS.json manifest")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=REPO_ROOT / "TASKS.json",
        help="Output path (default: repo root TASKS.json)",
    )
    parser.add_argument("--pretty", action="store_true", default=True)
    args = parser.parse_args()

    manifest = build_manifest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2 if args.pretty else None)
        fh.write("\n")

    print(f"Wrote {args.output}")
    print(f"  Months tasks:    {manifest['summary']['months_tasks']}")
    print(f"  Colosseum tasks: {manifest['summary']['colosseum_tasks']}")
    print(f"  Other:           {manifest['summary']['other']}")


if __name__ == "__main__":
    main()
