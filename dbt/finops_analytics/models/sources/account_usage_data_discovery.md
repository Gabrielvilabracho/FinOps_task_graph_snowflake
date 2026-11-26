# Account Usage data discovery

Observed on 2026-11-26 through bounded native `dbt show --inline` queries executed by `FINOPS_DBT_ROLE`. Observed account values are kept separate from Snowflake's documented retention and maximum publication-latency contracts.

## Access boundary

- `QUERY_ATTRIBUTION_HISTORY`, `WAREHOUSE_LOAD_HISTORY`, and `WAREHOUSE_EVENTS_HISTORY` were initially readable by the dbt execution role.
- `QUERY_HISTORY` initially returned `Object 'SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY' does not exist or not authorized`.
- With explicit user authorization, `SHOW GRANTS ON VIEW` proved that `SNOWFLAKE.GOVERNANCE_VIEWER` supplies the view access. That one database role was granted to `FINOPS_DBT_ROLE`; no broader privilege was added.
- No deployment, task change, warehouse alteration, schedule change, data mutation, or email delivery was performed.
- The Snowflake Documentation Cortex Knowledge Extension was not installed in the account, so profiling did not create it. Current public Snowflake documentation supplied the documented contracts cited below.

## Source: QUERY_HISTORY

### Overview

- **Observed rows**: 36,354.
- **Observed grain**: One row per `QUERY_ID`; all 36,354 IDs were distinct and non-null.
- **Observed range**: 2026-11-20 11:51 through 2026-11-25 20:07.
- **Observed latest-row lag**: Three minutes during the focused probe.
- **Warehouse attribution**: 1,339 rows had no warehouse ID, which is valid for statements that do not execute on a warehouse.
- **Duration evidence**: `TOTAL_ELAPSED_TIME` ranged from 21 ms to 1,107,456 ms; no negative durations were observed. Maximum execution time was 1,106,098 ms and maximum combined queue/block time was 24,727 ms.
- **Relationship evidence**: All 1,001 observed `QUERY_ATTRIBUTION_HISTORY` query IDs joined to `QUERY_HISTORY`.
- **Documented contract**: 365-day retention and latency up to 45 minutes. Hybrid-table-only short queries are not complete enough in this view for latency percentiles; use `AGGREGATE_QUERY_HISTORY` for that workload.

### Selected columns

The durable base needs `QUERY_ID`, `QUERY_TYPE`, `EXECUTION_STATUS`, `USER_NAME`, `ROLE_NAME`, `WAREHOUSE_ID`, `WAREHOUSE_NAME`, `QUERY_TAG`, `QUERY_HASH`, `QUERY_PARAMETERIZED_HASH`, `START_TIME`, `END_TIME`, `TOTAL_ELAPSED_TIME`, `COMPILATION_TIME`, `EXECUTION_TIME`, `QUEUED_PROVISIONING_TIME`, `QUEUED_REPAIR_TIME`, `QUEUED_OVERLOAD_TIME`, `TRANSACTION_BLOCKED_TIME`, `BYTES_SCANNED`, `ROWS_PRODUCED`, `CREDITS_USED_CLOUD_SERVICES`, `QUERY_RETRY_TIME`, and `FAULT_HANDLING_TIME`. Query text and bind values are intentionally excluded from the first analytics slice.

### Recommended staging transformations

1. Preserve `QUERY_ID` as the unique key and keep statements without warehouses.
2. Store timing values in milliseconds and derive explicit queue totals without conflating them with execution time.
3. Normalize date boundaries to UTC while retaining source LTZ timestamps.
4. Exclude query text and bind values to reduce sensitive-data exposure.

## Source: QUERY_ATTRIBUTION_HISTORY

### Overview

- **Observed rows**: 1,001.
- **Observed grain**: One row per `QUERY_ID`; 1,001 distinct IDs and no null IDs were observed.
- **Observed range**: 2026-11-20 11:58 through 2026-11-25 09:15.
- **Observed latest-row lag**: 646 minutes during the probe.
- **Warehouses**: Two distinct warehouse IDs.
- **Attribution evidence**: No null `CREDITS_ATTRIBUTED_COMPUTE` values were observed. Values were nonnegative in the sampled aggregate.
- **Documented contract**: 365-day retention and latency up to eight hours. The view omits short-running queries of roughly 100 ms or less and excludes idle time.

