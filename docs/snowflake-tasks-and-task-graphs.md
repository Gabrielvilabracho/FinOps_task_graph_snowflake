# Snowflake Tasks and Task Graphs

This guide explains Snowflake tasks and Task Graphs as general orchestration concepts, then maps those concepts to this repository. It is intended for study, architecture discussions, and deciding when a Task Graph is an appropriate solution.

## Mental model

A **task** is a Snowflake object that executes SQL or calls a stored procedure. It can run on a schedule, after another task, or when a condition is satisfied. A task answers one question: **what unit of work should Snowflake execute, and when?**

A **Task Graph** is a directed acyclic graph (DAG) made from related tasks:

- **Directed:** dependencies define the direction of execution.
- **Acyclic:** a task cannot eventually depend on itself.
- **Graph:** one task can have multiple predecessors or successors.

The root starts a graph run. Child tasks use dependency relationships to express ordering. Snowflake then schedules every task whose predecessors and conditions allow it to run.

```text
root task
   │
   ├── child A ──┐
   └── child B ──┴──> consolidation task ──> notification task
```

The graph coordinates work; it should not become the only place where business state exists. Durable execution state, results, and audit information normally belong in tables or in the procedures called by the tasks.

## Anatomy of a task

| Element | Purpose |
| --- | --- |
| Task body | SQL statement or stored procedure call that performs one bounded unit of work |
| Compute model | User-managed warehouse or Snowflake-managed serverless compute |
| Start rule | Schedule for a root task, dependency for a child task, or an event/condition |
| `AFTER` | Declares one or more predecessor tasks |
| `WHEN` | Evaluates whether an eligible task should run |
| Return value | Small string value passed from one task to later tasks in the same graph run |
| Finalizer | Special task associated with the root that runs after the graph settles |
| State | Tasks are created suspended and must be enabled deliberately |

A task definition is orchestration metadata, not a replacement for a stored procedure. Complex transformations, reusable validation, and transactional behavior are easier to test and maintain when they remain in procedures or models and the task only invokes them.

## Graph execution patterns

### 1. Sequential flow

```text
A ──> B ──> C
```

Each task starts only after its predecessor completes successfully. This pattern is appropriate when every step requires the output or side effects of the previous step.

Typical uses:

- ingest, validate, and publish a dataset;
- build staging, intermediate, and reporting tables;
- generate a report before sending its notification;
- apply ordered maintenance operations.

Trade-off: the flow is easy to understand, but independent work is unnecessarily slow if it is forced into the same chain.

### 2. Fan-out (parallel work)

```text
        ┌──> B
A ──────┼──> C
        └──> D
```

One parent enables several independent children. Snowflake may execute those children concurrently when compute and scheduling capacity are available.

Typical uses:

- load independent dimensions after a common ingestion step;
- run several quality checks over the same snapshot;
- analyze costs, errors, queries, and warehouses independently;
- process independent partitions or business domains.

Trade-off: fan-out reduces elapsed time, but every branch must be independent. Shared mutable state can introduce races or inconsistent results.

### 3. Fan-in (convergence)

```text
B ──┐
C ──┼──> E
D ──┘
```

One task declares multiple predecessors and waits for all required branches. It creates an explicit synchronization point.

Typical uses:

- build a fact table after all dimensions are ready;
- publish an aggregate after several source domains complete;
- generate one report from multiple analyses;
- start reconciliation only after parallel validations finish.

Trade-off: the convergence task is constrained by the slowest predecessor. A failed predecessor normally prevents the success-path convergence task from running.

### 4. Finalizer (cleanup and reconciliation)

```text
root ──> graph work
  └────> finalizer, after the graph settles
```

A finalizer is associated with the root through `FINALIZE`, rather than as an ordinary success-only child. It runs after the graph has no remaining running or queued tasks, including graph runs where a child failed.

Typical uses:

- close or reconcile a persisted run record;
- release logical resources or temporary markers;
- write final audit information;
- summarize failures and emit operational alerts;
- make retries safe by recording the terminal state.

A finalizer is not a substitute for transactional cleanup inside an individual task. It is a graph-level recovery boundary.

### 5. Conditional or dynamic routing

```text
              ┌── condition true ──> B
A returns X ──┤
              └── condition false ─> C
```

A predecessor can publish a small return value with `SYSTEM$SET_RETURN_VALUE`. A later task can inspect it with `SYSTEM$GET_PREDECESSOR_RETURN_VALUE` inside a `WHEN` expression and decide whether to run.

Typical uses:

- skip processing when no new data is available;
- select a success, warning, or remediation branch;
- send an alert only when a report contains actionable findings;
- stop expensive downstream work after a validation gate fails.

Return values are control signals, not durable storage. They are strings with a documented size limit. Persist business results in tables, and use return values only to guide execution within the current graph run.

### 6. Event-driven processing

A triggered task reacts to changes detected through a stream instead of waiting for a fixed schedule.

Typical uses:

