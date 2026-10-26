#!/usr/bin/env python3
"""Validate registry.csv and rebuild the registry tables in README.md and README.en.md.

Usage:
    python validate.py          # validate CSV and rewrite the README tables
    python validate.py --check  # validate CSV and fail if the README tables are stale (CI)

No network access. Never calls any Anthropic endpoint.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "registry.csv"
README_FILES = [ROOT / "README.md", ROOT / "README.en.md"]

COLUMNS = ["domain", "category", "checked_at", "method", "reporter", "source", "notes"]
CATEGORIES = {"category0", "category1", "category2", "category3", "category4"}
METHODS = {"devtools_response", "dialog_observed", "third_party_report"}
DOMAIN_RE = re.compile(r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9-]{2,63}$")
START = "<!-- registry:start -->"
END = "<!-- registry:end -->"


def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def load_rows() -> list[dict[str, str]]:
    if not CSV_PATH.exists():
        fail(f"{CSV_PATH.name} not found")
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != COLUMNS:
            fail(f"header must be exactly: {','.join(COLUMNS)}; got: {reader.fieldnames}")
        rows = list(reader)
    errors: list[str] = []
    seen: set[tuple[str, str]] = set()
    today = date.today()
    for i, row in enumerate(rows, start=2):  # line 1 is the header
        where = f"line {i}"
        if any(v is None for v in row.values()):
            errors.append(f"{where}: wrong number of columns")
            continue
        domain = row["domain"]
        if domain != domain.strip() or domain != domain.lower():
            errors.append(f"{where}: domain must be lowercase without surrounding spaces: {domain!r}")
        if "://" in domain or "/" in domain:
            errors.append(f"{where}: domain must not contain a scheme or a path: {domain!r}")
        elif not DOMAIN_RE.match(domain):
            errors.append(f"{where}: not a valid domain: {domain!r}")
        if row["category"] not in CATEGORIES:
            errors.append(f"{where}: category must be one of {sorted(CATEGORIES)}; got {row['category']!r}")
        try:
            checked = date.fromisoformat(row["checked_at"])
            if checked > today:
                errors.append(f"{where}: checked_at is in the future: {row['checked_at']}")
        except ValueError:
            errors.append(f"{where}: checked_at must be YYYY-MM-DD; got {row['checked_at']!r}")
        if row["method"] not in METHODS:
            errors.append(f"{where}: method must be one of {sorted(METHODS)}; got {row['method']!r}")
        for col in ("reporter", "source"):
            if not row[col].strip():
                errors.append(f"{where}: {col} must not be empty")
        src = row["source"].strip()
        if src.startswith("evidence/") and not (ROOT / src).exists():
            errors.append(f"{where}: evidence file not found: {src}")
        key = (domain, row["checked_at"])
        if key in seen:
            errors.append(f"{where}: duplicate domain+date: {domain} {row['checked_at']}")
        seen.add(key)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    return rows


def md_cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ").strip()


def md_source(src: str) -> str:
    src = src.strip()
    if src.startswith("http://") or src.startswith("https://"):
        label = src.split("://", 1)[1]
        if len(label) > 60:
            label = label[:57] + "..."
        return f"[{md_cell(label)}]({src})"
    if src.startswith("evidence/"):
        return f"[{md_cell(src.split('/', 1)[1])}]({src})"
    return md_cell(src)


def build_table(rows: list[dict[str, str]]) -> str:
    rows = sorted(rows, key=lambda r: (r["category"], r["domain"], r["checked_at"]))
    lines = [
        "| domain | category | checked_at | method | reporter | source | notes |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        cells = [
            md_cell(r["domain"]),
            md_cell(r["category"]),
            md_cell(r["checked_at"]),
            md_cell(r["method"]),
            md_cell(r["reporter"]),
            md_source(r["source"]),
            md_cell(r["notes"]),
        ]
        lines.append("| " + " | ".join(cells) + " |")
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["category"]] = counts.get(r["category"], 0) + 1
    summary = ", ".join(f"{c}: {n}" for c, n in sorted(counts.items()))
    header = f"_{len(rows)} entries ({summary}). Generated from registry.csv by validate.py, do not edit by hand._"
    return f"{START}\n{header}\n\n" + "\n".join(lines) + f"\n{END}"


def update_readme(path: Path, table: str, check: bool) -> bool:
    if not path.exists():
        fail(f"{path.name} not found")
    text = path.read_text(encoding="utf-8")
    if START not in text or END not in text:
        fail(f"{path.name}: markers {START} / {END} not found")
    pre, rest = text.split(START, 1)
    _, post = rest.split(END, 1)
    new_text = pre + table + post
    if new_text == text:
        return False
    if check:
        print(f"ERROR: {path.name} table is stale; run: python validate.py", file=sys.stderr)
        sys.exit(1)
    path.write_text(new_text, encoding="utf-8", newline="\n")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="do not write; fail if the README tables are stale")
    args = parser.parse_args()
    rows = load_rows()
    table = build_table(rows)
    changed = [p.name for p in README_FILES if update_readme(p, table, args.check)]
    print(f"OK: {len(rows)} rows valid")
    if changed:
        print("Updated: " + ", ".join(changed))
    else:
        print("README tables are up to date")


if __name__ == "__main__":
    main()
