# Snowflake Native FinOps Task Graph

A serverless FinOps monitoring system implemented inside Snowflake with modular SQL procedures, a native Task Graph, durable findings, daily reports, conditional notifications, and a resilient finalizer.

## Current state

| Area | State |
| --- | --- |
| Repository implementation | Implemented in SQL and covered by local contract tests |
| `FINOPS_RUN`, `FINOPS_MODULE_RUN` in target Snowflake | Reported as created; not independently verified |
| Remaining tables, procedures, tasks, reports, and alerts in target Snowflake | Pending deployment and live validation |
| `GG_APP_CC_REC_DATAWARE_DMO` access | Pending `sql/00_setup/02_finops_grants.sql` |
| Task Graph owner role | Pending explicit confirmation before applying `03_finops_task_owner_grants.template.sql` |
| OpenWiki | Generated and finalized with source-backed Claims |
| Streams and triggered tasks | Proposed future phase only |

## What the daily run answers

1. What happened yesterday?
2. Is anything important happening?
3. What must the team check?

Only the cost module has approved anomaly rules: more than 25 credits or more than 30% day-over-day growth. Other modules collect evidence and return `RULE_NOT_CONFIGURED` until their alert rules are approved.

## Graph

```text
FINOPS_ROOT_TASK (10:00 UTC, serverless, no overlap)
├── FINOPS_CHECK_COST
├── FINOPS_CHECK_ERRORS
├── FINOPS_CHECK_WAREHOUSE
├── FINOPS_CHECK_QUERIES
├── FINOPS_CHECK_AI
└── FINOPS_CHECK_OTHER_COSTS
    └── FINOPS_REPORT_TASK (waits for every analysis branch)
        └── FINOPS_ALERT_TASK

FINOPS_FINALIZER (runs after the graph completes or a child fails)
```

## Quick path

1. Review [architecture](docs/architecture.md) and [official evidence](docs/official-snowflake-evidence.md).
2. Deploy SQL in numeric order; keep the root suspended during structural changes.
3. Apply read/monitor grants from `02_finops_grants.sql`; confirm the owner role before adapting the separate task-owner template.
4. Validate with `sql/90_validation/90_validate_deployment.sql`.
5. Resume only after configuration and notification recipients are approved.

See the [runbook](docs/operations/runbook.md) for prerequisites, deployment, testing, rollback, and incident handling.

## Local verification

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

The SQL tests in `tests/sql/` require a non-production Snowflake environment and an explicitly authorized authenticated session.