- process newly arrived rows with lower latency;
- apply incremental transformations when change data becomes available;
- avoid polling schedules when arrivals are irregular.

Use scheduled tasks when a predictable batch window is the real requirement. Use triggered tasks when the arrival of data, rather than the clock, should initiate work.

## Choosing the right pattern

| Requirement | Recommended pattern |
| --- | --- |
| Every step depends on the previous result | Sequential |
| Several operations share a starting point but are independent | Fan-out |
| One result requires several completed branches | Fan-in |
| Graph-level state must be reconciled after success or failure | Finalizer |
| A runtime signal decides whether a branch is useful | Conditional |
| Data arrival should initiate processing | Triggered task |

Most production graphs combine several patterns. A common shape is scheduled root → fan-out analysis → fan-in report → sequential notification, with a finalizer covering the entire run.

## When Task Graphs are a good fit

Task Graphs are well suited when:

- the work already lives primarily inside Snowflake;
- SQL and stored procedures are the natural execution units;
- dependencies form a bounded DAG;
- Snowflake-native scheduling and task history provide enough observability;
- the team wants to avoid operating an external orchestrator for a contained workflow.

Consider an external orchestrator when the workflow coordinates many systems outside Snowflake, requires rich human approvals, needs complex cross-platform retries, or has long-lived state transitions that are difficult to express as a bounded DAG.

## Design and operational guidance

### Keep tasks small and idempotent

Each task should own one clear responsibility. Re-running the same graph run should not duplicate reports, alerts, or persisted findings. Prefer deterministic identifiers and `MERGE`-style writes where appropriate.

### Persist durable state

Record run identifiers, module status, timestamps, errors, and outputs in tables. Task history explains orchestration; application tables explain business outcomes.

### Separate anomaly from failure

An unexpected business value is not the same as a technical execution failure. Model them separately so a valid warning does not look like a broken pipeline.

### Design failure behavior explicitly

For every branch, decide:

1. What happens if it fails?
2. Which downstream tasks should be skipped?
3. What state must the finalizer reconcile?
4. Is retry safe?
5. How will operators discover the failure?

### Control overlap

Decide whether a new scheduled run may start while a previous run is still active. Prevent overlap when runs modify the same logical period or shared state and concurrency has not been designed deliberately.

### Treat ownership as part of the architecture

Tasks in a traditional graph have ownership constraints. Use one confirmed owner role for the graph and grant only the privileges required by the task bodies and their compute model.

### Activate deliberately

Deployment and activation are separate operations. Validate objects, privileges, configuration, and task state before enabling the root and its dependents.

## Patterns in this repository

The FinOps graph combines four implemented patterns:

```text
FINOPS_ROOT_TASK
├── FINOPS_CHECK_COST ───────────┐
├── FINOPS_CHECK_ERRORS ─────────┤
├── FINOPS_CHECK_WAREHOUSE ──────┤
├── FINOPS_CHECK_QUERIES ────────┼──> FINOPS_REPORT_TASK ──> FINOPS_ALERT_TASK
├── FINOPS_CHECK_AI ─────────────┤
└── FINOPS_CHECK_OTHER_COSTS ────┘

FINOPS_FINALIZER -- FINALIZE = FINOPS_ROOT_TASK
```

- **Fan-out:** the root enables six independent analysis tasks.
- **Fan-in:** the report waits for all six analyses.
- **Sequential:** the alert follows the completed report.
- **Finalizer:** the finalizer reconciles the persisted run after the graph settles, including child-failure paths.

The current graph does **not** implement conditional branches with `SYSTEM$GET_PREDECESSOR_RETURN_VALUE`. Its conditional notification decision is handled inside the report and alert procedures; that is different from dynamically selecting graph branches.

Implementation: [`sql/30_tasks/30_finops_task_graph.sql`](../sql/30_tasks/30_finops_task_graph.sql).

## Study questions

1. Which branches can run concurrently, and what state do they share?
2. What prevents the report from observing incomplete analysis?
3. Which failures skip the normal report and alert path?
4. What state does the finalizer need to reconstruct?
5. Would a return value be sufficient for a decision, or must the result be persisted?
6. Is the workflow clock-driven, data-driven, or a mixture of both?

If these questions cannot be answered from the graph and its procedures, the design needs clearer boundaries before activation.

## Official references

- [Introduction to task graphs](https://docs.snowflake.com/en/user-guide/tasks-graphs)
- [`CREATE TASK`](https://docs.snowflake.com/en/sql-reference/sql/create-task)
- [Task return values](https://docs.snowflake.com/en/sql-reference/functions/system_set_return_value)
- [`SYSTEM$GET_PREDECESSOR_RETURN_VALUE`](https://docs.snowflake.com/en/sql-reference/functions/system_get_predecessor_return_value)
- [Triggered tasks](https://docs.snowflake.com/en/user-guide/tasks-triggered)
- [Task history](https://docs.snowflake.com/en/sql-reference/functions/task_history)
