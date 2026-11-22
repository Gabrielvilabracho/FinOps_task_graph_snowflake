# FinOps operational analytics expansion

This is the implementation handoff for the next session. The goal is to evolve the current daily Task Graph from simple status classification into an operational report that explains what changed, why it changed, who or what caused it, and what action should be considered.

## Quick path for the next session

1. Read this document and `docs/architecture.md`.
2. Inspect the current objects in `sql/00_setup/01_finops_objects.sql` and checks in `sql/20_procedures/21-26_*.sql`.
3. Treat Slice 1 as the shared metric and completeness contract already implemented for Cost and Warehouse proof points.
4. Run the behavior-first contract tests before extending another collector.
5. Keep HTML rendering separate from metric collection and decision logic.

## Current state

- The local Task Graph definition runs daily at 12:00 UTC and analyzes the previous complete UTC day; this schedule change has not been deployed.
- Six checks run in parallel: Cost, Errors, Warehouse, Queries, AI Services, and Other Costs.
- Only Cost has an approved anomaly policy: daily credits over 25 or day-over-day growth over 30%.
- Warehouse returns `REVIEW_REQUIRED` after complete evidence and `DATA_INCOMPLETE` while publication is incomplete. Errors, Queries, AI Services, and Other Costs collect metrics but return the legacy `RULE_NOT_CONFIGURED` review state.
- The report aggregates module states and attempts one deduplicated email for `ATTENTION_REQUIRED`, `DATA_INCOMPLETE`, or `FAILED` only when delivery is enabled and configured; disabled or incomplete configuration remains `NOT_CONFIGURED`.
- `ACCOUNT_USAGE` views can publish data late. Every result must expose its freshness and completeness.

## Target result

Every reported metric should provide:

| Field | Meaning |
| --- | --- |
| Current value | Value for the analysis day |
| Previous value | Value for the previous comparable day |
| Seven-day baseline | Recent expected behavior |
| Thirty-day baseline | Longer trend |
| Absolute and percentage change | Size of the change |
| Threshold | Approved decision boundary, when one exists |
| Status | `NORMAL`, `ATTENTION`, `REVIEW_REQUIRED`, `FAILED`, or `DATA_INCOMPLETE` |
| Contributors | Warehouses, users, queries, services, models, or objects responsible |
| Explanation | Plain-language reason for the result |
| Recommended action | Concrete operational next step |
| Data freshness | Latest source timestamp and known latency |

The HTML report must render these results. It must not calculate them.

## Analysis by module

### Cost

**Snowflake sources**

- `SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY`
- `SNOWFLAKE.ORGANIZATION_USAGE.USAGE_IN_CURRENCY_DAILY`, when organization access is available

**Questions to answer**

- How much was consumed, adjusted, and actually billed?
- How does the day compare with yesterday and the 7-day and 30-day baselines?
- Which service, warehouse, query, team, or untagged resource caused the change?
- Is the increase isolated or recurrent?

**Likely actions**

- Investigate the top cost driver.
- Add missing cost attribution tags or `QUERY_TAG` values.
- Review budgets and warehouse resource monitors.
- Optimize expensive queries before increasing compute.

### Errors

**Snowflake sources**

- `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.AGGREGATE_QUERY_HISTORY`
- Task history and login history
- `SYSTEM$GET_LOGIN_FAILURE_DETAILS` for supported authentication failures

**Questions to answer**

- Which errors are new, recurring, or increasing?
- Which users, warehouses, tasks, and applications are affected?
- Are failures caused by permissions, SQL, authentication, timeout, blocking, or capacity?
- What is the failure rate instead of only the raw count?

**Likely actions**

- Group failures by root cause and owner.
- Escalate repeated task failures.
- Separate platform failures from user query errors.
- Show representative query IDs and exact error codes.

### Warehouses

**Snowflake sources**

- `SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_LOAD_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_EVENTS_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`

**Questions to answer**

- Which warehouses consume the most credits?
- How much compute was attributed to queries versus idle time?
- Where are queueing, blocking, low cache usage, or local/remote spills occurring?
- Which resize, resume, or suspend events explain the change?

**Likely actions**

- Review `AUTO_SUSPEND` and workload schedules when idle cost is high.
- Resize only after separating query inefficiency from capacity pressure.
- Evaluate multi-cluster behavior when queueing is sustained.
- Separate incompatible workloads when they compete for resources.

