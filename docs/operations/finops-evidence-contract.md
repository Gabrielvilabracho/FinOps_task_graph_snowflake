# FinOps evidence without double counting

The local refactor separates raw consumption, billed-credit evidence, technical attribution,
business policy and actions. It preserves the existing six-module graph and procedure signatures.
**These changes have not been deployed or compiled in Snowflake.** The root schedule definition
is now 12:00 UTC daily, as explicitly requested. No live schedules, grants, task states,
stored-data migrations, notification settings or remediation actions were changed.

## Read the results

| Representation | Source and unit | Contract |
| --- | --- | --- |
| `COST.DAILY_CREDITS` | Hourly `METERING_HISTORY.CREDITS_USED`, credits | Existing raw-usage key and strict 25-credit / 30% growth policy remain unchanged. Not billed credits or currency. |
| `COST.DAY_OVER_DAY_GROWTH_RATIO` | Same source, ratio | Previous-day maturity/history is checked independently. A missing baseline is null, not zero; the growth metric is incomplete without it. |
| `COST.DAILY_BILLED_CREDITS` | `METERING_DAILY_HISTORY`, credits | Separate daily billed credits after cloud-services adjustment. Provisional observations remain labelled in evidence; the typed value is null until ready. Never add to hourly usage. |
| `WAREHOUSE.COMPUTE_RESIDUAL_CREDITS` | `WAREHOUSE_METERING_HISTORY`, credits | Signed compute less query-attributed compute. Every compute and attribution row must be known. Over-attribution stays negative, not hidden. |
| `AI.CORTEX_AI_FUNCTION_CREDITS` | `CORTEX_AI_FUNCTIONS_USAGE_HISTORY`, credits | Functions-only detail; excludes warehouse compute. All hourly rows are retained; one completion marker per query prevents join fan-out, including queries ending on a later day. |
| `AI.USER_AI_SUBSET_CREDITS` | `USER_AI_USAGE_HISTORY`, credits | Broader service-labelled subset, aggregated without user or object identities. Not all AI expense; not additive to Functions or daily account metering. |

`estimated_idle_credits` and `estimated_idle_ratio` remain compatibility aliases for the
nonnegative warehouse residual. They do **not** establish waste, savings, business ownership
or chargeback. The new signed residual is the reconciliation field. Warehouse counts use stable
warehouse IDs, including rows with an unresolved name. Ownership remains `UNKNOWN`; query-level
QAS is `NOT_COLLECTED`, never an inferred zero.

## Publication, history and nulls

`IS_COMPLETE` means the stated checks passed for the **observed population**, not that every
service was invoiced or every missing population independently reconciled. Keep `source_rows`,
known-value counts, history boundaries, reasons and source scope alongside the number.

| Evidence | Readiness checks |
| --- | --- |
| Hourly account raw credits | Conservative 12h account-wide wait, covering potentially absent Streaming populations; per-service metadata records 6h for raw totals including cloud services, 12h for Streaming. Covering watermark, historical start and all observed values are required. |
| Daily billed credits | Documented source latency is 3h. A separate **local conservative 48h reconciliation margin** keeps young financial observations provisional; earlier/later observed history and known raw/adjustment/billed values are required. The procedure verifies session `TIMEZONE = UTC`; it does not change it. |
| Warehouse collector | 6h for raw totals including cloud services, covering watermark/history and known compute values. Attribution has its own known-row guard. |
| Warehouse dbt mart | Existing conservative 8h wait retained, with explicit UTC boundary construction. Values remain descriptive/provisional until `is_source_complete`; attribution coverage is independent. |
| Functions detail | At least the 5-minute update SLA after the UTC window, known credits, observed history and terminal query markers. Documented history begins January 5, 2026. |
| User-AI subset | 1h publication window, known credits and observed history. Documented history begins March 1, 2026; source retention is 12 calendar months including the current month. |

