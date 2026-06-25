#!/usr/bin/env python3
"""Discover and run unittest tasks under Months/."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "TASKS.json"

TEST_CANDIDATES = ("tests.py", "test.py", "test_ideal_completion.py")


def load_months_tasks(manifest_path: Path) -> list[dict]:
    if manifest_path.is_file():
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return [t for t in data.get("months", []) if t.get("has_tests")]

    # Fallback scan if manifest missing
    tasks = []
    months_root = REPO_ROOT / "Months"
    for ideal in months_root.rglob("ideal_completion.py"):
        task_dir = ideal.parent
        test_file = next((task_dir / n for n in TEST_CANDIDATES if (task_dir / n).is_file()), None)
        if test_file:
            tasks.append({"path": str(task_dir.relative_to(REPO_ROOT)), "test_files": [test_file.name]})
    return tasks


def run_task(task_dir: Path, test_name: str, timeout: int) -> tuple[bool, str]:
    cmd = [sys.executable, test_name]
    try:
        result = subprocess.run(
            cmd,
            cwd=task_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT after {timeout}s"

    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode == 0, output.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Months eval unit tests")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--path", help="Run a single task directory (relative to repo root)")
    parser.add_argument("--month", help="Only run tasks under this month folder")
    parser.add_argument("--domain", help="Only run tasks with this domain tag")
    parser.add_argument("--limit", type=int, default=0, help="Max tasks to run (0 = all)")
    parser.add_argument("--timeout", type=int, default=120, help="Per-task timeout seconds")
    parser.add_argument("--fail-fast", action="store_true")
    args = parser.parse_args()

    if args.path:
        task_dirs = [REPO_ROOT / args.path]
        specs = [{"path": args.path, "test_files": [n for n in TEST_CANDIDATES if (REPO_ROOT / args.path / n).is_file()]}]
    else:
        specs = load_months_tasks(args.manifest)
        if args.month:
            specs = [s for s in specs if Path(s["path"]).parts[1:2] == (args.month,) or s["path"].startswith(f"Months/{args.month}")]
        if args.domain:
            specs = [s for s in specs if s.get("domain") == args.domain]
        if args.limit:
            specs = specs[: args.limit]
        task_dirs = [REPO_ROOT / s["path"] for s in specs]

    passed = failed = skipped = 0
    failures: list[tuple[str, str]] = []

    for spec, task_dir in zip(specs, task_dirs):
        if not task_dir.is_dir():
            skipped += 1
            continue

        test_files = spec.get("test_files") or [n for n in TEST_CANDIDATES if (task_dir / n).is_file()]
        if not test_files:
            skipped += 1
            continue

        test_name = test_files[0]
        rel = task_dir.relative_to(REPO_ROOT)
        ok, output = run_task(task_dir, test_name, args.timeout)

        if ok:
            passed += 1
            print(f"PASS  {rel}")
        else:
            failed += 1
            print(f"FAIL  {rel}")
            failures.append((str(rel), output))
            if args.fail_fast:
                break

    print()
    print(f"Results: {passed} passed, {failed} failed, {skipped} skipped")

    if failures:
        print("\n--- Failures ---")
        for path, output in failures[:10]:
            print(f"\n## {path}\n{output[:2000]}")

    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