### Queries

**Snowflake sources**

- `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.AGGREGATE_QUERY_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.QUERY_ATTRIBUTION_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY`
- `GET_QUERY_OPERATOR_STATS`
- Query Profile and Query Insights

**Questions to answer**

- Which queries are slowest, most expensive, or newly regressed?
- Which users and applications generate the most load?
- Where are bytes scanned, poor pruning, queue time, blocked time, or spills excessive?
- Which recurring queries lack `QUERY_TAG` attribution?

**Likely actions**

- Prioritize by credits and user impact, not duration alone.
- Improve filters, joins, pruning, and repeated workloads.
- Investigate spills before increasing warehouse size.
- Evaluate Query Acceleration only for suitable queries.

### AI Services

**Snowflake sources**

- `SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_FUNCTIONS_USAGE_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.CORTEX_SEARCH_DAILY_USAGE_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.MODEL_SERVING_USAGE_HISTORY`
- `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY`
- AI-related service types in metering history

**Questions to answer**

- Which function, model, user, or application consumes the most tokens and credits?
- Is growth caused by more calls or larger prompts and outputs?
- What is the average cost per call?
- Which AI functions fail or lack an owner?

**Likely actions**

- Reduce unnecessary prompt context.
- Evaluate smaller models for suitable workloads.
- Separate experimental and production usage.
- Configure budgets for supported Cortex resources.

### Other costs

**Snowflake sources**

- Service types in `METERING_HISTORY`
- `SERVERLESS_TASK_HISTORY`
- `PIPE_USAGE_HISTORY`
- `AUTOMATIC_CLUSTERING_HISTORY`
- `MATERIALIZED_VIEW_REFRESH_HISTORY`
- `SEARCH_OPTIMIZATION_HISTORY`
- `REPLICATION_USAGE_HISTORY`
- `STORAGE_USAGE` and `DATABASE_STORAGE_USAGE_HISTORY`

**Questions to answer**

- Which serverless or storage service changed the most?
- What do tasks, Snowpipe, clustering, materialized views, search optimization, and replication cost?
- Which databases are growing fastest?
- Which service appeared for the first time or has no owner?

**Likely actions**

- Review task frequency and unused services.
- Validate that optimization services produce measurable benefit.
- Review storage retention and growth.
- Consolidate small or unnecessarily frequent workloads where appropriate.

## Recommended implementation order

### Analytics foundation — dbt Cost and Warehouse marts (implemented locally)

- `dbt/finops_analytics` defines credential-free project configuration, documented Account Usage sources, staging views, and descriptive daily marts.
- `finops_daily_cost` keeps raw usage, cloud-services adjustments, and billed credits distinct. It does not apply currency conversion or the operational Cost thresholds.
- `finops_warehouse_daily` keeps query-attribution gaps explicit and does not invent a Warehouse anomaly rule.
- The current procedures remain owners of approved rules and durable run persistence. The serverless Task Graph remains unchanged.
- `UDTF_FINOPS_COST_METRICS` and `UDTF_FINOPS_WAREHOUSE_METRICS` are not created because date/warehouse filters over the marts provide the same read interface without duplicating transformations.
- Repository checks are implemented. dbt parse/build and native Snowflake deployment remain pending an installed runner and explicitly authorized Snowflake target.

### Slice 1 — Shared metric contract (implemented in repository)

- `FINOPS_METRIC` is the normalized durable contract, keyed by `(RUN_ID, MODULE_NAME, METRIC_KEY)` and written through one idempotent merge helper. `FINOPS_MODULE_RUN.METRICS` remains the summary payload.
- Typed values, baselines, deltas, thresholds, contributors, explanation, action, source windows, row count, watermark, collection time, expected-complete time, and completeness evidence are explicit.
- Before expected completion, or when publication has not reached the requested window, values are `NULL`, `IS_COMPLETE = FALSE`, and status is `DATA_INCOMPLETE`. A successful mature empty window may be zero. Query and privilege errors remain `FAILED`.
- Shared folding order is `FAILED > DATA_INCOMPLETE > ATTENTION > REVIEW_REQUIRED > NORMAL`; module attention maps to run `ATTENTION_REQUIRED`.
- Cost and Warehouse are narrow proof points only: Cost retains raw `CREDITS_USED` and its strict approved thresholds; Warehouse remains review-required without a new threshold.
- Snowflake compilation, privileges, Account Usage freshness, graph execution, and email delivery remain live checks that require an explicitly authorized session.

