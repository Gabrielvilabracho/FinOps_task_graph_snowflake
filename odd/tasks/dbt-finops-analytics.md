# Native dbt FinOps analytics
Objective: add the first local, credential-free dbt analytics slice for Cost and Warehouse while preserving the existing Snowflake procedure and Task Graph contracts.
Branches: `feat/dbt-finops-analytics-tracker` → `feat/dbt-finops-analytics-01-cost` → `feat/dbt-finops-analytics-02-warehouse` | Delivery: `feature-branch-chain` | Offline runner: `python3 -m unittest discover -s tests -p "test_*.py"`

## Specs

- S1 — Continue the saved dbt, functions, and adaptation work requested as: "con las skill que tenemos de dbt , snowflake y relevantes. vamos a continuar con lo planeado sobre dbt y las funciones , y adaptacion".
- S2 — Implement the selected scope "Capa analítica primero (Recommended)": create a dbt Cost/Warehouse analytics layer while leaving the existing procedures and Task Graph behavior unchanged.
- S3 — Preserve the approved Cost contract exactly: raw consumed credits, strict `>25` credits and `>30%` day-over-day growth boundaries, and no invented thresholds for Warehouse.
- S4 — Preserve completeness semantics: delayed or unpublished source windows must remain distinguishable from mature zero usage; do not present query-attributed compute as the full bill.
- S5 — Keep responsibilities separated: dbt transforms and tests descriptive analytics; procedures own approved anomaly rules and durable run persistence; tasks orchestrate the existing operational graph; reports and email consume persisted results.
- S6 — Assess `UDTF_FINOPS_COST_METRICS` and `UDTF_FINOPS_WAREHOUSE_METRICS` against the implemented marts. Add no UDTF when ordinary mart filtering provides the same interface; document the decision, proposed contracts, and the condition that would justify each function.
- S7 — Keep implementation local and credential-free. Do not connect to Snowflake or Cortex, discover ambient credentials, deploy objects, change grants, resume tasks, or send email.
- S8 — Add offline repository checks and dbt model/data-test definitions. Record dbt compilation and live Snowflake validation as pending when no authorized target/session is available.
- S9 — The user requested: "antes de activarla, quiero priemro activar el dbt project y toda la activacion y configuracion de este". Acceptance: provision the native dbt prerequisites, deploy `FINOPS_DEV.FINOPS.FINOPS_DBT_PROJECT`, and validate the selected Cost/Warehouse build before activating the operational Task Graph.
- S10 — The user confirmed the safe baseline: `FINOPS_DBT_WAREHOUSE` is `X-SMALL` with 60-second auto-suspend and auto-resume; `FINOPS_DBT_ROLE` is dedicated to dbt; dbt remains unscheduled and the operational Task Graph remains suspended through validation.

## Tasks

- [x] T1 — S1-S8 — Route: inline (one coherent behavior; no writer trigger) — Add RED repository contracts for the dbt project, ownership boundaries, and unchanged Task Graph — Commits: `7f4b3c6`, `1c8b1a8`.
- [x] T2 — S2-S5,S8 — Route: inline (one coherent behavior; no writer trigger) — Implement sources, staging models, Cost/Warehouse marts, and dbt tests — Commits: `7f4b3c6`, `1c8b1a8`.
- [x] T3 — S5-S8 — Route: inline (one coherent behavior; no writer trigger) — Document native Snowflake deployment prerequisites, operational adaptation boundary, and UDTF decisions — Commits: `7f4b3c6`, `1c8b1a8`.
- [x] T4 — S1-S8 — Route: inline verification; independent verifier required for Risk item 5 — Run offline checks, review exact diff, and record unavailable live proof — Commits: `7f4b3c6`, `1c8b1a8`.
- [x] T5 — S9-S10 — Route: inline — Commit `cdc9f41` — Provisioned the `X-SMALL` warehouse, dedicated role, target-schema authority, Account Usage access, and native dbt project privilege.
- [x] T6 — S9-S10 — Route: inline — Commit `cdc9f41` — Deployed and compiled `FINOPS_DBT_PROJECT` from `dbt/finops_analytics` with dbt 1.9.4.
- [x] T7 — S9-S10 — Route: inline — Commit `cdc9f41` — Built the selected Cost/Warehouse lineage; final result was PASS=24, WARN=0, ERROR=0, SKIP=0.
- [x] T8 — S9-S10 — Route: inline — Commit `cdc9f41` — Verified 365 Cost rows, four Warehouse rows, the suspended dbt warehouse, and ten suspended operational tasks.

