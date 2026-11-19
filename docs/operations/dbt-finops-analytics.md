# dbt FinOps analytics

This first chain slice adds descriptive Cost analytics without changing the operational Task Graph. dbt transforms and tests account metadata; procedures own approved anomaly rules and durable run persistence.

## Cost model

`finops_daily_cost` reads `SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY` through a documented staging model. It keeps raw usage, cloud-services adjustments, and billed credits separate and never converts credits to currency.

A 365-day date spine distinguishes missing dates from observed usage. A date becomes complete only after its expected publication time and after a later source date proves publication advanced beyond it. Before that proof, metric values remain null; only a mature missing aggregate becomes zero.

The mart contains no attention status or anomaly threshold. `FINOPS_CLASSIFY_COST` remains the owner of the strict `>25` credit and `>30%` growth rules.

## Native Snowflake boundary

The project is intended for `DATALAB.SPAIN.FINOPS_DBT_PROJECT`. Its profile contains no password, token, or private key. Snowflake requires a user-managed warehouse for tasks that execute native dbt projects, so this slice does not modify the existing serverless graph.

`UDTF_FINOPS_COST_METRICS` remains unimplemented because filtering the mart by `analysis_date` provides the same interface without duplicating transformations. A future function must select from the mart and preserve its freshness evidence.

Repository tests are credential-free. dbt parse/build, Snowflake compilation, privileges, freshness, and deployment remain pending an explicitly authorized target session.

## References

- https://docs.snowflake.com/en/user-guide/data-engineering/dbt-projects-on-snowflake
- https://docs.snowflake.com/en/sql-reference/account-usage/metering_daily_history
- https://docs.getdbt.com/docs/build/unit-tests
