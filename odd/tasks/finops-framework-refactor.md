# FinOps Framework Refactor — Session Handoff
Objective: implement a local, tested adaptation of the existing project to the researched Framework and verified Snowflake source contracts.
Baseline: `b73f504d9fbc9409dcd10a4aed4d759a50edd6fb` on the original `feat/finops-dev-deployment` branch. Delivery: user-authorized single PR with size exception from `feat/finops-evidence-research`, linked to approved issue #14; no Snowflake deployment. Runner: `python3 -m unittest discover -s tests -p "test_*.py"`.

## Specs

### S1 — Adapt the existing project using the available evidence

User request, verbatim:

> aunqune no exista historico suficioente tenemos suficiente conocimientos de las fuentes y el estudio del freamwork para poder refactorizar este proyecto y adaptarlo adecuadamente a encontrar los resultados que buscamso

Accepted interpretation: the Framework study, documented source contracts, and read-only account observations are sufficient to begin a foundational local refactor. Limited mature history constrains statistical and financial claims, not all engineering. Preserve useful existing components; do not mechanically create one module per Framework capability.

Proposed acceptance criteria, to refine during T1:

- Separate source consumption, billed/effective financial views, attribution, business policy, and actions; overlapping representations must not be summed as separate expenses.
- Model source coverage, units, publication expectations, empty/null/unknown/provisional states and history boundaries explicitly.
- Support technical attribution and future ownership enrichment without inventing owners, historical mappings, shared-cost policies, or chargeback rules.
- Cover observed AI/service entry points deliberately; one Cortex AI Functions source must not be presented as all AI expense.
- Use deterministic fixtures for unavailable historical and edge cases; preserve the behavior of existing interfaces unless a breaking change is deliberately selected and authorized.
- Do not claim validated forecasting, realized savings, complete Product TCA, invoice reconciliation or safe automatic remediation from the limited observed history.

### S2 — Prepare now; implement next session, locally only

User instruction, verbatim:

> si dejalo preparado y continuamos en la siguiente session con la refactirizacion

The original deferral applied to the preparation session. The following explicit instruction resumes T1–T6 locally:

> aplicalo , el plan de refactorizaccion

Local code, tests and documentation are now authorized; deployment and Snowflake modifications remain excluded.

### S3 — Run the daily analysis at noon UTC

> a entendi, pues aplica para que sea a las 12

Change the local root schedule to 12:00 UTC once per day; preserve the previous complete UTC day as the analysis window. Do not deploy or change live tasks. The separate 48h financial margin is unchanged.

Authorization boundaries:

- Next-session work is local code, tests and documentation. No deployment, migration of existing stored data, grants, task activation/suspension, scheduling changes, or notification/remediation actions are authorized.
- Previous account validation used connection `finops`; `ACCOUNTADMIN` was explicitly authorized only for read-only probes. It is not a deployment or runtime role selection.
- Keep SQL text, prompts/responses, user identifiers, credentials and business data out of evidence extraction. Do not reuse remote access outside its authorized scope.
- No commit, push, PR, branch change or Snowflake operation was part of the original handoff preparation. Later Git publication is separately authorized in L13; Snowflake operations remain excluded.

## Tasks

- [x] **T0 — Prepare recovery** | S1–S2 | Route: inline, passive documentation only | Status: completed | Commit: `bf0470e`; document readback and structural checks recorded below.
- [x] **T1 — Reconcile the local baseline and choose the first bounded change** | S1–S2 | Route: delegated read-only mapping after the inline evidence budget; implementation stays inline | Status: completed | Commit: `bf0470e`; baseline 42 tests passed.
- [x] **T2 — Separate consumption and financial evidence contracts** | S1–S2 | Route: inline | Status: completed locally | Commit: `bf0470e`; RED/GREEN SQL-helper and mart fixtures, independent baseline guards, optional billed representation; native compilation pending.
- [x] **T3 — Make attribution, ownership and residual boundaries explicit** | S1–S2 | Route: inline | Status: completed locally | Commit: `bf0470e`; RED missing residual helper/fields; GREEN signed/partial/null/legacy-alias fixtures and suite. Ownership unknown; no waste verdict.
- [x] **T4 — Expand service-aware AI evidence without double counting** | S1–S2 | Route: inline | Status: completed locally | Commit: `bf0470e`; RED empty-as-zero/coverage contract; GREEN actual Functions aggregation fixtures (empty, zero, null, running, multi-day). Optional User-AI service subset and explicit uncollected coverage; no AI grand total.
- [x] **T5 — Adapt reporting and workflow boundaries to evidence readiness** | S1–S3 | Route: inline | Status: completed locally | Commit: `bf0470e`; daily root schedule changed to 12:00 UTC with authored docs aligned; existing evidence-aware reporting preserved; no live deployment.
- [x] **T6 — Verify the local refactor and document remaining operational gates** | S1–S3 | Route: inline tests plus independent verifiers for Risk items 3 and 5 | Status: completed locally | Commit: `bf0470e`; 64 tests passed; schedule-only delta and prior-day UTC window independently verified; native integration remains a separate gate.

