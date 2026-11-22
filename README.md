# Snowflake Native FinOps Task Graph

A serverless FinOps monitoring system implemented inside Snowflake with modular SQL procedures, a native Task Graph, durable findings, daily reports, conditional notifications, and a resilient finalizer.

## Current state

| Area | State |
| --- | --- |
| Repository implementation | Implemented in SQL and covered by local contract tests |
| `FINOPS_DEV.FINOPS` application objects | Deployed and structurally validated; no historical data migration was required |
| `FINOPS_METRIC` and `DATA_INCOMPLETE` contract | Earlier deployed baseline compiled; the evidence refactor is local-only, with native compilation and runtime freshness still pending |
| dbt Cost and Warehouse analytics | Implemented locally under `dbt/finops_analytics`; parse, execution, and native deployment remain unverified |
| `FINOPS_REPO_OPERATOR` | Configured for Snowflake Git synchronization only; not an object deployment role |
| Optional `GG_APP_CC_REC_DATAWARE_DMO` access | Pending `sql/00_setup/02_finops_grants.sql` |
| Combined deployment and Task Graph owner role | `FINOPS_TASK_OWNER` created and verified as the sole owner of all ten tasks |
| Task Graph activation | Not revalidated in this local refactor; last authorized observation on November 22 found ten started tasks. No task state was changed here |
| OpenWiki | Generated and finalized with source-backed Claims |
| Streams and triggered tasks | Proposed future phase only |

## What the daily run answers

1. What happened yesterday?
2. Is anything important happening?
3. What must the team check?

Only the cost module has approved anomaly rules: raw `METERING_HISTORY.CREDITS_USED` over 25 or more than 30% day-over-day growth, both strict comparisons. Other modules remain informational or review-required until their rules are approved. Missing or immature source data is `DATA_INCOMPLETE`, never zero or `NORMAL`.

The local [evidence contract refactor](docs/operations/finops-evidence-contract.md) separates
raw consumption, billed credits, warehouse residuals and service-aware AI evidence. These are
overlapping representations, not amounts to sum. The local schedule is once daily at 12:00 UTC,
covering the previous complete UTC day and allowing 12 hours for raw publication. The separate
48-hour financial margin still applies; deployment remains explicitly pending.

The [Tokenomics Foundation research](docs/tokenomics-foundation-research.md) maps the Foundation's
12 publicly indexed project entries across AI production, consumption and value. It records version and
coverage limits, then contrasts the proposed TCA/task/outcome/value contracts with this repository's
bounded Snowflake evidence. It is research guidance—not implemented VADA, FOCUS 1.5, TCA or ROI.

## Graph

```text
FINOPS_ROOT_TASK (12:00 UTC daily, serverless, no overlap)
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

1. Review [architecture](docs/architecture.md), [official evidence](docs/official-snowflake-evidence.md), the [FinOps Framework research](docs/finops-framework-research.md), the [Tokenomics Foundation research](docs/tokenomics-foundation-research.md), and the [dbt analytics guide](docs/operations/dbt-finops-analytics.md).
2. Run the one-time authorized owner bootstrap from `03_finops_task_owner_grants.sql`; optional read/monitor grants remain separate in `02_finops_grants.sql`.
3. Run `./scripts/deploy.sh <snowflake-connection-name>` with the confirmed combined deployment and single task-owner role; it targets `FINOPS_DEV.FINOPS` and keeps the graph suspended.
4. Validate with `sql/90_validation/90_validate_deployment.sql`.
5. Resume only after configuration and notification recipients are approved.

See the [runbook](docs/operations/runbook.md) for prerequisites, deployment, testing, rollback, and incident handling.

## Local verification

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

The SQL tests in `tests/sql/` require a non-production Snowflake environment and an explicitly authorized authenticated session. Local checks do not prove Snowflake compilation, privileges, Account Usage freshness, graph execution, or email delivery.
