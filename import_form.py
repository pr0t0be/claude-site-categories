#!/usr/bin/env python3
"""Pull Google Form responses (published-to-web CSV) into candidates_form.csv.

Candidates are not registry rows. A person reviews them and copies confirmed
observations into registry.csv. Rows already present keep their `reviewed` mark.

Usage:
    python import_form.py --url "https://docs.google.com/spreadsheets/d/e/.../pub?output=csv"
    python import_form.py --file responses.csv      # a CSV downloaded by hand

No Google credentials are used: the sheet must be published to the web as CSV
(see FORM_setup.md). Nothing is sent to any Anthropic endpoint.
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_PATH = ROOT / "candidates_form.csv"
COLUMNS = ["domain", "category_guess", "dialog_seen", "date", "product", "screenshot", "comment", "submitted_at", "reviewed"]

# Form question -> internal field. Matching is by keywords in the header, case-insensitive,
# so small edits to the question text do not break the import.
FIELD_KEYWORDS = {
    "submitted_at": ["timestamp", "отметка времени"],
    "domain": ["domain", "домен"],
    "dialog_seen": ["what did you see", "что вы увидели"],
    "date": ["date", "дата"],
    "product": ["product", "продукт"],
    "screenshot": ["screenshot", "скриншот"],
    "comment": ["comment", "комментар"],
}
DOMAIN_RE = re.compile(r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$")


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def guess_category(dialog: str, comment: str) -> str:
    d = (dialog + " " + comment).lower()
    m = re.search(r"category\s*([0-4])", d)
    if m:
        return f"category{m.group(1)}"
    if "site-level permissions are disabled" in d or "every action" in d:
        return "category3"
    if "right to access content" in d:
        return "category4"
    if "blocked" in d:
        return "category1"
    if "always allow" in d:
        return "category0"
    return "unknown"


def normalize_domain(raw: str) -> str:
    s = raw.strip().lower()
    s = re.sub(r"^[a-z]+://", "", s)
    s = s.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0].split(":", 1)[0]
    return s.strip(".")


def normalize_date(raw: str) -> str:
    s = raw.strip()
    # ISO 2026-10-24; European 24.10.2026; Google Forms (US locale) 10/24/2026
    for pat, order in (
        (r"^(\d{4})-(\d{1,2})-(\d{1,2})", (1, 2, 3)),
        (r"^(\d{1,2})\.(\d{1,2})\.(\d{4})", (3, 2, 1)),
        (r"^(\d{1,2})/(\d{1,2})/(\d{4})", (3, 1, 2)),
    ):
        m = re.match(pat, s)
        if m:
            y, mo, d = (int(m.group(i)) for i in order)
            if mo > 12 and d <= 12:  # sheet locale was day/month after all
                mo, d = d, mo
            return f"{y:04d}-{mo:02d}-{d:02d}"
    return s


def map_headers(headers: list[str]) -> dict[str, int]:
    mapping: dict[str, int] = {}
    for i, h in enumerate(headers):
        hl = h.lower()
        for field, keys in FIELD_KEYWORDS.items():
            if field not in mapping and any(k in hl for k in keys):
                mapping[field] = i
                break
    missing = [f for f in ("domain", "dialog_seen") if f not in mapping]
    if missing:
        log(f"ERROR: cannot find columns for {missing} in headers: {headers}")
        sys.exit(1)
    return mapping


def read_source(url: str | None, file: str | None) -> str:
    if file:
        return Path(file).read_text(encoding="utf-8-sig")
    assert url
    req = urllib.request.Request(url, headers={"User-Agent": "claude-site-categories-import"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8-sig")


def load_existing() -> dict[tuple[str, str, str], dict[str, str]]:
    if not OUT_PATH.exists():
        return {}
    with OUT_PATH.open(encoding="utf-8", newline="") as f:
        return {(r["domain"], r["date"], r["category_guess"]): r for r in csv.DictReader(f)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--url", help="published-to-web CSV link of the responses sheet")
    g.add_argument("--file", help="a responses CSV on disk")
    parser.add_argument("--dry-run", action="store_true", help="print candidates, do not write")
    args = parser.parse_args()

    text = read_source(args.url, args.file)
    reader = csv.reader(io.StringIO(text))
    try:
        headers = next(reader)
    except StopIteration:
        log("ERROR: empty CSV")
        sys.exit(1)
    mapping = map_headers(headers)

    def cell(row: list[str], field: str) -> str:
        i = mapping.get(field)
        return row[i].strip() if i is not None and i < len(row) else ""

    rows = load_existing()
    new = skipped = 0
    for row in reader:
        if not any(row):
            continue
        domain = normalize_domain(cell(row, "domain"))
        if not DOMAIN_RE.match(domain):
            skipped += 1
            log(f"skipped, not a domain: {cell(row, 'domain')!r}")
            continue
        dialog = cell(row, "dialog_seen")
        comment = cell(row, "comment")
        screenshot = cell(row, "screenshot")
        if re.search(r"header", screenshot + " " + comment, re.I):
            # Headers tab may contain the login token: do not keep the link.
            screenshot = "REMOVED (mentioned Headers tab)"
        date = normalize_date(cell(row, "date")) or normalize_date(cell(row, "submitted_at"))
        guess = guess_category(dialog, comment)
        key = (domain, date, guess)
        if key in rows:
            continue
        rows[key] = {
            "domain": domain,
            "category_guess": guess,
            "dialog_seen": dialog[:120],
            "date": date,
            "product": cell(row, "product"),
            "screenshot": screenshot,
            "comment": re.sub(r"\s+", " ", comment)[:300],
            "submitted_at": cell(row, "submitted_at"),
            "reviewed": "",
        }
        new += 1

    ordered = sorted(rows.values(), key=lambda r: (r["reviewed"] != "", r["domain"], r["date"]))
    out = sys.stdout if args.dry_run else OUT_PATH.open("w", encoding="utf-8", newline="")
    w = csv.DictWriter(out, fieldnames=COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(ordered)
    if out is not sys.stdout:
        out.close()
    log(f"candidates: {len(ordered)} total, {new} new, {skipped} skipped; reviewed marks kept")


if __name__ == "__main__":
    main()
