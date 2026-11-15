---
type: concept
title: State and Cost Policy
description: Durable FinOps run state, module outcomes, approved cost thresholds, and the separation of anomalies, failures, and rule gaps.
tags: [finops, state-model, cost-policy, persistence]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-15T23:16:32.229Z
sources:
  - id: openwiki-source-dca64cdef932c78b6964b073
    resource: repo://sql/00_setup/01_finops_objects.sql
  - id: openwiki-source-656899cf62cb6ce46893ebdd
    resource: repo://sql/10_core/10_finops_cost_policy.sql
  - id: openwiki-source-47aa4a9c88bf62cb036c5042
    resource: repo://sql/20_procedures/20_finops_run_lifecycle.sql
  - id: openwiki-source-43045712dad8dcb3dc6f8118
    resource: repo://sql/20_procedures/29_finops_finalizer.sql
generated: { by: "opencode", at: "2026-11-15T23:16:32.229Z" }
---

# State and Cost Policy

The graph persists operational evidence before it reports conclusions. Run, module, finding, report, and delivery records make a scheduled execution inspectable even when part of the task graph fails.

## Persistent model

| Object | Responsibility |
| --- | --- |
| `FINOPS_CONFIG` | Stores approved rules and notification configuration. |
| `FINOPS_RUN` | Stores one durable record per task-graph run group, including aggregate counts and finalizer completion. |
| `FINOPS_MODULE_RUN` | Stores each analyzer's lifecycle, metrics, finding count, and technical error details. |
| `FINOPS_FINDING` | Stores approved rule matches, technical failures, and explicit rule gaps. |
| `FINOPS_DAILY_REPORT` | Stores an idempotent summary and rendered report text for a run. |
| `FINOPS_ALERT_DELIVERY` | Stores notification attempts and outcomes without storing credentials. |

`SP_FINOPS_BEGIN_RUN` upserts the run as `RUNNING` and creates six `PENDING` module rows: `COST`, `ERRORS`, `WAREHOUSE`, `QUERIES`, `AI`, and `OTHER_COSTS`. Module procedures then move their own rows through `RUNNING` to a terminal result.

## State semantics

Module outcomes are deliberately distinct:

- `NORMAL`: an approved rule was evaluated and did not match.
- `ATTENTION`: an approved business rule matched.
- `RULE_NOT_CONFIGURED`: evidence was measured, but no approved anomaly rule exists.
- `FAILED`: technical execution failed or the module never reached a terminal state.

Run-level state summarizes those outcomes:

- `NORMAL`: every required evaluation completed without attention or rule gaps.
- `REVIEW_REQUIRED`: execution completed, but at least one module has no approved rule.
- `ATTENTION_REQUIRED`: a business anomaly or technical failure requires action.
- `FAILED`: run finalization itself failed.

This separation prevents missing policy from being reported as healthy and prevents a platform failure from masquerading as a business anomaly.

## Approved cost policy

Only the cost module has approved alert thresholds:

1. `ATTENTION` when daily credits are strictly greater than `25`.
2. `ATTENTION` when a positive prior-day baseline exists and day-over-day growth is strictly greater than `30%`.
3. Otherwise `NORMAL`.

The pure `FINOPS_CLASSIFY_COST` function returns both the classification and its inputs, computed growth ratio, and per-rule booleans. Exact threshold equality is normal because both comparisons are strict. Missing or non-positive prior credits disable the growth comparison rather than fabricating a baseline.

The remaining modules record measured metrics and a `RULE_NOT_CONFIGURED` finding. Their required business decisions remain explicit; the implementation does not invent limits for failed queries, warehouse idle credits, expensive queries, AI usage, or other service costs.

## Failure reconciliation

Every module marks itself `RUNNING` before analysis. A caught technical exception records a critical `TECHNICAL_FAILURE`, marks the module `FAILED`, and is re-raised so Snowflake also records task failure.

During finalization, any module still `PENDING` or `RUNNING` receives a technical-failure finding and becomes `FAILED`. The finalizer then rebuilds the report, attempts alert delivery, and marks `FINALIZER_COMPLETED`. If finalization itself raises, the run becomes `FAILED` and the completion flag remains false.

## Related pages

- [Task Graph Architecture](../architecture/task-graph.md)
- [Daily FinOps Run](../workflows/daily-finops-run.md)
- [Testing and Verification](../testing/verification.md)
