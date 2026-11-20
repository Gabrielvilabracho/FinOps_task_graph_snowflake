# ADR 0001 — Use a Traditional Snowflake Task Graph

## Status

Accepted for the first implementation.

## Context

Snowflake supports both a root-task-based graph and a newer `TASK GRAPH` object. The requested design names independent tasks and requires a root task and finalizer. The original `DATALAB.SPAIN` context was superseded by the selected clean-deployment target `FINOPS_DEV.FINOPS`.

## Decision

Use individually declared `CREATE TASK` objects connected by `AFTER`, with `CREATE TASK ... FINALIZE = FINOPS_ROOT_TASK` for closure.

## Consequences

- Every task is directly visible and independently inspectable.
- The graph works with the established root/child/finalizer model and documented limits.
- All tasks must share one schema and owner.
- The root must be suspended before structural graph changes.
- A future migration to a `TASK GRAPH` object requires separate compatibility and operational validation; it is not silently mixed into this graph.

## Evidence

- https://docs.snowflake.com/en/user-guide/tasks-graphs
- https://docs.snowflake.com/en/user-guide/task-graph-object
