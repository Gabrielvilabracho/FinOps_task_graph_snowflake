# dbt FinOps analytics delivery chain

Objective: deliver the Cost and Warehouse dbt analytics foundation in independently reviewable slices while preserving one final integration boundary.

## Chain

```text
main
 └── feat/dbt-finops-analytics-tracker
      └── feat/dbt-finops-analytics-01-cost
           └── feat/dbt-finops-analytics-02-warehouse
```

1. Cost foundation: project configuration, Account Usage staging, conservative date completeness, Cost mart, tests, and focused documentation.
2. Warehouse extension: warehouse mart, null-safe query attribution, eight-hour freshness boundary, remaining documentation, and complete repository contracts.

Issue: `#8` (explicitly confirmed by the maintainer as the approved tracking issue).

The tracker PR remains draft until both child slices are integrated. Snowflake deployment and live dbt execution remain outside this delivery because no target session was authorized.
