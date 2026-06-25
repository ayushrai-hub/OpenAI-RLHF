#!/usr/bin/env python3
"""Validate repository structure and report common issues."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def validate(manifest_path: Path) -> dict:
    report = {
        "ok": True,
        "warnings": [],
        "errors": [],
        "stats": {},
    }

    def warn(msg: str) -> None:
        report["warnings"].append(msg)

    def err(msg: str) -> None:
        report["errors"].append(msg)
        report["ok"] = False

    for name in ("Colosseum", "Months"):
        p = REPO_ROOT / name
        if not p.is_dir():
            err(f"Missing required directory: {name}/")

    triton = REPO_ROOT / "triton"
    if triton.is_dir() and not any(triton.iterdir()):
        warn("triton/ is empty (placeholder only)")

    pycache = list(REPO_ROOT.rglob("__pycache__"))
    if pycache:
        warn(f"Found {len(pycache)} __pycache__ directories (consider gitignoring)")

    readme = REPO_ROOT / "README.md"
    if readme.is_file() and len(readme.read_text(encoding="utf-8").strip()) < 50:
        warn("README.md is very short")

    if not manifest_path.is_file():
        warn(f"TASKS.json missing — run scripts/generate_task_manifest.py")
    else:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        report["stats"] = data.get("summary", {})

    docs = REPO_ROOT / "docs"
    if not docs.is_dir():
        warn("docs/ directory missing")

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate OpenAI-RLHF repository")
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "TASKS.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = validate(args.manifest)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status = "OK" if report["ok"] else "ISSUES FOUND"
        print(f"Validation: {status}")
        if report["stats"]:
            print(f"Indexed tasks: {report['stats']}")
        for w in report["warnings"]:
            print(f"  WARN: {w}")
        for e in report["errors"]:
            print(f"  ERROR: {e}")

    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
