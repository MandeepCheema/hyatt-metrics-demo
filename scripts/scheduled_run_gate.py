#!/usr/bin/env python3
"""The scheduled-run gate (design slide 12, layer 2).

Run this as the first step of the nightly rebuild. If any Atlan-originated PR (branch atlan/*) is still open,
an approved-but-unmerged definition exists: HOLD the rebuild instead of rebuilding stale definitions.
Env: GITHUB_TOKEN, GITHUB_REPOSITORY (owner/repo).
"""
from __future__ import annotations
import os, sys, requests

def open_atlan_prs(repo: str, token: str, get=requests.get) -> list[dict]:
    r = get(f"https://api.github.com/repos/{repo}/pulls", params={"state": "open", "per_page": 100},
            headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}, timeout=30)
    r.raise_for_status()
    return [p for p in r.json() if p.get("head", {}).get("ref", "").startswith("atlan/")]

def main() -> int:
    repo, token = os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get("GITHUB_TOKEN", "")
    prs = open_atlan_prs(repo, token)
    if prs:
        print("::error::HOLD: approved-but-unmerged metric changes exist. Merge or close them before rebuilding:")
        for p in prs:
            print(f"  - #{p['number']} {p['title']}  {p['html_url']}")
        return 1
    print("gate open: no pending Atlan changes; rebuild may proceed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
