# Official Snowflake Evidence

All platform claims below are grounded in Snowflake documentation. Architectural recommendations are labeled separately.

## Task Graph and finalizer

- [Task graphs](https://docs.snowflake.com/en/user-guide/tasks-graphs): root/child DAGs, `AFTER` dependencies, parallel siblings, finalizers, ownership, limits, overlap, retries, versioning, runtime logic, and graph history.
- [CREATE TASK](https://docs.snowflake.com/en/sql-reference/sql/create-task): serverless tasks omit `WAREHOUSE`; root scheduling supports `USING CRON`; newly created tasks start suspended.
- [SYSTEM$TASK_RUNTIME_INFO](https://docs.snowflake.com/en/sql-reference/functions/system_task_runtime_info): `CURRENT_TASK_GRAPH_RUN_GROUP_ID` and the original scheduled timestamp identify one logical graph run.
- [Task graph configuration](https://docs.snowflake.com/en/sql-reference/functions/system_get_task_graph_config): graph-level JSON is appropriate for small configuration, not durable operational state.
- [Task return values](https://docs.snowflake.com/en/sql-reference/functions/system_set_return_value): predecessor values are strings limited to 10 KB.

Verified constraints:

- Tasks in one traditional graph must share a schema and owner.
- A graph supports up to 1,000 tasks; one task supports up to 100 parents and 100 children.
- One finalizer is allowed per root and runs only after no task remains running or queued.
- Child failures do not prevent the finalizer, but a skipped root does.
- Traditional graph structure must be changed while the root is suspended.

## Observability

- [Information Schema TASK_HISTORY](https://docs.snowflake.com/en/sql-reference/functions/task_history): immediate operational task history with seven-day scope.
- [Account Usage TASK_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/task_history): 365-day history with documented latency.
- [COMPLETE_TASK_GRAPHS](https://docs.snowflake.com/en/sql-reference/account-usage/complete_task_graphs): graph-level completion evidence.

Recommendation: finalization uses persisted module state and immediate runtime information; it must not depend on delayed Account Usage task history.

## Usage and cost evidence

| Source | Use | Important caveat |
| --- | --- | --- |
| [METERING_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/metering_history) | Account service credits | Generally up to three-hour latency; cloud services can be later. |
| [WAREHOUSE_METERING_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/warehouse_metering_history) | Warehouse compute, cloud services, and query-attributed credits | Query-attributed credits exclude idle time. |
| [QUERY_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/query_history) | Query volume, failures, users, roles, tags | Account Usage is delayed and retained for 365 days. |
| [QUERY_ATTRIBUTION_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/query_attribution_history) | Per-query warehouse compute attribution | Can arrive up to eight hours late and excludes idle/serverless/AI costs. |
| [SERVERLESS_TASK_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/serverless_task_history) | Serverless task credits | Separate from warehouse cost. |
| [CORTEX_AI_FUNCTIONS_USAGE_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/cortex_ai_functions_usage_history) | AI function/model/query credits | Covers Cortex AI functions represented by this view, not every possible AI product. |

Recommendation: schedule the daily graph at `10:00 UTC` and use explicit UTC day boundaries so the previous day's query-attribution records have time to arrive.

## Alerts and controls

- [Email notifications](https://docs.snowflake.com/en/user-guide/notifications/email-notifications): `SYSTEM$SEND_EMAIL` requires a notification integration, verified same-account users, and integration `USAGE` for the task owner.
- [Task error notifications](https://docs.snowflake.com/en/user-guide/tasks-errors-integrate): a root `ERROR_INTEGRATION` can publish failed task attempts to supported cloud messaging systems.
- [Budgets](https://docs.snowflake.com/en/user-guide/budgets): monitor and forecast supported services but do not hard-cap usage.
- [Resource monitors](https://docs.snowflake.com/en/user-guide/resource-monitors): can suspend warehouses but do not control serverless or AI spending.

Recommendation: use persisted findings for business alerts, optional native task-error integration for platform failures, and resource monitors only as a separate warehouse guardrail.

## Event-driven option

- [Triggered tasks](https://docs.snowflake.com/en/user-guide/tasks-triggered) and [Streams](https://docs.snowflake.com/en/user-guide/streams-intro) support event-driven processing when new data arrives.

Recommendation: keep this as a future phase until a named event source and a required response time justify stream ownership and staleness management.
