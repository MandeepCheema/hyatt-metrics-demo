#!/usr/bin/env python3
"""CI: the Atlan gate. For each changed metric, re-read the glossary term from Atlan and require
certificateStatus == VERIFIED. This is 'one gate, two conditions' from the design: checks green AND the
governed definition is still approved in Atlan at merge time.

Env: ATLAN_BASE_URL, ATLAN_API_KEY. Args: changed yaml paths (defaults to all).
"""
from __future__ import annotations
import os, sys, pathlib
import yaml, requests

ROOT = pathlib.Path(__file__).resolve().parents[1]

def fetch_term(base: str, key: str, guid: str) -> dict:
    r = requests.get(f"{base.rstrip('/')}/api/meta/entity/guid/{guid}", params={"ignoreRelationships": "true"},
                     headers={"Authorization": f"Bearer {key}"}, timeout=30)
    r.raise_for_status()
    return r.json().get("entity", {})

def gate(files: list[pathlib.Path], base: str, key: str, fetch=fetch_term) -> int:
    failures = 0
    for f in files:
        m = yaml.safe_load(f.read_text()) or {}
        guid = m.get("atlan_guid", "")
        if not guid or guid.startswith("REPLACE"):
            print(f"::warning::{f.name}: no Atlan guid; gate skipped"); continue
        try:
            ent = fetch(base, key, guid)
        except Exception as e:  # noqa: BLE001
            print(f"::error::{f.name}: could not read term {guid} from Atlan: {e}"); failures += 1; continue
        a = ent.get("attributes", {})
        cert = a.get("certificateStatus")
        state = ent.get("status")
        if state != "ACTIVE":
            print(f"::error::{f.name}: term {a.get('name')} is {state} in Atlan"); failures += 1
        elif cert != "VERIFIED":
            print(f"::error::{f.name}: term {a.get('name')} is {cert or 'uncertified'} in Atlan; needs VERIFIED"); failures += 1
        else:
            print(f"✓ {a.get('name')} is VERIFIED in Atlan (owners: {', '.join(a.get('ownerUsers') or []) or '—'})")
    print("atlan gate:", "FAIL" if failures else "OK")
    return 1 if failures else 0

def main(argv: list[str]) -> int:
    base, key = os.environ.get("ATLAN_BASE_URL", ""), os.environ.get("ATLAN_API_KEY", "")
    if not base or not key:
        print("::error::ATLAN_BASE_URL / ATLAN_API_KEY not set"); return 1
    files = [pathlib.Path(p) for p in argv] or sorted((ROOT / "metrics").glob("*.yaml"))
    return gate(files, base, key)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