## Log

- L1 (2026-11-19) — User request verbatim: "con las skill que tenemos de dbt , snowflake y relevantes. vamos a continuar con lo planeado sobre dbt y las funciones , y adaptacion"
- L2 (2026-11-19) — User selected: "Capa analítica primero (Recommended)".
- L3 (2026-11-19) — Repository evidence: no dbt project exists; current Cost/Warehouse procedures query `SNOWFLAKE.ACCOUNT_USAGE`; current Task Graph is serverless and remains unchanged in this slice.
- L4 (2026-11-19) — Current Snowflake documentation states that tasks executing `EXECUTE DBT PROJECT` must use a user-managed warehouse, so integrating dbt into the current serverless graph is intentionally deferred.
- L5 (2026-11-19) — Test-first plan: add repository contracts and observe RED before adding dbt files; dbt execution remains unavailable without an installed runner and authorized Snowflake target.
- L6 (2026-11-19) — RED observed: `python3 -m unittest discover -s tests -p "test_repository_contract.py"` ran 21 tests and failed 13 assertions because the required dbt project and guide did not yet exist.
- L7 (2026-11-19) — GREEN observed: the focused repository contract ran 21 tests successfully; the full offline suite ran 28 tests successfully; shell syntax, YAML parsing, and `git diff --check` passed.
- L8 (2026-11-19) — `dbt` is not installed locally. dbt parse/build, unit-test execution, SQL compilation, target privileges, and source freshness remain pending rather than inferred.
- L9 (2026-11-19) — Independent verification initially blocked S4/S6. One bounded correction added conservative date-spine completeness, the documented eight-hour query-attribution boundary, regression probes, and concrete proposed UDTF contracts. Targeted recheck passed both blockers.
- L10 (2026-11-19) — Final offline proof: 30 repository tests passed; shell syntax and `git diff --check` passed; YAML loaded successfully with only the environment's pre-existing world-writable `/usr/local/bin` warning.
- L11 (2026-11-19) — The original coherent work reached 575 authored lines. User selected `feature-branch-chain`; delivery was split once into Cost foundation (`7f4b3c6`, 343 lines) and Warehouse extension (`1c8b1a8`, 220 changed lines) while keeping each slice's tests and docs with its behavior.
- L12 (2026-11-19) — The earlier unsplit local candidate was reviewed through native assessment and the user selected "Omitir esta vez". The final delivery candidates are the two bounded chain commits above and retain the same independently verified behavior.
- L13 (2026-11-21) — User request verbatim: "antes de activarla, quiero priemro activar el dbt project y toda la activacion y configuracion de este". The interrupted Task Graph resume left all ten tasks suspended.
- L14 (2026-11-21) — User confirmed an `X-SMALL` `FINOPS_DBT_WAREHOUSE` with 60-second auto-suspend and auto-resume, a dedicated `FINOPS_DBT_ROLE`, selected Cost/Warehouse deployment and tests, no automatic dbt schedule, and no Task Graph activation before validation.
- L15 (2026-11-21) — Provisioning created `FINOPS_DBT_WAREHOUSE`, `FINOPS_DBT_ROLE`, the minimum warehouse/database/schema/dbt-project privileges, and imported `SNOWFLAKE.USAGE_VIEWER`; the configuration is reproduced by `sql/00_setup/04_finops_dbt_bootstrap.sql`.
- L16 (2026-11-21) — The first live build exposed one legitimate Account Usage row with a stable warehouse ID but a null warehouse name. RED reproduced the over-strict contract; the correction preserves the source null, documents it, and removes only the invalid `not_null` test.
- L17 (2026-11-21) — Final live proof: native project deployment and compilation succeeded; the selected build passed all 24 model/data/unit checks; marts contain 365 Cost rows and four Warehouse rows; the `X-SMALL` warehouse auto-suspended; all ten operational tasks remain suspended.
- L18 (2026-11-21) — Live dbt provisioning, credential-free runtime variables, the Account Usage null-name correction, repository regression coverage, and operating evidence were committed as `cdc9f41`. RDD remains disabled for this clone, so delivery is `disabled/unmanaged` under ordinary repository policy.
