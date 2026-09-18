# hyatt-metrics-demo — governed metric definitions (synthetic)

**Source of truth for definitions: Atlan.** This repo is the *system of record* Git keeps, exactly as in Hyatt's
current architecture: one `ddl/<metric>.sql` per Snowflake view, plus a `metrics/<metric>.yaml` sidecar carrying the
governed definition (formula, grain, owners, certificate, Atlan link).

## The loop
1. A steward edits a term in the **Hyatt Metrics** glossary in Atlan; a change-management governance workflow routes approval.
2. When the approved change is applied, Atlan fires a signed webhook.
3. The write-back service regenerates `metrics/<slug>.yaml` + `ddl/<slug>.sql` and opens a PR on branch `atlan/<slug>`.
4. CI: `validate` (schema, Snowflake DDL parse, yaml↔sql consistency) and `atlan-gate` (re-reads the term; requires VERIFIED).
5. A human merges. `deploy` applies the DDL (simulated here) and posts a "Deployed" announcement back on the Atlan term.
6. `nightly-rebuild` runs the **scheduled-run gate** first: if any `atlan/*` PR is open, the rebuild holds.

**Rule the whole design turns on:** an approved change is not applied until its pull request merges.

Do not hand-edit `metrics/` or `ddl/` — change the term in Atlan.
