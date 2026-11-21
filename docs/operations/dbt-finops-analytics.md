# dbt FinOps analytics

This slice adds descriptive Cost and Warehouse models without changing the operational Task Graph. dbt transforms and tests account metadata; procedures own approved anomaly rules and durable run persistence; the existing tasks, report, and email continue to use those persisted results.

## Models and sources

The project lives in `dbt/finops_analytics` and reads two documented sources:

- `SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY` supplies account-level raw and billed credits. The mart keeps both values explicit and never converts credits to currency.
- `SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY` supplies hourly warehouse usage and query-attributed compute. Query attribution excludes idle time and can be null, so the mart leaves the idle estimate null when attribution is incomplete.

`finops_daily_cost` uses a 365-day date spine. A date becomes complete only after its expected publication time and after a later source date proves publication advanced beyond it; only then can a missing aggregate become a mature zero. Otherwise its values remain null. `finops_warehouse_daily` has one row per observed UTC date and warehouse and waits eight hours for query-attribution publication. Each mart exposes publication evidence and an `is_source_complete` flag.

## Responsibility boundary

The marts contain no attention status, anomaly threshold, or delivery decision. The existing `FINOPS_CLASSIFY_COST` helper retains the strict `>25` credit and `>30%` growth rules, and Warehouse remains informational until a rule is approved.

The current Task Graph remains serverless and unchanged. Snowflake requires a user-managed warehouse for a task that runs `EXECUTE DBT PROJECT`; therefore this analytics-first slice does not insert dbt execution into `FINOPS_ROOT_TASK` or its children.

## Native Snowflake project

The live object is `FINOPS_DEV.FINOPS.FINOPS_DBT_PROJECT`, owned by `FINOPS_DBT_ROLE`. `dbt_projects_profiles.yml` contains no password, token, or private key. Deployment provides the non-secret account, user, execution role, database, schema, and `FINOPS_DBT_WAREHOUSE` values through `DBT_`-prefixed execution variables.

The reproducible administrative baseline lives in `sql/00_setup/04_finops_dbt_bootstrap.sql` and provisions:

1. A user-managed warehouse for dbt execution.
2. A profile role with imported access to `SNOWFLAKE`, usage on target database/schemas, and create privileges for dbt relations.
3. A calling role with usage on the dbt project object and permission to use the profile role.
4. Separate read grants for consumers of the resulting marts.

The approved warehouse is `X-SMALL`, auto-resumes on demand, and auto-suspends after 60 seconds. The deployed native project uses dbt Core 1.9.4 and dbt-snowflake 1.9.2. Its selected Cost/Warehouse build completed with 24 passes, zero warnings, and zero errors. dbt has no automatic schedule, and the operational Task Graph remains separate and suspended until explicitly activated.

## Function assessment

`UDTF_FINOPS_COST_METRICS` is not created in this slice. Filtering `finops_daily_cost` by `analysis_date` already supplies the proposed date-range interface, so a UDTF would duplicate the mart without adding behavior.

`UDTF_FINOPS_WAREHOUSE_METRICS` is also not created. Filtering `finops_warehouse_daily` by date and warehouse provides the same read-only interface while preserving lineage and dbt tests.

The decision is deliberately **no UDTF** until a caller needs a parameterized result that a secured view or direct mart filter cannot provide. If that requirement appears, the function must select from these marts rather than reimplementing source aggregation, and its contract must document inputs, columns, freshness, privileges, and examples.

### Proposed UDTF_FINOPS_COST_METRICS contract

- Inputs: `START_DATE DATE`, `END_DATE DATE` with an inclusive start and exclusive end; reject a reversed or wider-than-approved retention window.
- Output columns: `ANALYSIS_DATE DATE`, raw, compute, cloud-services, adjustment, and billed credit `NUMBER` values; `SOURCE_LATEST_USAGE_DATE DATE`, `EXPECTED_COMPLETE_AT TIMESTAMP_TZ`, and `IS_SOURCE_COMPLETE BOOLEAN`.
- Freshness: select only from `finops_daily_cost`; keep incomplete values null and preserve the mart's conservative publication evidence.
- Privileges: caller needs `USAGE` on the database/schema and function; the function owner needs `SELECT` on the mart. No direct Account Usage access is delegated to callers.
- Example: `SELECT * FROM TABLE(UDTF_FINOPS_COST_METRICS('2026-11-01', '2026-12-01'));` if a future parameterized caller justifies creating it.

### Proposed UDTF_FINOPS_WAREHOUSE_METRICS contract

- Inputs: `START_DATE DATE`, `END_DATE DATE`, and optional `WAREHOUSE_NAME STRING`; use an inclusive start, exclusive end, and exact warehouse match after normal identifier handling.
- Output columns: `ANALYSIS_DATE DATE`, `WAREHOUSE_ID NUMBER`, `WAREHOUSE_NAME STRING`, raw, compute, cloud-services, attributed, and estimated-idle credit `NUMBER` values; `ESTIMATED_IDLE_RATIO FLOAT`, `SOURCE_WATERMARK TIMESTAMP_LTZ`, `EXPECTED_COMPLETE_AT TIMESTAMP_TZ`, and `IS_SOURCE_COMPLETE BOOLEAN`.
- Freshness: select only from `finops_warehouse_daily`; preserve null idle estimates when query attribution is absent and the eight-hour publication boundary.
- Privileges: caller needs `USAGE` on the database/schema and function; the function owner needs `SELECT` on the mart. No direct Account Usage access is delegated to callers.
- Example: `SELECT * FROM TABLE(UDTF_FINOPS_WAREHOUSE_METRICS('2026-11-01', '2026-12-01', 'COMPUTE_WH'));` if secured-view filtering becomes insufficient.

## Verification boundary

Repository tests verify structure, safe warehouse defaults, and ownership boundaries without credentials. Authorized live validation deployed and compiled the native project, built five models, ran 17 data tests and two unit tests, and produced 365 Cost rows plus four Warehouse rows. `FINOPS_DBT_WAREHOUSE` returned to `SUSPENDED`; all ten operational tasks remained suspended. Future source freshness and production behavior still require ongoing observation rather than inference from this first build.

## References

- https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake
- https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake-schedule-project-execution
- https://docs.snowflake.com/en/sql-reference/account-usage/metering_daily_history
- https://docs.snowflake.com/en/sql-reference/account-usage/warehouse_metering_history
- https://docs.getdbt.com/docs/build/unit-tests
