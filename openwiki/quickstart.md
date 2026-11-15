---
type: quickstart
title: FinOps Task Graph Quickstart
description: Entry point for understanding, testing, deploying, and operating the native Snowflake FinOps Task Graph safely.
tags: [quickstart, snowflake, finops, navigation]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-15T23:36:35.919Z
sources:
  - id: openwiki-source-66381fd16098d228f5875787
    resource: repo://docs/operations/runbook.md
  - id: openwiki-source-23775c3de52f3ab95a13cb8b
    resource: repo://README.md
generated: { by: "opencode", at: "2026-11-15T23:36:35.919Z" }
---

# FinOps Task Graph Quickstart

This repository implements a native Snowflake FinOps system in `DATALAB.SPAIN`. A daily serverless Task Graph opens a durable run, executes six analyzers, builds a report, conditionally sends email, and uses a finalizer to reconcile failures.

## Current status

- Repository SQL, shell tooling, and local contract tests are implemented.
- `FINOPS_RUN` and `FINOPS_MODULE_RUN` were reported as present in the target account but were not independently verified.
- Remaining objects, effective grants, Task Graph execution, notification delivery, and finalizer behavior are pending live Snowflake validation.
- `GG_APP_CC_REC_DATAWARE_DMO` is treated only as the confirmed read/monitor access role.
- The single Task Graph owner role still requires an explicit team decision.
- OpenWiki is generated and finalized with source-backed Claims and guarded maintenance tests.
- Streams and triggered tasks are a proposed future phase, not current runtime members.

## Start with the question you have

| Question | Read |
| --- | --- |
| How is the DAG scheduled and connected? | [Task Graph Architecture](architecture/task-graph.md) |
| What do statuses, findings, and thresholds mean? | [State and Cost Policy](concepts/state-and-cost-policy.md) |
| What happens during one daily execution? | [Daily FinOps Run](workflows/daily-finops-run.md) |
| How do I deploy without over-granting or auto-activating? | [Deployment and Access](operations/deployment-and-access.md) |
| What is proven locally and what still needs Snowflake? | [Testing and Verification](testing/verification.md) |

## Runtime at a glance

```text
10:00 UTC root
  ├─ cost ────────────┐
  ├─ errors ──────────┤
  ├─ warehouse ───────┤
  ├─ queries ─────────┼─> report ─> conditional alert
  ├─ AI ──────────────┤
  └─ other costs ─────┘

finalizer: reconciles the completed or failed graph
```

Only cost has approved anomaly rules: strictly more than `25` daily credits or strictly more than `30%` day-over-day growth. Other modules collect evidence and return `RULE_NOT_CONFIGURED` until the team approves their rules.

## Safe local entrypoints

Run local tests:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
bash -n scripts/deploy.sh
git diff --check
```

Inspect the deployment sequence without assuming it activates production: `scripts/deploy.sh` applies core SQL and validation but intentionally leaves grants and resume manual.

## Safe Snowflake path

1. Use an explicitly authorized Snowflake session.
2. Confirm the Task Graph owner role before applying account-level task privileges.
3. Deploy core SQL while the root remains suspended.
4. Apply object-scoped access grants and confirmed owner grants under the documented administrative roles.
5. Run deployment inspection and SQL policy assertions in a non-production environment.
6. Review notification configuration, resume explicitly, and run a manual smoke execution.
7. Inspect persisted run, module, finding, report, and delivery evidence before relying on the schedule.

Do not infer live success from local tests. They verify repository contracts and deployment boundaries, not target-account privileges or runtime behavior.
