#!/usr/bin/env python3
"""GitHub radar: find candidate domains in anthropics/claude-code issues and comments.

Searches public issues for phrases that usually accompany a category3 or blocked site
("Site-level permissions are disabled", "category3", "cat3", "url_hash_check",
"per-action approval"), extracts hostnames mentioned near those phrases and writes
them to candidates_github.csv. Candidates are NOT registry entries: a person reviews
each one and, if the source really states the observation, adds a row to registry.csv
as third_party_report.

Only GitHub is queried. Nothing is sent to any Anthropic endpoint.
Uses the `gh` CLI if installed (authenticated search, higher rate limit), otherwise
plain unauthenticated GitHub REST (10 searches per minute). No secrets in this file.

Usage:
    python radar_github.py            # update candidates_github.csv
    python radar_github.py --dry-run  # print candidates, do not write
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT_PATH = ROOT / "candidates_github.csv"
REPO = "anthropics/claude-code"
ISSUES_PATH = ROOT / "candidates_github_issues.csv"
PHRASES = [
    '"Site-level permissions are disabled"',
    '"site-level permissions"',
    '"prompts on every action"',
    "category3",
    "cat3",
    "url_hash_check",
    '"per-action approval"',
]
MAX_PAGES_PER_PHRASE = 3
MAX_ISSUES = 300
COLUMNS = ["domain", "category_guess", "issue_url", "issue_date", "quote", "reviewed"]
ISSUE_COLUMNS = ["issue_url", "issue_date", "title", "domains_found"]

HOST_RE = re.compile(r"(?<![\w@/.\-])((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,24})(?![\w\-])", re.I)
EXCLUDE_SUFFIXES = (
    "github.com", "githubusercontent.com", "github.io", "anthropic.com", "claude.ai", "claude.com",
    "localhost", "example.com", "example.org", "example.net", "w3.org", "schema.org",
)
# Only hostnames ending in a real public TLD are kept. Issue text is full of code
# identifiers that look like hostnames (permissions.allow, date.now, c.action).
# "md" (Moldova) is left out on purpose: it matches CLAUDE.md and friends.
# Extend the list if a real site is being dropped.
TLDS = {
    # generic
    "com", "net", "org", "info", "biz", "edu", "gov", "mil", "int", "io", "ai", "app", "dev", "co",
    "me", "tv", "cc", "cloud", "tech", "online", "site", "store", "shop", "xyz", "pro", "club",
    "blog", "news", "page", "live", "studio", "agency", "digital", "design", "media", "team",
    "space", "world", "zone", "one", "top", "today", "finance", "bank", "travel", "health",
    # country codes (common ones)
    "ru", "su", "by", "kz", "ua", "uz", "ge", "am", "az", "kg", "ee", "lv", "lt", "pl", "cz",
    "sk", "hu", "ro", "bg", "rs", "hr", "si", "gr", "tr", "il", "ae", "sa", "ir", "eg", "za", "ng",
    "ke", "uk", "ie", "fr", "de", "nl", "be", "lu", "ch", "at", "it", "es", "pt", "se", "no", "dk",
    "fi", "is", "us", "ca", "mx", "br", "ar", "cl", "co", "pe", "au", "nz", "jp", "kr", "cn", "hk",
    "tw", "sg", "my", "th", "vn", "id", "ph", "in", "pk", "bd", "lk", "eu", "asia", "рф",
}
WINDOW = 150


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def gh_available() -> bool:
    return shutil.which("gh") is not None


def api_get(endpoint: str, params: dict[str, str]) -> object:
    """GET a GitHub REST endpoint via gh (if present) or plain HTTPS. Returns parsed JSON."""
    if gh_available():
        cmd = ["gh", "api", "-X", "GET", endpoint]
        for k, v in params.items():
            cmd += ["-f", f"{k}={v}"]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if r.returncode != 0:
            raise RuntimeError(f"gh api {endpoint} failed: {r.stderr.strip()[:300]}")
        return json.loads(r.stdout)
    url = f"https://api.github.com/{endpoint}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "claude-site-categories-radar"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_issues() -> dict[str, dict]:
    """Return {html_url: issue} for every issue matching any phrase."""
    found: dict[str, dict] = {}
    for phrase in PHRASES:
        for page in range(1, MAX_PAGES_PER_PHRASE + 1):
            q = f"repo:{REPO} {phrase}"
            try:
                data = api_get("search/issues", {"q": q, "per_page": "100", "page": str(page)})
            except Exception as e:  # noqa: BLE001
                log(f"search failed for {phrase!r} page {page}: {e}")
                break
            items = data.get("items", []) if isinstance(data, dict) else []
            for it in items:
                if "pull_request" in it:
                    continue
                found.setdefault(it["html_url"], it)
            log(f"{phrase}: page {page}, {len(items)} items, total unique {len(found)}")
            if len(items) < 100 or len(found) >= MAX_ISSUES:
                break
            if not gh_available():
                time.sleep(7)  # unauthenticated search: 10 requests per minute
        if len(found) >= MAX_ISSUES:
            break
    return found


def issue_comments(number: int) -> list[str]:
    texts: list[str] = []
    for page in range(1, 6):
        try:
            data = api_get(f"repos/{REPO}/issues/{number}/comments", {"per_page": "100", "page": str(page)})
        except Exception as e:  # noqa: BLE001
            log(f"comments for #{number} page {page} failed: {e}")
            break
        if not isinstance(data, list) or not data:
            break
        texts += [c.get("body") or "" for c in data]
        if len(data) < 100:
            break
    return texts


def guess_category(window: str) -> str:
    w = window.lower()
    if re.search(r"category\s*3|\bcat3\b|site-level permissions are disabled|force-?prompt|per-action|every action|each action", w):
        return "category3"
    if re.search(r"category\s*1|\bcat1\b|blocked\.html|fully blocked", w):
        return "category1"
    if re.search(r"category\s*4|\bcat4\b|right to access content", w):
        return "category4"
    if re.search(r"category\s*2|\bcat2\b", w):
        return "category2"
    if re.search(r"category\s*0|\bcat0\b|always allow works", w):
        return "category0"
    return "unknown"


def extract(text: str) -> dict[str, tuple[str, str]]:
    """Return {domain: (category_guess, quote)} for one text."""
    out: dict[str, tuple[str, str]] = {}
    for m in HOST_RE.finditer(text):
        host = m.group(1).lower().strip(".")
        tld = host.rsplit(".", 1)[-1]
        if tld not in TLDS:
            continue
        if any(host == s or host.endswith("." + s) for s in EXCLUDE_SUFFIXES):
            continue
        if any(len(label) == 0 for label in host.split(".")):
            continue
        window = text[max(0, m.start() - WINDOW): m.end() + WINDOW]
        guess = guess_category(window)
        quote = re.sub(r"\s+", " ", window).strip()
        if len(quote) > 200:
            quote = quote[:197] + "..."
        prev = out.get(host)
        if prev is None or (prev[0] == "unknown" and guess != "unknown"):
            out[host] = (guess, quote)
    return out


def load_existing() -> dict[tuple[str, str], dict[str, str]]:
    if not OUT_PATH.exists():
        return {}
    with OUT_PATH.open(encoding="utf-8", newline="") as f:
        return {(r["domain"], r["issue_url"]): r for r in csv.DictReader(f)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="print candidates, do not write the CSV")
    args = parser.parse_args()

    log("backend: " + ("gh CLI" if gh_available() else "unauthenticated GitHub REST"))
    issues = search_issues()
    log(f"{len(issues)} issues to scan")

    existing = load_existing()
    rows: dict[tuple[str, str], dict[str, str]] = dict(existing)
    issue_rows: list[dict[str, str]] = []
    new = 0
    for url, it in sorted(issues.items(), key=lambda kv: kv[1]["number"]):
        text = (it.get("title") or "") + "\n" + (it.get("body") or "")
        if it.get("comments", 0):
            text += "\n" + "\n".join(issue_comments(it["number"]))
        found = extract(text)
        issue_rows.append({
            "issue_url": url,
            "issue_date": (it.get("created_at") or "")[:10],
            "title": re.sub(r"\s+", " ", it.get("title") or "").strip(),
            "domains_found": str(len(found)),
        })
        for host, (guess, quote) in found.items():
            key = (host, url)
            if key in rows:
                continue
            rows[key] = {
                "domain": host,
                "category_guess": guess,
                "issue_url": url,
                "issue_date": (it.get("created_at") or "")[:10],
                "quote": quote,
                "reviewed": "",
            }
            new += 1

    ordered = sorted(rows.values(), key=lambda r: (r["category_guess"] == "unknown", r["domain"], r["issue_url"]))
    if args.dry_run:
        w = csv.DictWriter(sys.stdout, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(ordered)
    else:
        with OUT_PATH.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
            w.writeheader()
            w.writerows(ordered)
        with ISSUES_PATH.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=ISSUE_COLUMNS, lineterminator="\n")
            w.writeheader()
            w.writerows(sorted(issue_rows, key=lambda r: r["issue_date"], reverse=True))
        log(f"matched issues written to {ISSUES_PATH.name} ({len(issue_rows)}); issues without domains are still worth a look")
    log(f"candidates: {len(ordered)} total, {new} new, reviewed flags kept from the previous file")


if __name__ == "__main__":
    main()
