# Operations Runbook

## Prerequisites

- An explicitly authorized Snowflake session.
- `SYSADMIN` or the managed-access schema owner for schema-level grants.
- `ACCOUNTADMIN` for account-level serverless-task privileges when not already delegated.
- A single approved task-owner role with access to `SNOWFLAKE.ACCOUNT_USAGE` through `USAGE_VIEWER` or equivalent privileges.
- An email notification integration and verified recipients only when alert delivery is enabled.

## Deployment order

Keep `FINOPS_ROOT_TASK` suspended while changing graph structure.

```text
sql/00_setup/01_finops_objects.sql
sql/10_core/10_finops_cost_policy.sql
sql/10_core/11_finops_status_precedence.sql
sql/20_procedures/20_finops_run_lifecycle.sql
sql/20_procedures/21_finops_check_cost.sql
sql/20_procedures/22_finops_check_errors.sql
sql/20_procedures/23_finops_check_warehouse.sql
sql/20_procedures/24_finops_check_queries.sql
sql/20_procedures/25_finops_check_ai.sql
sql/20_procedures/26_finops_check_other_costs.sql
sql/20_procedures/27_finops_report.sql
sql/20_procedures/28_finops_alert.sql
sql/20_procedures/29_finops_finalizer.sql
sql/30_tasks/30_finops_task_graph.sql
sql/00_setup/02_finops_grants.sql
sql/90_validation/90_validate_deployment.sql
```

Do not run `31_resume_finops_task_graph.sql` until validation passes and the notification configuration is reviewed.

## Alert configuration

Alerting is disabled by default. Configure values without storing credentials:

```sql
UPDATE DATALAB.SPAIN.FINOPS_CONFIG
SET CONFIG_VALUE = TO_VARIANT('FINOPS_EMAIL_INTEGRATION'), UPDATED_AT = CURRENT_TIMESTAMP()
WHERE MODULE_NAME = 'ALERT' AND CONFIG_KEY = 'EMAIL_INTEGRATION';

UPDATE DATALAB.SPAIN.FINOPS_CONFIG
SET CONFIG_VALUE = TO_VARIANT('verified.user@example.com'), UPDATED_AT = CURRENT_TIMESTAMP()
WHERE MODULE_NAME = 'ALERT' AND CONFIG_KEY = 'RECIPIENTS';

UPDATE DATALAB.SPAIN.FINOPS_CONFIG
SET CONFIG_VALUE = TO_VARIANT(TRUE), UPDATED_AT = CURRENT_TIMESTAMP()
WHERE MODULE_NAME = 'ALERT' AND CONFIG_KEY = 'ENABLED';
```

## Verification

1. Run local contract tests.
2. Run `sql/90_validation/90_validate_deployment.sql`.
3. Run `tests/sql/00_cost_policy_test.sql`, `02_metric_contract_test.sql`, and `03_status_precedence_test.sql` in a non-production environment.
4. Resume children/finalizer, execute `FINOPS_ROOT_TASK AWAIT`, and inspect run tables.
5. Resume the production schedule only after the smoke run is understood.

The context-confirmed `GG_APP_CC_REC_DATAWARE_DMO` role receives only object-scoped FinOps read and monitor grants. The team must identify the single Task Graph owner before applying the account-level template in `sql/00_setup/03_finops_task_owner_grants.template.sql`.

## Daily interpretation

```text
Analysis date: 2026-11-14
COST: ATTENTION — approved cost rule matched
ERRORS: RULE_NOT_CONFIGURED — evidence collected, rule pending
WAREHOUSE: RULE_NOT_CONFIGURED — evidence collected, rule pending
QUERIES: RULE_NOT_CONFIGURED — evidence collected, rule pending
AI: RULE_NOT_CONFIGURED — evidence collected, rule pending
OTHER_COSTS: RULE_NOT_CONFIGURED — evidence collected, rule pending
Overall: ATTENTION_REQUIRED
```

`FAILED` outranks `DATA_INCOMPLETE`, which outranks business attention. `DATA_INCOMPLETE` is alert-worthy and never falls through to `NORMAL`; delivered alerts remain deduplicated by run and channel.

## Incident handling

- If the root is suspended after failures, inspect `FINOPS_MODULE_RUN`, `FINOPS_FINDING`, and Information Schema `TASK_HISTORY` before resuming.
- If a module failed, correct the source privilege/query issue and retry the graph with Snowflake's graph retry capability or run a new manual graph execution.
- If alert delivery failed, inspect `FINOPS_ALERT_DELIVERY`; do not assume the notification was sent.
- If Account Usage data is incomplete, rerun after documented source latency instead of lowering or fabricating a threshold.

## Unsupported live checks

Without an explicitly authorized session, Snowflake compilation, object privileges, Account Usage freshness, Task Graph execution, and email delivery remain unverified. Repository tests do not prove those live behaviors.

## Safe stop and rollback

Run `sql/30_tasks/32_suspend_finops_task_graph.sql`. Suspending the root prevents future schedules; active children may finish. Repository deployment scripts never drop run history tables. Structural rollback should restore the prior SQL definitions while the root remains suspended.
