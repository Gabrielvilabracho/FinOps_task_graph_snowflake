---
type: testing
title: Testing and Verification
description: Local contract tests, mocked deployment checks, Snowflake-side validation, and the remaining live-integration evidence gap.
tags: [testing, verification, snowflake, contracts]
verified:
  - by: openwiki/0.9.0
    at: 2026-11-15T23:16:32.229Z
sources:
  - id: openwiki-source-b8325a9b65c05ee9a2638982
    resource: repo://sql/90_validation/90_validate_deployment.sql
  - id: openwiki-source-60d2c254172ab184137fc60a
    resource: repo://tests/sql/00_cost_policy_test.sql
  - id: openwiki-source-6d002d3a454526a6cfa48721
    resource: repo://tests/test_deploy_script.py
  - id: openwiki-source-1b7ab3f3796385286d32910e
    resource: repo://tests/test_finops_grants_security.py
  - id: openwiki-source-1bb3862e57a34c739599e099
    resource: repo://tests/test_repository_contract.py
generated: { by: "opencode", at: "2026-11-15T23:16:32.229Z" }
---

# Testing and Verification

Verification is layered because local tests can prove repository contracts but cannot prove effective privileges, Account Usage availability, task execution, or notification behavior inside a Snowflake account.

## Local test suite

Run all deterministic repository tests with:

```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

The suite verifies:

- required repository and SQL artifacts exist;
- the cost function contains only the approved `25` credit and `30%` growth thresholds;
- non-cost modules record rule gaps instead of hardcoding alert limits;
- the graph is serverless, daily, non-overlapping, and acyclic by contract;
- report, alert, and finalizer dependencies are present;
- no external orchestrator is introduced into runtime SQL;
- grant SQL cannot give the read/monitor role unconfirmed runtime privileges or blanket shared-schema access;
- the parent-database grant occurs under `SECURITYADMIN` before managed-schema grants under `SYSADMIN`;
- the deployment helper invokes core SQL in the expected order while grants and activation remain manual.

`bash -n scripts/deploy.sh` and `git diff --check` provide additional shell-syntax and whitespace checks.

## Mocked deployment probe

`tests/test_deploy_script.py` replaces the `snow` executable with a temporary recorder. It checks the public shell entrypoint without contacting Snowflake, compares every submitted file against the expected dependency order, and confirms that the output still directs operators to manual grant and resume steps.

This proves ordering and activation boundaries in the repository. It does not prove that any SQL statement is accepted by a live Snowflake account.

## Snowflake-side policy assertions

After deployment in a non-production Snowflake environment, run:

```text
tests/sql/00_cost_policy_test.sql
```

The script calls the public `FINOPS_CLASSIFY_COST` function and asserts below-threshold normal behavior, above-25 attention, above-30-percent attention, missing-baseline normal behavior, and exact-boundary normal behavior.

## Deployment inspection

`sql/90_validation/90_validate_deployment.sql` lists FinOps tables, views, functions, procedures, and tasks. It then inspects the ten expected task names from the immediately preceding `SHOW TASKS` result, evaluates policy boundaries, displays configuration, and reads recent run evidence.

`tests/sql/01_graph_contract_test.sql` provides a smaller task inventory query plus the documented manual smoke-run command.

These queries are inspection aids: the current task inventory query displays matching rows but does not fail automatically if one task is absent or has an unexpected predecessor. Operators must compare the observed rows with the documented graph before resume.

## Evidence required for live closure

An authorized Snowflake session must still prove:

1. All SQL compiles and creates objects in `DATALAB.SPAIN`.
2. The confirmed task owner has effective serverless execution and Account Usage privileges.
3. The read/monitor role sees only the intended FinOps objects and tasks.
4. A manual `FINOPS_ROOT_TASK ... AWAIT` run creates six module outcomes and a final report.
5. Child failure reaches the finalizer and produces durable failed-module evidence.
6. Alert-disabled, alert-success, and alert-failure paths record accurate delivery status.
7. The resumed graph fires at `10:00 UTC` without overlap.

Until those probes run, live deployment and runtime behavior remain **unverified**, even though local checks pass.

## Related pages

- [Task Graph Architecture](../architecture/task-graph.md)
- [State and Cost Policy](../concepts/state-and-cost-policy.md)
- [Deployment and Access](../operations/deployment-and-access.md)