### Slice 2 — Cost and Warehouse expansion (not implemented)

- Expand the existing approved Cost policy without changing its current threshold semantics.
- Add billed cloud-services adjustments, currency when available, attribution, and trends.
- Add warehouse idle, queue, spill, cache, and event evidence.
- Keep new warehouse recommendations informational until thresholds are approved.

### Slice 3 — Queries and Errors

- Add query latency percentiles, scan/pruning, queue, blocking, spill, cost attribution, and regression comparisons.
- Group errors by stable root cause and expose affected users, tasks, warehouses, and applications.
- Define approved decision rules only after observing a baseline period.

### Slice 4 — AI Services and Other Costs

- Add token, model, function, call, serving, Cortex Search, and AI credit attribution.
- Add serverless and storage service breakdowns.
- Expose unsupported or unavailable sources explicitly instead of returning zero.

### Slice 5 — Report and HTML email

- Extend `SP_FINOPS_BUILD_REPORT` to produce a structured operational summary.
- Build escaped HTML from already-computed results.
- Change `SYSTEM$SEND_EMAIL` from `text/plain` to `text/html` only after the HTML is tested.
- Preserve the plain-text facts in persisted data for audit and troubleshooting.

## Expected file impact

| Area | Expected files |
| --- | --- |
| Objects and metric storage | `sql/00_setup/01_finops_objects.sql` |
| Shared states and lifecycle | `sql/20_procedures/20_finops_run_lifecycle.sql` |
| Domain collectors | `sql/20_procedures/21-26_*.sql` |
| Report aggregation | `sql/20_procedures/27_finops_report.sql` |
| HTML email delivery | `sql/20_procedures/28_finops_alert.sql` |
| Failure reconciliation | `sql/20_procedures/29_finops_finalizer.sql` |
| Deployment validation | `sql/90_validation/90_validate_deployment.sql` |
| Contracts and regression tests | `tests/sql/*`, `tests/test_repository_contract.py` |

The Task Graph topology should remain unchanged unless a measured runtime or source-latency problem requires a new dependency.

## Decisions required before implementation

- Which Snowflake edition and features are available?
- Is organization-level usage accessible, or only account-level usage?
- What is the reporting currency?
- Which tags and `QUERY_TAG` conventions identify owners, teams, applications, and environments?
- What baseline period is acceptable before approving new anomaly thresholds?
- Which recommendations may trigger automatic action, and which remain advisory?
- Who owns each module and each resulting operational action?

## Verification checklist

- [ ] Existing Cost boundary behavior remains unchanged.
- [ ] Every metric identifies its source and freshness.
- [ ] Previous-day and baseline comparisons use consistent UTC windows.
- [ ] Missing or delayed data never appears as zero or `NORMAL`.
- [ ] Contributors reconcile with the reported totals.
- [ ] Repeated execution for one `RUN_ID` remains idempotent.
- [ ] A failed branch is still reconciled by the finalizer.
- [ ] Email is not duplicated for a delivered run.
- [ ] HTML contains presentation only; decisions remain testable in SQL.
- [ ] Deployment validation confirms every required view and privilege.

## Official Snowflake references

- [METERING_DAILY_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/metering_daily_history)
- [WAREHOUSE_METERING_HISTORY](https://docs.snowflake.com/en/sql-reference/account-usage/warehouse_metering_history)
- [Warehouse cache](https://docs.snowflake.com/en/user-guide/performance-query-warehouse-cache)
- [Warehouse memory and spilling](https://docs.snowflake.com/en/user-guide/performance-query-warehouse-memory)
- [Query Acceleration Service](https://docs.snowflake.com/en/user-guide/query-acceleration-service)
- [Cortex AI Functions usage](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ai-function-studio)
- [Cortex Search costs](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/cortex-search-overview)
- [Snowflake Budgets](https://docs.snowflake.com/en/user-guide/budgets)

## Next session starting point

Start with **Slice 2 — Cost and Warehouse expansion** only after live validation of Slice 1. Do not treat billed/adjusted credits, broader attribution, warehouse queue/spill/cache evidence, or HTML as part of Slice 1.