### Available columns

`QUERY_ID`, `PARENT_QUERY_ID`, `ROOT_QUERY_ID`, `WAREHOUSE_ID`, `WAREHOUSE_NAME`, `QUERY_HASH`, `QUERY_PARAMETERIZED_HASH`, `QUERY_TAG`, `USER_NAME`, `START_TIME`, `END_TIME`, `CREDITS_ATTRIBUTED_COMPUTE`, and `CREDITS_USED_QUERY_ACCELERATION`.

### Recommended staging transformations

1. Preserve `QUERY_ID` as the stable attribution key.
2. Normalize timestamps to explicit UTC boundaries without discarding their LTZ semantics.
3. Keep query-attributed credits separate from metered credits and never label their residual as exact idle duration or guaranteed savings.

## Source: WAREHOUSE_LOAD_HISTORY

### Overview

- **Observed rows**: 673.
- **Observed grain**: One row per `WAREHOUSE_ID` and `START_TIME`; all 673 observed keys were distinct.
- **Observed nulls**: No null warehouse IDs.
- **Observed range**: 2026-11-20 11:50 through 2026-11-25 09:20.
- **Observed latest-row lag**: 637 minutes during the probe.
- **Warehouses**: Three distinct warehouse IDs.
- **Observed maxima**: `AVG_RUNNING` about 1.066, `AVG_QUEUED_LOAD` about 0.001, `AVG_QUEUED_PROVISIONING` about 0.165, and `AVG_BLOCKED` equal to 0.
- **Documented contract**: Five-minute intervals and latency up to three hours. The source page does not state a retention duration, so no retention value is inferred here.

### Available columns

`START_TIME`, `END_TIME`, `WAREHOUSE_ID`, `WAREHOUSE_NAME`, `AVG_RUNNING`, `AVG_QUEUED_LOAD`, `AVG_QUEUED_PROVISIONING`, and `AVG_BLOCKED`.

### Recommended staging transformations

1. Preserve the five-minute source interval rather than inferring a continuous warehouse-on interval.
2. Keep running, queued-load, queued-provisioning, and blocked measures separate.
3. Derive higher-period measures from the interval base, not from averages of already-aggregated percentiles.

## Source: WAREHOUSE_EVENTS_HISTORY

### Overview

- **Observed rows**: 300 in the initial aggregate; a later event distribution contained 312 rows as new history arrived.
- **Observed nulls**: No null warehouse IDs in the initial aggregate.
- **Observed range**: 2026-11-20 11:51 through 2026-11-25 09:20.
- **Observed latest-row lag**: 638 minutes during the initial probe.
- **Observed event names**: `CLUSTER_CONSISTENT`, `WAREHOUSE_CONSISTENT`, `RESUME_WAREHOUSE`, `RESUME_CLUSTER`, `SUSPEND_CLUSTER`, `SUSPEND_WAREHOUSE`, and `CREATE_WAREHOUSE`.
- **Documented contract**: 365-day retention and latency up to three hours. A single operation can emit multiple related rows, so events are not a one-row-per-operation fact table.

### Available columns

`TIMESTAMP`, `WAREHOUSE_ID`, `WAREHOUSE_NAME`, `CLUSTER_NUMBER`, `EVENT_NAME`, `EVENT_REASON`, `EVENT_STATE`, `USER_NAME`, `ROLE_NAME`, `QUERY_ID`, `SIZE`, `CLUSTER_COUNT`, `WAREHOUSE_TYPE`, `GENERATION`, and `RESOURCE_CONSTRAINT`.

### Recommended staging transformations

1. Preserve raw event names and reasons; do not infer exact active or idle intervals from events alone.
2. Treat event history as lifecycle evidence that can bound warehouse-on periods when paired with load and metering data.
3. Keep incomplete intervals null when a matching lifecycle boundary is absent.

## References

- https://docs.snowflake.com/en/sql-reference/account-usage/query_history
- https://docs.snowflake.com/en/sql-reference/account-usage/query_attribution_history
- https://docs.snowflake.com/en/sql-reference/account-usage/warehouse_load_history
- https://docs.snowflake.com/en/sql-reference/account-usage/warehouse_events_history
