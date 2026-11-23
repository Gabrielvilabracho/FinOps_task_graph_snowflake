# Validate the native FinOps runtime

Run the native probes after an authorized deployment to `FINOPS_DEV.FINOPS`.
Offline expression tests cannot validate Snowflake Scripting bindings or stored-procedure argument resolution.

## Safe update sequence

1. Record the task names, states, owners, and root schedule.
2. Suspend the root; confirm that `CURRENT_TASK_GRAPHS` has no `EXECUTING` run for this database/schema before changing procedures. The function accepts the unqualified root name `FINOPS_ROOT_TASK` and also returns future `SCHEDULED` runs.
3. Publish only the changed functions/procedures. Existing tables and configuration do not need recreation. For the noon update, set the root schedule to `USING CRON 0 12 * * * UTC` while suspended.
4. Run the probes below. Compare operational table counts and hashes before/after to verify rollback.
5. Resume only the tasks recorded as started, with the root last. Confirm the resulting schedule and task states.

## Native regression and real-source smoke

```bash
snow sql --connection finops --database FINOPS_DEV --schema FINOPS \
  --role FINOPS_TASK_OWNER --secondary-roles NONE \
  --filename tests/sql/05_native_runtime_regression_test.sql \
  --filename tests/sql/06_collectors_real_source_smoke_test.sql
```

Both probes use unique run IDs and roll back on success or failure. They do not execute the task graph or finalizer and do not send email.

| Probe | Checks |
| --- | --- |
| Native regression | Bound exception diagnostics, decimal metric preservation, strict policy boundaries, finding/report idempotency, report ordering and real newlines |
| Alert failure path | An uncommitted invalid boolean causes failure before recipient lookup or sending; both failure-log merge branches are checked, then all fixture configuration and records are rolled back |
| Real-source smoke | Six collectors against Account Usage, seven metric records, one report, no technical module failures or alert delivery |

`DATA_INCOMPLETE` is a valid evidence outcome, not a compilation failure. Optional unavailable sources must remain unknown rather than become fabricated zeros. The 48-hour financial margin is unchanged.

## Runtime fixes

- Bind `:SQLCODE` and `:SQLERRM` inside SQL statements; bare variables remain valid in scripting expressions.
- Use a literal `\n` separator in `LISTAGG`, retaining the existing report text.
- Match metric arguments explicitly to `VARIANT`, `TIMESTAMP_LTZ`, and fixed-point numeric types. Preserve nine decimal places at the metric procedure boundary, matching the existing metric columns.
- Project `OBJECT_CONSTRUCT` through `INSERT ... SELECT` instead of an unsupported `VALUES` expression.

Rebuild the changed dbt marts separately using the existing native project and its owner role. Use `snow dbt deploy` without `--force` to preserve project versions and run history; a source upload alone does not refresh materialized tables. See [dbt operations](dbt-finops-analytics.md).

## References

- [Snowflake Scripting exception bindings](https://docs.snowflake.com/en/developer-guide/snowflake-scripting/exceptions)
- [LISTAGG constant delimiter](https://docs.snowflake.com/en/sql-reference/functions/listagg)
- [Current task graphs](https://docs.snowflake.com/en/sql-reference/functions/current_task_graphs)
- [Non-destructive dbt deployment](https://docs.snowflake.com/en/developer-guide/snowflake-cli/command-reference/dbt-commands/deploy)
