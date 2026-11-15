---
type: operations
title: Deployment and Access
description: Safe Snowflake deployment order, managed-access privileges, task-owner boundaries, activation, smoke testing, and rollback.
tags: [deployment, access-control, snowflake, operations]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-15T23:16:32.229Z
sources:
  - id: openwiki-source-66381fd16098d228f5875787
    resource: repo://docs/operations/runbook.md
  - id: openwiki-source-76f3d337b59570f380794dd4
    resource: repo://scripts/deploy.sh
  - id: openwiki-source-a655620558e4ee23d9375ca5
    resource: repo://sql/00_setup/02_finops_grants.sql
  - id: openwiki-source-ba075b472b5d594218454e8f
    resource: repo://sql/00_setup/03_finops_task_owner_grants.template.sql
  - id: openwiki-source-c1eb251dec6548141c4b3df1
    resource: repo://sql/30_tasks/32_suspend_finops_task_graph.sql
generated: { by: "opencode", at: "2026-11-15T23:16:32.229Z" }
---

# Deployment and Access

Deployment is intentionally split into core object creation, administrative access decisions, validation, and explicit graph activation. The repository does not treat local SQL generation as proof that the graph has been deployed successfully in Snowflake.

## Safe deployment sequence

`scripts/deploy.sh <connection>` applies core SQL in dependency order:

1. Tables, configuration, and views.
2. The pure cost-policy function.
3. Lifecycle and six module procedures.
4. Report, alert, and finalizer procedures.
5. The suspended Task Graph.
6. Read-only validation queries.

The script uses `set -euo pipefail`, so a failing `snow sql` command stops the sequence. It deliberately excludes access grants and graph resume. Its final message points operators to those manual steps rather than activating production implicitly.

## Managed-access grant boundary

`DATALAB.SPAIN` is treated as a managed-access schema owned by `SYSADMIN`. The context-confirmed role `GG_APP_CC_REC_DATAWARE_DMO` is an access role, not an assumed runtime owner.

Its grant script uses:

- `SECURITYADMIN` to grant database `USAGE`.
- `SYSADMIN` to grant schema `USAGE`.
- Explicit `SELECT` on the six FinOps tables and two FinOps views.
- Explicit `MONITOR` on the ten FinOps tasks.

It does not grant blanket `ALL` or `FUTURE` privileges, procedure execution, account-level task execution, or `SNOWFLAKE.USAGE_VIEWER` to the access role.

## Task-owner decision

Serverless task execution requires a single confirmed owner role. That role has not been identified in the repository context, so account-level runtime grants remain commented in `03_finops_task_owner_grants.template.sql`.

After approval, administrators must replace the placeholders and confirm that the owner:

- owns every task in the graph;
- can use `DATALAB.SPAIN` and execute every called procedure;
- has `EXECUTE TASK` and `EXECUTE MANAGED TASK`;
- can read the required Account Usage views, through `SNOWFLAKE.USAGE_VIEWER` or approved equivalent privileges;
- can use the approved notification integration when native email is enabled.

Do not apply those privileges to the read/monitor role merely because it needs operational visibility.

## Activation and smoke run

Before activating the schedule:

1. Run local contract tests.
2. Apply core SQL while the root remains suspended.
3. Apply confirmed access and task-owner grants under the appropriate administrative roles.
4. Run `sql/90_validation/90_validate_deployment.sql`.
5. Review alert configuration; email delivery is disabled by default.
6. Resume the finalizer and dependent graph with `31_resume_finops_task_graph.sql`.
7. Execute a manual root-task smoke run with `AWAIT` and inspect persisted run, module, report, finding, and delivery evidence.
8. Rely on the production schedule only after the smoke run is understood.

## Safe stop and recovery

`32_suspend_finops_task_graph.sql` suspends the root to prevent future scheduled runs. Already-running descendants may finish. Before resuming after failure, inspect module records, findings, alert-delivery state, and Snowflake task history. Fix source privileges or query errors instead of weakening policy thresholds.

Repository deployment scripts do not drop historical run tables. Structural rollback restores previous SQL definitions while the root remains suspended.

## Current verification limit

The repository has local static and mocked deployment evidence, but no authorized Snowflake session was available during implementation. Live object creation, effective privileges, Account Usage access, notification delivery, task execution, and finalizer behavior remain unverified in `DATALAB.SPAIN`.

## Related pages

- [Task Graph Architecture](../architecture/task-graph.md)
- [Testing and Verification](../testing/verification.md)
- [Daily FinOps Run](../workflows/daily-finops-run.md)
