---
type: workflow
title: Daily FinOps Run
description: End-to-end flow from scheduled run initialization through parallel analysis, reporting, alert delivery, and final reconciliation.
tags: [workflow, finops, account-usage, alerting]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-15T23:16:32.229Z
sources:
  - id: openwiki-source-9dfab680645da6608e28f0e6
    resource: repo://sql/20_procedures/21_finops_check_cost.sql
  - id: openwiki-source-3f7ae1d59d2eb0f973a460b4
    resource: repo://sql/20_procedures/22_finops_check_errors.sql
  - id: openwiki-source-e1e93a56b39fa5c418451f03
    resource: repo://sql/20_procedures/23_finops_check_warehouse.sql
  - id: openwiki-source-94c56a4a9afae71994341d3d
    resource: repo://sql/20_procedures/24_finops_check_queries.sql
  - id: openwiki-source-8205a01aea78e9fd4633be02
    resource: repo://sql/20_procedures/25_finops_check_ai.sql
  - id: openwiki-source-cb6d1c58e89265154eb21167
    resource: repo://sql/20_procedures/26_finops_check_other_costs.sql
  - id: openwiki-source-3ff7a45601c9a1e843f2a44d
    resource: repo://sql/20_procedures/27_finops_report.sql
  - id: openwiki-source-0e8b051622e79d4642c00831
    resource: repo://sql/20_procedures/28_finops_alert.sql
  - id: openwiki-source-43045712dad8dcb3dc6f8118
    resource: repo://sql/20_procedures/29_finops_finalizer.sql
generated: { by: "opencode", at: "2026-11-15T23:16:32.229Z" }
---

# Daily FinOps Run

One scheduled graph execution analyzes the previous UTC day. Snowflake's graph run-group ID connects task runtime metadata to the durable `FINOPS_RUN`, `FINOPS_MODULE_RUN`, findings, report, and alert-delivery records.

## 1. Initialize the run

At `10:00 UTC`, the root derives the previous UTC analysis date, upserts a `RUNNING` run, and initializes six `PENDING` module rows. The root does not perform analysis itself.

## 2. Run six analyzers in parallel

Every child marks its module `RUNNING`, reads Snowflake Account Usage for the same analysis date, and persists metrics or failure evidence.

| Module | Account Usage source | Measured output | Policy result |
| --- | --- | --- | --- |
| `COST` | `METERING_HISTORY` | Current and previous credits, growth, threshold flags | `NORMAL` or `ATTENTION` using approved rules |
| `ERRORS` | `QUERY_HISTORY` | Failed/incident queries, affected users and warehouses | `RULE_NOT_CONFIGURED` |
| `WAREHOUSE` | `WAREHOUSE_METERING_HISTORY` | Warehouse, compute, estimated idle credits and ratio | `RULE_NOT_CONFIGURED` |
| `QUERIES` | `QUERY_HISTORY`, `QUERY_ATTRIBUTION_HISTORY` | Query activity, attributed credits, maximum query credits | `RULE_NOT_CONFIGURED` |
| `AI` | `CORTEX_AI_FUNCTIONS_USAGE_HISTORY` | Cortex AI credits, queries, functions, and models | `RULE_NOT_CONFIGURED` |
| `OTHER_COSTS` | `METERING_HISTORY` | Non-warehouse/non-AI metering and serverless-task credits | `RULE_NOT_CONFIGURED` |

The cost analyzer loads the configured `25` credit and `30%` growth rules, invokes the pure policy function, replaces prior cost findings for the same run, and records warning findings only for matched rules.

The other five analyzers measure evidence but do not issue anomaly verdicts. They call the shared rule-gap procedure with a concrete decision the team still needs to approve. This preserves visibility without converting arbitrary values into policy.

Each analyzer catches technical exceptions, marks its module `FAILED`, records a critical finding, and re-raises so the Snowflake task also fails.

## 3. Build the report

On the normal path, `FINOPS_REPORT_TASK` runs after all six analyzers. `SP_FINOPS_BUILD_REPORT` aggregates module states and metrics, then chooses:

- `ATTENTION_REQUIRED` if any module is `ATTENTION` or `FAILED`;
- `REVIEW_REQUIRED` if no attention/failure exists but any rule is unconfigured;
- `NORMAL` otherwise.

The procedure merges one report per run and updates run-level counts and status, making report generation safe to repeat during finalization.

## 4. Decide alert delivery

Alert delivery is idempotent by run and email channel:

- A previously delivered email returns `ALREADY_DELIVERED`.
- A report not requiring attention records `NOT_REQUIRED`.
- Disabled or incomplete notification configuration records `NOT_CONFIGURED`.
- An attention-required report with approved configuration calls `SYSTEM$SEND_EMAIL` and records `DELIVERED`.
- A notification exception records `FAILED` with a bounded error message.

Email is therefore a persisted outcome, not an assumption. `REVIEW_REQUIRED` does not send an attention alert under the current policy.

## 5. Reconcile in the finalizer

If an analyzer fails, the success-only report and alert tasks may be skipped. The finalizer still runs after the graph settles. It converts unfinished modules into failed modules, records missing-completion findings, rebuilds the report, retries the alert decision idempotently, and marks finalizer completion.

This produces a reportable terminal run even when the normal chain cannot reach its reporting stage. A failure inside the finalizer itself marks the run `FAILED` and leaves `FINALIZER_COMPLETED = FALSE` for operators.

## Data freshness considerations

Account Usage views may lag. The query module records an explicit attribution-latency note, and operations should rerun after documented source latency rather than weaken thresholds or treat delayed data as zero-cost truth.

## Related pages

- [Task Graph Architecture](../architecture/task-graph.md)
- [State and Cost Policy](../concepts/state-and-cost-policy.md)
- [Deployment and Access](../operations/deployment-and-access.md)