## Log

### L1 — Original refactor discussion

> aunqune no exista historico suficioente tenemos suficiente conocimientos de las fuentes y el estudio del freamwork para poder refactorizar este proyecto y adaptarlo adecuadamente a encontrar los resultados que buscamso

### L2 — User deferral, November 22, 2026

> si dejalo preparado y continuamos en la siguiente session con la refactirizacion

Implementation is explicitly paused. Resume at T1 next session; do not interpret preparation as permission to implement in this session.

### L3 — Readiness correction

The earlier blanket requirement to close all ten financial/operational evidence gates before any schema/dbt design was overconservative. Foundational local engineering can proceed with validated source contracts and realistic fixtures. Business policy, invoice reconciliation, statistical confidence, historical ownership and deployment/remediation authority remain separate, capability-specific gates. The research document was corrected accordingly.

### L4 — Evidence and source locators

- `docs/finops-framework-research.md`: 22-capability contrast, 157-source ledger, source semantics, control limits, and evidence gates. Three sources remain partial: dynamic capability index, dynamic KPI library, broad Organization Usage index. Not a production specification.
- `docs/architecture.md`: existing task/procedure/core-policy/report separation and descriptive dbt boundary. Deployment-state statements may be stale; do not overwrite source contracts merely to align documentation.
- `sql/20_procedures/21_finops_check_cost.sql`: raw hourly `METERING_HISTORY` credits, fixed three-hour completeness expectation, shared policy and metric helpers. Inspect service-specific maturity, previous-period validity and compatibility before changing it.
- `sql/20_procedures/25_finops_check_ai.sql`: explicitly scoped to `CORTEX_AI_FUNCTIONS_USAGE_HISTORY`; empty sum becomes zero. Preserve the honest scope and distinguish complete zero from missing/unpublished data in the proposed replacement.
- Reuse existing `SP_FINOPS_RECORD_METRIC`, `SP_FINOPS_MARK_MODULE_START`, `SP_FINOPS_COMPLETE_MODULE_FROM_METRICS`, failure/finalizer and pure-policy functions where their contracts fit. Do not reimplement shared state transitions independently.
- `dbt/finops_analytics` and `tests/`: inspect during T1; current design separates descriptive analytics from operational classification and delivery.
- Engram observation `8158`, topic `validation/finops-readiness-live-access`: full scrubbed validation findings. Observation `8169`: distinction between refactor readiness and financial validation.

### L5 — Live validation snapshot; historical evidence only

Observed November 22, 2026 under authorized read-only `ACCOUNTADMIN` override:

| Area | Observation | Consequence |
|---|---|---|
| Access | Enterprise account in `AWS_EU_WEST_3`; selected AU, OU finance and FOCUS sources readable. Default `finops` remains `FINOPS_REPO_OPERATOR`, no secondary roles. | Administrative source access is not proof of least-privilege runtime readiness. |
| History | Observed usage begins November 20; no populated complete day met the chosen 48-hour reconciliation margin. | Use provisional evidence and fixtures; do not wait for history to begin local foundational work. |
| Metering, Nov 20–21 UTC | Hourly/daily used: 6.174710370 credits; adjustment: -0.020631115; billed: 6.154079255. | Keep raw and billed semantics separate. |
| Currency/FOCUS | Both returned USD 24, all `Free Usage`; FOCUS consumed quantity differed from AU billed by 0.001369422 credits for identified provisional service/day populations. | Not payable-invoice proof or a proven permanent omission; preserve rounding/population bridges. |
| Attribution | Warehouse compute: 3.47325 credits; warehouse query-attributed aggregate: 0.153256101; residual: 3.319993899. QAS: 213/213 null. | Residual is not automatically waste; null QAS is not verified zero. |
| Metadata | 24,378 statements in previous 30 complete UTC days; 46 tagged (~0.1887%); 0/213 attributed queries tagged; direct tag-reference count zero. | Do not fabricate ownership or equate tag frequency with cost-weighted business allocation. |
| AI | Selected Functions/AISQL/Analyst/Agents/CoWork/Search views readable but empty; user AI 0.000860475 credits, Containers 2.659738935, each matching its daily-metering representation. | Empty source does not mean unavailable feature; aggregate/detail are not additive expenses. |
| Controls | Four XS warehouses; all auto-resume; two 60s/two 300s auto-suspend; zero returned resource monitors/assignments. Ten scoped tasks already `started`. | No control or task change was made. Never assume the graph is suspended. |
| Gaps | Budget/quota discovery timed out at 75 seconds; server completion unknown. Contracts, invoices, external costs/outcomes and policies not supplied. | Not evidence of absence; preserve as pending operational/financial proof. |

