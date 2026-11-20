# Architecture — Snowflake Native FinOps

## Executive summary

The implementation keeps orchestration, cost evidence, analysis rules, reports, and alert state in Snowflake. Tasks orchestrate; procedures own business logic; tables preserve operational evidence; a finalizer reconciles every graph run even when a child fails. A separate dbt project provides descriptive Cost and Warehouse marts without changing that operational ownership.

## Operational model

| Stage | Responsibility | Input | Output | Dependency | State |
| --- | --- | --- | --- | --- | --- |
| `FINOPS_ROOT_TASK` | Open the daily run | Graph runtime ID and scheduled time | `FINOPS_RUN` plus pending module rows | Daily `10:00 UTC` | Implemented in repository; deployment pending |
| `FINOPS_CHECK_COST` | Evaluate approved cost rules | `METERING_HISTORY` | Metrics and cost findings | Root | Implemented in repository; deployment pending |
| `FINOPS_CHECK_ERRORS` | Count failed queries | `QUERY_HISTORY` | Metrics; no anomaly verdict | Root | Implemented; rule pending |
| `FINOPS_CHECK_WAREHOUSE` | Measure warehouse and idle credits | `WAREHOUSE_METERING_HISTORY` | Metrics; no anomaly verdict | Root | Implemented; rule pending |
| `FINOPS_CHECK_QUERIES` | Measure query activity and attributed credits | `QUERY_HISTORY`, `QUERY_ATTRIBUTION_HISTORY` | Metrics; no anomaly verdict | Root | Implemented; rule pending |
| `FINOPS_CHECK_AI` | Measure Cortex AI function usage | `CORTEX_AI_FUNCTIONS_USAGE_HISTORY` | Metrics; no anomaly verdict | Root | Implemented; rule pending |
| `FINOPS_CHECK_OTHER_COSTS` | Aggregate non-warehouse and non-AI metering | `METERING_HISTORY` | Metrics; no anomaly verdict | Root | Implemented; rule pending |
| `FINOPS_REPORT_TASK` | Materialize daily summary | Module outcomes and findings | `FINOPS_DAILY_REPORT` | All analysis tasks succeed | Implemented in repository; deployment pending |
| `FINOPS_ALERT_TASK` | Deliver only required notifications | Report status and alert config | `FINOPS_ALERT_DELIVERY` | Report succeeds | Implemented; integration pending |
| `FINOPS_FINALIZER` | Reconcile incomplete/failed graph runs | Persisted module state | Final report, delivery attempt, final run status | Finalizer of root | Implemented in repository; deployment pending |

## Status model

- `NORMAL`: evaluated rule found no anomaly.
- `ATTENTION`: business anomaly matched an approved rule.
- `RULE_NOT_CONFIGURED`: evidence exists, but the team has not approved an anomaly rule.
- `DATA_INCOMPLETE`: the source is not expected complete yet or has not published through the requested window; values remain `NULL`.
- `FAILED`: technical analysis or delivery failure.
- `REVIEW_REQUIRED`: run succeeded but one or more modules lack approved rules.
- `ATTENTION_REQUIRED`: at least one business anomaly or technical failure requires action.

Status folding uses one precedence order: `FAILED > DATA_INCOMPLETE > ATTENTION > REVIEW_REQUIRED > NORMAL`. Module `ATTENTION` maps to run `ATTENTION_REQUIRED`; legacy `RULE_NOT_CONFIGURED` folds as `REVIEW_REQUIRED`. This prevents failures, delayed data, and missing rules from being reported as healthy.

## Cost decision flow

```text
previous-day credits > 25
  └── yes → ATTENTION
  └── no  → previous day exists and growth > 30%
              └── yes → ATTENTION
              └── no  → NORMAL
```

The comparison is strictly greater than each threshold. A missing previous-day baseline does not fabricate a growth alert.

## Failure flow