Elapsed time or a later global watermark alone cannot prove an empty day was zero.
`SOURCE_PUBLICATION_ABSENT`, `HISTORY_NOT_COVERED`, `SOURCE_VALUES_INCOMPLETE`,
`SOURCE_NOT_EXPECTED_COMPLETE`, `SOURCE_PUBLICATION_INCOMPLETE`, `IN_PROGRESS_QUERIES`
and `ATTRIBUTION_UNAVAILABLE` remain explicit. A mature **observed zero-credit row** can be zero.
The earliest partially observed historical period stays unknown; no historical owners are invented.

Optional daily financial or User-AI source failures become `SOURCE_UNAVAILABLE` without discarding
the primary raw/Functions evidence. No error text, identity, query text, prompt or response is
copied into the new evidence. Required primary-source failures still use the existing failure helper.
Incomplete typed metrics participate in the existing failed > incomplete > attention > review > normal fold.

The dbt daily source must be queried in a **UTC session**; this is a deployment precondition,
not something local tests establish. Daily raw, adjustment and billed values remain separate;
conditional data tests replace unconditional non-null expectations for provisional financial rows.
The marts do not call operational procedures or apply anomaly/ownership policies.

## Coverage is not an AI grand total

The report carries Functions observations, User-AI service aggregates and an explicit coverage
inventory. AISQL alternative detail, standalone Analyst, Agents/CoWork request detail, Search
serving/embedding and Gateway/direct-REST detail are `NOT_COLLECTED`. Direct REST credit-field
semantics still need verification. User-AI includes only a service subset and Gateway inference
is not direct REST. Credit-family mapping remains `UNKNOWN` until verified; names are not guessed.
Containers are compute-pool consumption, not automatically AI workload cost.

`OTHER_COSTS` is unchanged and is **not** a disjoint complement of AI. COST, WAREHOUSE, AI and
OTHER_COSTS expose overlapping views of consumption. Do not sum their module totals. FOCUS,
currency, contracts and effective cost are not collected by this implementation; their absence
is a boundary, not a zero or an invoice-reconciliation result.

## Workflow and operational gates

Reports retain existing module summaries and status fields, adding `evidence_contract`, readiness,
basis and scope notes to JSON and text. The report authorizes no actions. Existing alert and
finalizer code, idempotent metric/report writes and the shared status fold are unchanged.

**The selected local schedule is 12:00 UTC once daily**, analyzing the previous UTC day from
00:00 inclusive to the next 00:00 exclusive. This provides a 12-hour publication margin after
day close, not a 12-hour execution frequency. Source/history/null checks still apply at noon.
The separate 48h financial margin is unchanged, so previous-day billed evidence remains
provisional at that run. Financial reconciliation or historical reruns need a separate decision
before deployment. No live task was rescheduled.

Remaining gates: native compilation and fixture execution, least-privilege source access, UTC
session settings, live publication validation, invoice/currency reconciliation, effective-dated
ownership and allocation policy, non-cost thresholds, notification authorization and rollback.
Forecasting, realized savings, complete Product TCA, chargeback and automatic remediation are not validated.

## Local proof and rollback boundary

Run `python3 -m unittest discover -s tests -p "test_*.py"` locally. Executable fixtures extract
the shipped SQL helper bodies, mart SELECTs, Functions aggregation and report line expression.
SQLite adapters implement a narrow syntax subset; they do not establish Snowflake compilation,
fixed-point precision, Scripting exception handling, privileges, dbt execution or graph behavior.
Structural checks pin integration with existing lifecycle helpers. Native SQL/dbt checks require
separate authorization and remain pending; no historical account queries are needed for local tests.

Rollback is confined to the modified core/collector/report SQL, descriptive marts/YAML, their tests
and documentation. No deployed objects or existing stored records have been changed here.

## Source references

- [Metering history](https://docs.snowflake.com/en/sql-reference/account-usage/metering_history)
- [Daily metering](https://docs.snowflake.com/en/sql-reference/account-usage/metering_daily_history)
- [Warehouse metering](https://docs.snowflake.com/en/sql-reference/account-usage/warehouse_metering_history)
- [AI Functions history](https://docs.snowflake.com/en/sql-reference/account-usage/cortex_ai_functions_usage_history)
- [User-AI history](https://docs.snowflake.com/en/sql-reference/account-usage/user_ai_usage_history)
- [Framework research and capability gates](../finops-framework-research.md)