Do not replay live queries merely to reconstruct context. Revalidate time-sensitive facts only when needed and within explicit authorization. Historical figures above are not current claims.

### L6 — Next-session execution and verification discipline

1. Recover this task document and its full Engram mirror at `odd/finops-framework-refactor/tasks`; reconcile with observation `8158`, actual source and `git status`.
2. Preserve unrelated untracked `.agents/`, `.atl/`, HTML/workflow artifacts and `skills-lock.json`. The research Markdown was already untracked before this preparation; do not lose it.
3. Begin T1: inspect existing SQL/dbt/tests, identify exact compatibility boundaries and authorized edit surfaces, then choose a bounded first behavior. Do not start with a wholesale rewrite, new production tables or live migration.
4. Before each behavior change, observe a relevant deterministic RED, implement GREEN, then refactor. Add one preservation case for each existing behavior sharing changed helpers/parsers/contracts. Where meaningful RED is unavailable, record the exception rather than inventing proof.
5. Runner: `python3 -m unittest discover -s tests -p "test_*.py"`. The last live-validation session inherited a 42-test passing local baseline; rerun it before source changes. SQL integration tests are not authorized by this local-only scope.
6. Record source-mutating normalizers before verification. Run focused tests and the applicable suite; use outside-workspace scratch for differential probes where meaningful. No fixed Git history reads in committed regression tests.
7. Assess actual risk: persisted format/data changes, shared public contracts, permissions, concurrency and deployment are high-risk items, not incidental cleanup. Avoid these unless required and explicitly scoped; name any applicable item and use its independent verification gate.
8. RDD was clone-locally off when last checked. Read status when needed; never enable it automatically. Do not commit/publish as part of preparation. Future commit decisions follow the active instructions and explicit authorization.

Routing and delivery forecast: implementation units are sequential/dependent, so no parallel writer reason is currently established. Authored size is not yet measured; provisional forecast is 800–1,600 changed lines including tests/docs, excluding generated files. This is a planning estimate, not a target. Use coherent work units; resolve `ask-on-risk` delivery strategy before any applicable commit boundary, not by splitting behavior from tests/docs or minimizing code for a line count.

### L7 — Preparation checks and stopping point

Preparation-only exception: no behavior was changed, so RED/GREEN and Snowflake integration execution do not apply. Check document paths, headings, task/spec links, source ledger counts, local anchors, fences and whitespace; read back the local document and full Engram mirror.

Observed checks: `Specs`/`Tasks`/`Log` ordering, seven task IDs, exact user deferral, cited local paths and handoff link, balanced fences, whitespace and conflict checks passed. Research inventory remains 157 unique sources (152 Full, 3 Partial, 1 Redirect, 1 observed 404). `git diff --check` passed; custom structural checks also covered both untracked Markdown files. Behavioral tests were not rerun because only passive documentation changed.

Current stopping point: **T0 complete; T1–T6 pending by the user's explicit instruction.** No implementation, branch change, commit, deployment or remote operation is part of this preparation.

### L8 — Implementation resumed, November 22, 2026

> aplicalo , el plan de refactorizaccion

Reconciled the full Engram mirror with this document and the working tree. The baseline has 42 passing local tests; RDD is clone-locally disabled and will stay disabled. Unrelated untracked files remain untouched. CodeGraph has no index; read-only mapping used native file inspection. No source changes existed before this session.

Implementation route: inline, sequential T2–T5; no independent parallel writer units exist. Reuse lifecycle/metric/status helpers and existing deployed file paths; no new production tables, task nodes, grants, installer changes, or live operations. Preserve raw COST keys/policy, Functions-specific AI keys, legacy warehouse aliases and report shape; add explicit evidence metadata. Named risk: item 3, shared report/metric consumer contracts; independent verification at T6. No meaningful local Snowflake Scripting execution is available: use executable shipped SQL-expression fixtures plus structural integration checks, and explicitly leave native compilation/integration pending.

Provisional forecast remains 800–1,600 authored lines; no PR or commit boundary is requested, so chain strategy is not needed for working-tree implementation. Source-mutating normalizers: none planned. First bounded change: conservative publication/history/null guards and separately labelled daily billed evidence without replacing or adding to hourly consumption.

### L9 — T2 evidence

