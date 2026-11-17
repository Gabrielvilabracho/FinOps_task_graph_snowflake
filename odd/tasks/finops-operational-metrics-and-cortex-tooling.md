# FinOps Operational Metrics and Cortex Tooling

Objective: make the first operational-analytics slice implementation-ready and prepare credential-free Cortex Code tooling without connecting to Snowflake.
Branch: `feat/finops-operational-metrics` · Delivery: `ask-on-risk` with `feature-branch-chain` · Runner: Python repository contracts, shell syntax checks, and Snowflake SQL checks only when a session is explicitly authorized.
Forecast: more than 400 authored lines across SQL contracts, procedures, tests, operational documentation, and project-local tooling.

## Specs

- S1 — Implement the user's request “implementalos” according to the selected scope “Ambos”. Acceptance: both the corrected Slice 1 implementation and credential-free Cortex tooling preparation are delivered; no live Snowflake connection is used.
- S2 — Apply the selected project scope: “Corregir el documento e implementar Slice 1 en este repositorio usando sf-samples y la documentación oficial como referencias, sin instalar herramientas externas.” Acceptance: the expansion plan becomes unambiguous; the implementation uses source-backed patterns without copying sample assumptions as production contracts.
- S3 — Apply the selected tooling scope: “Implementar Slice 1 en el proyecto y además preparar las herramientas de Cortex Code, manteniendo la conexión Snowflake desactivada.” Acceptance: project-local, pinned preparation artifacts are provided without authentication, credential discovery, Snowflake execution, or global host configuration changes.
- S4 — Define one durable `FINOPS_METRIC` contract. Acceptance: stable metric identity, idempotent merge semantics, typed values, source windows, freshness, completeness evidence, and zero-versus-missing rules are explicit and tested.
- S5 — Add `DATA_INCOMPLETE` without allowing incomplete data to become healthy. Acceptance: metric-to-module-to-run precedence is deterministic; report, finalizer, and alert behavior cover incomplete data; source query or privilege failures remain `FAILED`.
- S6 — Preserve the approved Cost policy. Acceptance: classification continues to use raw `CREDITS_USED`; strict `> 25` credits and `> 30%` growth behavior remains unchanged; billed or adjusted credits are informational only.
- S7 — Preserve the existing Task Graph and operational invariants. Acceptance: topology remains unchanged; repeated writes for one `RUN_ID` are idempotent; finalizer reconciliation and alert deduplication continue to work.
- S8 — Keep unsupported live behavior explicit. Acceptance: Snowflake compilation, privileges, Account Usage freshness, graph execution, email delivery, and Cortex authentication are reported as unavailable until the user explicitly authorizes a session.

## Tasks

- T1 · S1,S2,S4-S8 · delegated (parallel independent Slice 1 unit) · complete · commits `da104ed`, `a4e2dd5`, and `84f3492` · RED: 9 contract failures, one targeted invariant failure, and one partial-publication failure; GREEN: focused regressions and the full local suite pass.
- T2 · S1,S3,S8 · delegated (parallel independent tooling unit) · complete · commit `6bd6e2e` · lock, shell syntax, ShellCheck, and offline `--check` pass without activation or credentials.
- T3 · S1-S8 · inline parent seam and high-risk verification · in progress · local suite passes; final independent verification and PR-chain delivery remain pending; live Snowflake proof remains unavailable.

## Log

- L1 · 2026-11-17 · User request (verbatim): “implementalos”.
- L2 · 2026-11-17 · Scope clarification selected by the user (verbatim): “Ambos”.
- L3 · 2026-11-17 · The accepted “Ambos” choice means implementing Slice 1 and preparing Cortex Code tooling while keeping the Snowflake connection disabled.
- L4 · 2026-11-17 · Read-only validation found that the previous plan was not implementation-ready because storage identity, completeness semantics, status precedence, and incomplete-data alert behavior were undefined.
- L5 · 2026-11-17 · Parallel writer trigger applies: T1 and T2 are independent units with disjoint edit surfaces and each includes its behavior, tests, and documentation.
- L6 · 2026-11-17 · Risk: items 1, 2, 3, 4, 5, and 6 — durable schema, managed-access grants, financial classification compatibility, retry ordering, notification behavior, and unavailable live-environment proof.
- L7 · 2026-11-17 · T1 implemented the durable metric contract, shared status precedence, completeness-aware Cost and Warehouse collection, report/alert/finalizer folding, grants, validation, tests, and operational documentation without changing Task Graph topology.
- L8 · 2026-11-17 · T2 pinned Snowflake AI Kit and coco-skills public revisions and added project-local offline preparation. No Cortex or Snowflake connection was configured or invoked.
- L9 · 2026-11-17 · Independent verification found one candidate-caused completeness invariant defect and one documentation contradiction. A single bounded correction normalized incomplete metric status at the shared persistence boundary and corrected alert documentation; the targeted recheck passed.
- L10 · 2026-11-17 · Parent seam checks pass: 22 Python tests, deployment/tooling shell syntax, lock JSON validation, offline tooling check, and `git diff --check`.
- L11 · 2026-11-17 · User selected `feature-branch-chain` for this feature because the implementation exceeds the review-size forecast.
- L12 · 2026-11-18 · Native review corroborated that partial source rows could incorrectly satisfy completeness before the source watermark reached the requested window end. Commit `a4e2dd5` now requires both expected-complete time and `SOURCE_WATERMARK >= V_WINDOW_END` for Cost and Warehouse.
- L13 · 2026-11-18 · Independent whole-feature verification found that the credential-free Cortex artifacts were not yet committed and that one Warehouse status sentence contradicted the implementation. Commits `84f3492` and `6bd6e2e` close those gaps; final verification remains pending.
