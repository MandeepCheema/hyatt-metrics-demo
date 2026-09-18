#!/usr/bin/env python3
"""CI: validate every metric definition.

Checks: required yaml keys present; matching ddl file exists; DDL parses as Snowflake SQL;
view COMMENT equals the yaml description; target_view in yaml equals the view name in DDL.
Exit 1 with a readable report on any failure.
"""
from __future__ import annotations
import re, sys, pathlib
import yaml, sqlglot

ROOT = pathlib.Path(__file__).resolve().parents[1]
REQUIRED = ["name", "slug", "atlan_guid", "atlan_url", "description", "formula", "grain", "unit",
            "source_table", "target_view", "owners", "certificate", "last_changed_by", "last_changed_at"]

def check(yaml_path: pathlib.Path) -> list[str]:
    errs = []
    m = yaml.safe_load(yaml_path.read_text()) or {}
    for k in REQUIRED:
        if k not in m or m[k] in (None, "", []):
            errs.append(f"{yaml_path.name}: missing `{k}`")
    slug = m.get("slug") or yaml_path.stem
    sql_path = ROOT / "ddl" / f"{slug}.sql"
    if not sql_path.exists():
        return errs + [f"{yaml_path.name}: no ddl/{slug}.sql"]
    sql = sql_path.read_text()
    try:
        exprs = sqlglot.parse(sql, read="snowflake", error_level=sqlglot.ErrorLevel.RAISE)
        create = next((e for e in exprs if isinstance(e, sqlglot.exp.Create)), None)
        if create is None or create.find(sqlglot.exp.Select) is None or not create.find(sqlglot.exp.Select).expressions:
            errs.append(f"ddl/{slug}.sql: expected CREATE VIEW ... AS SELECT")
    except Exception as e:  # noqa: BLE001
        errs.append(f"ddl/{slug}.sql: does not parse as Snowflake SQL: {e}")
    cm = re.search(r"COMMENT\s*=\s*'((?:[^']|'')*)'", sql, re.S)
    if not cm:
        errs.append(f"ddl/{slug}.sql: no COMMENT")
    elif " ".join((m.get("description") or "").split()) != cm.group(1).replace("''", "'").strip():
        errs.append(f"ddl/{slug}.sql: COMMENT differs from yaml description")
    tv = re.search(r"CREATE OR REPLACE VIEW\s+([A-Z0-9_.]+)", sql, re.I)
    if not tv or tv.group(1).upper() != str(m.get("target_view", "")).upper():
        errs.append(f"ddl/{slug}.sql: view name != yaml target_view")
    if m.get("certificate") not in ("VERIFIED", "DRAFT", "DEPRECATED"):
        errs.append(f"{yaml_path.name}: certificate must be VERIFIED/DRAFT/DEPRECATED")
    return errs

def main(paths: list[str] | None = None) -> int:
    files = [pathlib.Path(p) for p in paths] if paths else sorted((ROOT / "metrics").glob("*.yaml"))
    errs = [e for f in files for e in check(f)]
    for e in errs:
        print("::error::" + e)
    print(f"validated {len(files)} metric(s): {'FAIL' if errs else 'OK'}")
    return 1 if errs else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