1. Each procedure marks its module `RUNNING` before reading usage views.
2. An approved anomaly records a finding and completes the module as `ATTENTION`.
3. A technical exception records `FAILED` and is re-raised so Snowflake marks the task failed.
4. Downstream report and alert tasks may be skipped after a child failure.
5. The finalizer marks unfinished modules failed, rebuilds the report idempotently, and attempts the required alert.

## Data model

- `FINOPS_CONFIG`: approved rules and delivery configuration.
- `FINOPS_RUN`: one durable record per graph run group.
- `FINOPS_MODULE_RUN`: one record per run and analysis module.
- `FINOPS_METRIC`: one typed metric per `(RUN_ID, MODULE_NAME, METRIC_KEY)`, including source window, watermark, expected-complete time, and completeness evidence. Repeated writes merge on that identity.
- `FINOPS_FINDING`: rule matches, technical findings, and explicit rule gaps.
- `FINOPS_DAILY_REPORT`: one idempotent summary per run.
- `FINOPS_ALERT_DELIVERY`: notification outcome without storing credentials.

`FINOPS_MODULE_RUN.METRICS` remains the compact module summary. `FINOPS_METRIC` is the durable normalized evidence contract. Before a source's expected-complete time, or when its publication watermark has not reached the requested window, collectors persist `NULL`, `IS_COMPLETE = FALSE`, and `DATA_INCOMPLETE`. Zero is valid only after a successful mature window query; source query and privilege errors remain `FAILED`.

## dbt analytics boundary

`dbt/finops_analytics` reads documented `SNOWFLAKE.ACCOUNT_USAGE` sources and materializes descriptive Cost and Warehouse marts. It does not classify anomalies, write operational run state, send alerts, or replace the procedure contract. The marts preserve raw versus billed credits, source publication evidence, and null attribution rather than manufacturing policy outcomes.

The current Task Graph remains serverless. Native Snowflake tasks that execute a dbt project require a user-managed warehouse, so dbt scheduling is a separate future adaptation that needs explicit warehouse, role, grant, failure, and rollback decisions.

## Repository structure

```text
.
├── docs/
│   ├── architecture.md
│   ├── official-snowflake-evidence.md
│   └── operations/runbook.md
├── dbt/finops_analytics/            # Descriptive Cost and Warehouse marts
├── odd/tasks/                      # Durable feature specification and log
├── scripts/                        # Optional deployment helper only
├── sql/
│   ├── 00_setup/                   # Objects and grants
│   ├── 10_core/                    # Pure policy functions
│   ├── 20_procedures/              # Modular business logic
│   ├── 30_tasks/                   # DAG, resume, and suspend operations
│   └── 90_validation/              # Deployment and smoke checks
└── tests/
    ├── sql/                        # Snowflake integration assertions
    └── test_repository_contract.py # Local structural checks
```

## Security and ownership

All graph tasks live in `FINOPS_DEV.FINOPS` and must share one owner role. Before grants are applied, confirm the schema owner and whether managed access is enabled; managed-access object grants must be issued by the schema owner or a role with `MANAGE GRANTS`. Serverless tasks additionally require account-level `EXECUTE TASK` and `EXECUTE MANAGED TASK` for the task owner. `FINOPS_REPO_OPERATOR` remains limited to repository synchronization and is not the deployment or runtime owner.

## Future event-driven phase

Streams and triggered tasks are **proposed future capabilities**, not implemented graph members. Add them only for a concrete event source that needs lower latency than the daily reconciliation. A triggered task requires stream-consumption ownership, staleness management, and a separate cost/operational justification.

## Decisions still required

- Error-volume rule and severity.
- Warehouse idle-credit rule.
- Expensive-query rule and exclusions.
- AI-credit rule and included AI products.
- Other-service cost rule.
- Notification integration, recipients, and escalation route.
- Retry, automatic-suspension, and serverless size boundaries after measured runs.
