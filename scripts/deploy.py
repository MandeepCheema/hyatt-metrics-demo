#!/usr/bin/env python3
"""CD (simulated): 'apply' changed DDL to Snowflake, record a deploy manifest, post status back to Atlan.

In Hyatt's real pipeline this step runs the DDL with snowsql / snowflake-connector. Here it prints the DDL,
writes deployed/manifest.json, and stamps an announcement on the Atlan term so stewards see deploy status
where they made the change.
Env: ATLAN_BASE_URL, ATLAN_API_KEY, GITHUB_SHA, GITHUB_SERVER_URL, GITHUB_REPOSITORY. Args: changed yaml paths.
"""
from __future__ import annotations
import datetime as dt, json, os, sys, pathlib
import yaml, requests

ROOT = pathlib.Path(__file__).resolve().parents[1]

def announce(base: str, key: str, m: dict, sha: str, run_url: str, post=requests.post) -> None:
    body = {"entities": [{"typeName": "AtlasGlossaryTerm", "guid": m["atlan_guid"],
            "attributes": {"qualifiedName": m.get("atlan_qualified_name") or None,
                           "announcementType": "information",
                           "announcementTitle": f"Deployed to Snowflake · {sha[:7]}",
                           "announcementMessage": f"{m['target_view']} rebuilt from Git commit {sha[:7]} at "
                                                  f"{dt.datetime.now(dt.UTC):%Y-%m-%d %H:%M} UTC. Run: {run_url}"}}]}
    # qualifiedName is required by the bulk endpoint; fetch if yaml lacks it
    if not body["entities"][0]["attributes"]["qualifiedName"]:
        r = requests.get(f"{base}/api/meta/entity/guid/{m['atlan_guid']}", params={"ignoreRelationships": "true"},
                         headers={"Authorization": f"Bearer {key}"}, timeout=30); r.raise_for_status()
        body["entities"][0]["attributes"]["qualifiedName"] = r.json()["entity"]["attributes"]["qualifiedName"]
    r = post(f"{base}/api/meta/entity/bulk", json=body, headers={"Authorization": f"Bearer {key}"}, timeout=30)
    r.raise_for_status()

def deploy(files: list[pathlib.Path], base: str, key: str, sha: str, run_url: str, announce_fn=announce) -> int:
    manifest_p = ROOT / "deployed" / "manifest.json"; manifest_p.parent.mkdir(exist_ok=True)
    manifest = json.loads(manifest_p.read_text()) if manifest_p.exists() else {}
    for f in files:
        m = yaml.safe_load(f.read_text()) or {}
        sql = (ROOT / "ddl" / f"{m['slug']}.sql").read_text()
        print(f"\n=== applying {m['target_view']} ===\n{sql}")
        manifest[m["slug"]] = {"target_view": m["target_view"], "commit": sha, "deployed_at": dt.datetime.now(dt.UTC).isoformat(),
                               "atlan_guid": m.get("atlan_guid")}
        if base and key and m.get("atlan_guid") and not str(m["atlan_guid"]).startswith("REPLACE"):
            try:
                announce_fn(base.rstrip("/"), key, m, sha, run_url)
                print(f"✓ announcement posted on Atlan term {m['name']}")
            except Exception as e:  # noqa: BLE001
                print(f"::warning::could not post announcement to Atlan for {m['name']}: {e}")
    manifest_p.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"\ndeployed {len(files)} metric(s); manifest updated")
    return 0

def main(argv: list[str]) -> int:
    files = [pathlib.Path(p) for p in argv] or sorted((ROOT / "metrics").glob("*.yaml"))
    sha = os.environ.get("GITHUB_SHA", "local")
    run_url = f"{os.environ.get('GITHUB_SERVER_URL','https://github.com')}/{os.environ.get('GITHUB_REPOSITORY','')}/actions/runs/{os.environ.get('GITHUB_RUN_ID','')}"
    return deploy(files, os.environ.get("ATLAN_BASE_URL", ""), os.environ.get("ATLAN_API_KEY", ""), sha, run_url)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
