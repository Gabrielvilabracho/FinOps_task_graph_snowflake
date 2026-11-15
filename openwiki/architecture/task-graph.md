---
type: architecture
title: Task Graph Architecture
description: The serverless Snowflake DAG that schedules, analyzes, reports, alerts, and finalizes each daily FinOps run.
tags: [snowflake, task-graph, serverless, finops]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-15T23:16:32.229Z
sources:
  - id: openwiki-source-28e7c9a4ebe00633afd95798
    resource: repo://sql/30_tasks/30_finops_task_graph.sql
  - id: openwiki-source-f12e205fe39a459768a95fe4
    resource: repo://sql/30_tasks/31_resume_finops_task_graph.sql
  - id: openwiki-source-c1eb251dec6548141c4b3df1
    resource: repo://sql/30_tasks/32_suspend_finops_task_graph.sql
generated: { by: "opencode", at: "2026-11-15T23:16:32.229Z" }
---

# Task Graph Architecture

The FinOps runtime is a traditional Snowflake Task Graph in `DATALAB.SPAIN`. Tasks provide orchestration while stored procedures own run state and analysis behavior. No task declares a warehouse, so Snowflake-managed serverless compute executes the graph.

## Graph topology

```text
FINOPS_ROOT_TASK (daily 10:00 UTC, no overlap)
├── FINOPS_CHECK_COST ───────────┐
├── FINOPS_CHECK_ERRORS ─────────┤
├── FINOPS_CHECK_WAREHOUSE ──────┤
├── FINOPS_CHECK_QUERIES ────────┼──> FINOPS_REPORT_TASK
├── FINOPS_CHECK_AI ─────────────┤         │
└── FINOPS_CHECK_OTHER_COSTS ────┘         └──> FINOPS_ALERT_TASK

FINOPS_FINALIZER -- FINALIZE = FINOPS_ROOT_TASK
```

The root runs at `10:00 UTC` and uses `OVERLAP_POLICY = NO_OVERLAP`. It derives a stable run-group identifier and the previous UTC date, then opens the persisted run through `SP_FINOPS_BEGIN_RUN`.

Six children depend directly on the root and may execute in parallel. Each reconstructs the same run ID and analysis date from Snowflake task runtime metadata before calling its module procedure. The report waits for all six analyzers; the alert waits for the report.

## Finalizer boundary

`FINOPS_FINALIZER` is associated with the root through `FINALIZE`, not through an ordinary `AFTER` dependency. It calls `SP_FINOPS_FINALIZE_RUN` after the graph settles, including paths where an analyzer failure prevents report or alert tasks from running. This gives persisted run state a reconciliation path outside the success-only chain.

## Activation and suspension

Task creation does not activate the graph. Deployment intentionally leaves it suspended while objects, privileges, configuration, and smoke checks are reviewed.

Activation is explicit and ordered:

1. Resume the finalizer because it is not an ordinary descendant.
2. Call `SYSTEM$TASK_DEPENDENTS_ENABLE` for the fully-qualified root.
3. Inspect `SHOW TASKS` before relying on the schedule.

Suspending the root prevents future scheduled graph runs. Snowflake may allow children from an already-captured graph version to finish, so suspension is a scheduling control rather than cancellation of in-flight work.

## Operational invariants

- All tasks belong to one graph and must share one confirmed owner role.
- The root is the only scheduled task; descendants use dependency edges.
- Every analyzer writes durable module state through its procedure.
- Report generation begins only after all six analyzers succeed on the normal path.
- The finalizer owns reconciliation when the normal report/alert chain is skipped.
- Streams and triggered tasks are not members of the implemented graph; they remain a future design option.

## Related pages

- [State and Cost Policy](../concepts/state-and-cost-policy.md)
- [Daily FinOps Run](../workflows/daily-finops-run.md)
- [Deployment and Access](../operations/deployment-and-access.md)
