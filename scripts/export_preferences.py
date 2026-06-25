#!/usr/bin/env python3
"""Export Colosseum A/B completion pairs to JSONL for preference-learning research."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def read_py_files(directory: Path) -> dict[str, str]:
    if not directory.is_dir():
        return {}
    return {
        p.name: p.read_text(encoding="utf-8", errors="replace")
        for p in sorted(directory.glob("*.py"))
    }


def export_colosseum(col_root: Path) -> list[dict]:
    records = []
    for turn_dir in sorted(col_root.rglob("Turn*")):
        if not turn_dir.is_dir():
            continue
        task_path = turn_dir.parent
        turn_name = turn_dir.name

        comp_a_dirs = [turn_dir / d for d in ("CompletionA", "completionA") if (turn_dir / d).is_dir()]
        comp_b_dirs = [turn_dir / d for d in ("CompletionB", "completionB") if (turn_dir / d).is_dir()]

        if not comp_a_dirs or not comp_b_dirs:
            continue

        a_files = read_py_files(comp_a_dirs[0])
        b_files = read_py_files(comp_b_dirs[0])
        if not a_files and not b_files:
            continue

        records.append(
            {
                "task": task_path.relative_to(REPO_ROOT).as_posix(),
                "turn": turn_name,
                "completion_a": a_files,
                "completion_b": b_files,
                "metadata": {
                    "track": "colosseum",
                    "note": "No prompt text in repo — code artifacts only",
                },
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Export Colosseum pairs to JSONL")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=REPO_ROOT / "exports" / "colosseum_pairs.jsonl",
    )
    args = parser.parse_args()

    col_root = REPO_ROOT / "Colosseum"
    if not col_root.is_dir():
        raise SystemExit("Colosseum/ not found")

    records = export_colosseum(col_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Exported {len(records)} turn-level pairs to {args.output}")


if __name__ == "__main__":
    main()
