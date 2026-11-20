# FINOPS_DEV Deployment

Objective: adapt the repository for a first clean deployment into `FINOPS_DEV.FINOPS`, keep every task suspended, and validate the installation without migrating data.
Branch: `feat/finops-dev-deployment` · Delivery: `feature-branch-chain` · Runner: Python repository contracts, shell syntax checks, and authorized Snowflake validation.
Forecast: initially under 400 authored changed lines; the completed atomic deployment slice is 629 lines because target migration, role bootstrap, deployment, validation, tests, and operator documentation must remain reviewable together.

## Specs

- S1 — Deploy to `FINOPS_DEV.FINOPS` instead of the historical target. Acceptance: editable deployment artifacts, tests, dbt defaults, and operating documentation consistently use or default to the selected target.
- S2 — The user clarified: “pero si no se corrido ninguna ves ninguna de esas es puro codigoq ue eoms creado nosotros”. Acceptance: treat this as a clean installation; do not design or execute a historical data migration.
- S3 — Preserve the existing safety boundary that tasks remain suspended. Acceptance: deployment never executes `sql/30_tasks/31_resume_finops_task_graph.sql`, and validation proves all ten graph tasks are suspended.
- S4 — Keep repository synchronization separate from object deployment. Acceptance: documentation and grants distinguish `FINOPS_REPO_OPERATOR` from the deployment role and the single task-owner role.
- S5 — Use minimum Snowflake privileges and avoid `ACCOUNTADMIN` for normal operation. Acceptance: owner/deployer grants are explicit, scoped to `FINOPS_DEV.FINOPS`, and live mutation waits for an authorized capable role.
- S6 — Preserve unrelated untracked files. Acceptance: `.agents/`, `.atl/`, generated HTML/workflow files, and `skills-lock.json` are neither modified nor committed by this feature.

## Tasks

- T1 · S1-S6 · delegated exploration · complete · Source, test, dbt, documentation, privilege, and suspension boundaries mapped with path-level evidence.
- T2 · S1-S4,S6 · inline · complete · Target contracts drove the SQL, deploy helper, dbt defaults, grants, tests, and documentation to `FINOPS_DEV.FINOPS`.
- T3 · S1-S4,S6 · inline · complete · RED observed 17 failures and one error; GREEN passed 39 tests, shell syntax, diff validation, parent spot check, and independent high-risk verification.
- T4 · S4-S5 · inline · complete · `FINOPS_TASK_OWNER` was created with scoped schema/warehouse privileges, both required Account Usage database roles, and account-level serverless task execution privileges.
- T5 · S1-S5 · inline · complete · The idempotent single-session deployment succeeded in `FINOPS_DEV.FINOPS`; fail-closed validation proved ten suspended tasks, one owner, no unexpected tasks, disabled alerts, and empty run history. Final targeted recheck: PASS.

## Log

- L1 · 2026-11-20 · User selected deployment target `FINOPS_DEV.FINOPS` instead of `DATALAB.SPAIN`.
- L2 · 2026-11-20 · Read-only mapping found 96 historical target references and confirmed that `scripts/deploy.sh` excludes grants and task resume.
- L3 · 2026-11-20 · User clarification (verbatim): “pero si no se corrido ninguna ves ninguna de esas es puro codigoq ue eoms creado nosotros , por eso me confundo”. The deployment is therefore a clean installation with no historical data migration.
- L4 · 2026-11-20 · Pre-existing untracked files were recorded before implementation and are outside this feature's edit surface.
- L5 · 2026-11-20 · Next step: observe failing repository contracts for the new target before changing implementation artifacts.
- L6 · 2026-11-20 · RED evidence: focused target tests failed with 17 failures and one error against the historical target and missing suspension assertions.
- L7 · 2026-11-20 · GREEN evidence: 33 repository tests and `bash -n scripts/deploy.sh` pass. The deployment order is unchanged, every call pins `FINOPS_DEV.FINOPS` with secondary roles disabled, and resume remains manual.
- L8 · 2026-11-20 · Independent high-risk verification initially found stale-task validation and role-grant gaps. One correction added unexpected-task detection, explicit combined owner/deployer grants, and regression coverage; targeted recheck returned PASS.
- L9 · 2026-11-20 · Next step: inspect the authorized Snowflake target and current role read-only, then resolve any missing owner privileges before deployment.
- L10 · 2026-11-20 · Authorized read-only Snowflake inspection confirmed `FINOPS_DEV.FINOPS` does not yet exist. The active `FINOPS_REPO_OPERATOR` role has only database/repository/integration/warehouse access, secondary roles are disabled, and `ACCOUNTADMIN` is not active. A scoped administrative setup is required before deployment.
- L11 · 2026-11-20 · User explicitly authorized a one-time `ACCOUNTADMIN` bootstrap through the existing `finops` OAuth session. `FINOPS_DEV.FINOPS` and `FINOPS_TASK_OWNER` were created; the role was granted to `gvilabracho` with scoped create, warehouse, Account Usage, and serverless task privileges.
- L12 · 2026-11-20 · Live deployment exposed and fixed three compilation/transport defects: redundant `ALTER ... ADD COLUMN IF NOT EXISTS` statements failed on defaulted columns, VARIANT functions were invalid inside the `VALUES` clause, and task scripting blocks needed `EXECUTE IMMEDIATE $$` delimiters.
- L13 · 2026-11-20 · The deployment helper now submits all ordered files in one OAuth session. An end-to-end rerun succeeded and remained idempotent.
- L14 · 2026-11-20 · Final Snowflake validation: ten tasks exist, all ten are suspended, all share owner `FINOPS_TASK_OWNER`, no unexpected FinOps tasks exist, native alerting remains disabled, and run tables remain empty. `31_resume_finops_task_graph.sql` was not executed.
- L15 · 2026-11-21 · Final correction replaced display-only task counts with Snowflake Scripting custom exceptions for missing expected tasks, active expected tasks, and unexpected `FINOPS_` tasks. The live valid deployment returned `10/10/0` and completed successfully.
- L16 · 2026-11-21 · Closure evidence: 39 Python tests, shell syntax, and `git diff --check` passed. The independent targeted blocker recheck confirmed fail-closed validation and bootstrap-before-deploy ordering with no remaining blocker. Activation remains intentionally pending.
- L17 · 2026-11-21 · The user selected `feature-branch-chain` after the completed diff reached 629 authored changed lines. The implementation remains one cohesive first slice because separating target, owner, deployment, validation, tests, or operating instructions would leave an unsafe intermediate deployment contract; a small closure commit will record final commit and review evidence.