Observed RED for missing publication helpers, absent independent baseline/financial metadata and mart false-zero/null-component behavior. GREEN: executable shipped helper/mart fixtures and existing contracts pass. COST preserves the existing classification function, adds a conservative 12h account-wide raw window, independent previous-day evidence, optional daily billed credits and explicit UTC-session validation. The daily mart uses observed-row/history guards and a local 48h provisional margin; conditional tests permit unknown financial values. See `docs/operations/finops-evidence-contract.md`. Local suite after dependent additions: 58 tests passed; Snowflake/dbt execution remains unperformed by scope.

### L10 — Local implementation closure and remaining gates

T1–T6 are complete for the authorized local scope. The independent verifier found no change-caused blockers and returned S1/S2 met. Baseline: 42 tests passed; initial candidate: 58; independent scratch candidate with additional probes: 66. Parent reproduced the scratch 66-test result, adopted nonredundant probes into the two new test files, then observed the final repository suite: **63 tests passed**. `git diff --check` passed. No source-mutating formatter ran.

Differential evidence: 576 identical outputs for the existing cost-policy overloads (including fractional/strict boundaries); 90 unchanged report lines for modules without new evidence; mature daily financial values and warehouse legacy aliases preserved. Fifteen unaffected SQL files and all baseline scripts were byte-identical, including lifecycle/status, alerts, finalizer, tasks/setup and deployment. All seven metric calls matched the 23-argument shared API. New tests read shipped expressions, not Git history. Independent scratch was outside the workspace and removed by the parent after the spot check.

No production correction round was needed. Advisory reproduced on both baseline and candidate: a warehouse cloud-services-only null can coexist with source completeness when raw/compute values are known; not fixed as unrelated baseline behavior. Native Snowflake compilation, NUMBER precision, Scripting exception execution, dbt parsing/execution, privileges and live freshness were not verified. Those are deployment gates, not claimed local proof. Context7 quota was unavailable; official public source pages supplied refreshed latency/schema evidence without an account connection.

Important next operational decision: the unchanged 10:00 UTC previous-day cadence is earlier than the 12h raw and 48h financial readiness windows; explicitly decide reconciliation cadence before deployment. No task state, schedule, grant, notification, remote object or existing stored data was changed. No branch change, commit, push or PR was made. Unrelated untracked files were preserved. Risk: item 3 (shared metric/report consumer contracts), independently checked. RDD remained clone-locally disabled.

### L11 — Daily noon schedule requested, November 22, 2026

> a entendi, pues aplica para que sea a las 12

The user selects 12:00 UTC daily after clarification that the window is the previous complete UTC day, not a 12-hour frequency. Reopen T5/T6 only. Local schedule definition and corresponding authored docs/tests are authorized; no live task operation or deployment. The 48h financial margin remains unchanged and can still yield provisional daily billed evidence. Risk: item 5 (local task schedule definition); independent verification after focused checks. No formatter or generated OpenWiki edit is planned.

### L12 — S3 verification and closure

Observed RED: updated cron expectation failed against the 10:00 definition. GREEN: focused repository checks 19 passed; complete suite 64 passed; `git diff --check` passed. The graph diff against the baseline is exactly `0 10` to `0 12`; independent verification confirmed the seven scheduled-UTC-minus-one expressions, full-day boundaries, serverless/no-overlap/dependencies unchanged, including date-boundary probes. Parent reproduced the independent scratch 64-test result. Scratch cleanup is parent-owned. Authored schedule docs now state 12:00 UTC daily and retain the separate 48h provisional financial margin. No remote deployment or live schedule validation, commit, branch change, or RDD toggle occurred. S1–S3 complete locally; native verification and financial reconciliation remain separate gates.

### L13 — Git publication authorized, November 22, 2026

> realiza  commit , push PR y merge

The user selected `Una PR con excepción` and supplied approved GitHub issue #14 after correcting #40. Publish the existing refactor and research as one PR with cohesive commits; exclude `.agents/`, `.atl/`, generated HTML/workflow artifacts and `skills-lock.json`. The previous deployment PR #13 is already merged, so the new delivery branch is `feat/finops-evidence-research` from current `origin/main`. The pre-publication suite passed 64 tests and `git diff --check`; native SQL/dbt verification, financial reconciliation, graph recovery and live deployment remain explicitly pending. RDD is clone-locally disabled and was not changed. Risk: items 3 and 5, covered by the previously recorded independent checks; Git publication does not authorize Snowflake execution.

Implementation delivery commit: `bf0470e` (`feat(finops): preserve evidence readiness and credit boundaries`). Its 20-file unit keeps runtime behavior, deterministic tests, operational documentation and the supporting FinOps Framework research together. The subsequent documentation unit adds the separately audited Tokenomics material and its navigation links without changing runtime bytes.
