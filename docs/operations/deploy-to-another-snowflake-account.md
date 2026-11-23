# Deploy FinOps to another Snowflake account

Use this guide to prepare an independent installation of this repository in a different Snowflake account. It identifies the values and files to review before deploying; it does not migrate the original account's data, users, grants, integrations, or execution history.

**You can keep `FINOPS_DEV.FINOPS` and the FinOps object names.** Separate accounts have separate namespaces. The minimum changes are the destination connection, approved user assignments, and warehouse selection. Email, native dbt, consumer access, and Snowflake-hosted Git synchronization require additional configuration only when used.

> Scope: documentation prepared on 2026-11-23 from the current working tree. No connection to the other account was opened. Replace every `<PLACEHOLDER>` before executing an example. Commands below create or change destination objects and require separate operational authorization.

## 1. Preserve the corrected source before copying or cloning

The native runtime fixes are published in [PR #17](https://github.com/Gabrielvilabracho/FinOps_task_graph_snowflake/pull/17), commit `c9a65f3`. The destination checkout must include that repair or an equivalent later version. Older branches and tags may lack the corrected procedures and native regression tests.

Review the local changes before preparing the destination copy:

```bash
git status --short
git diff --stat
```

Carry the reviewed changes in `sql/20_procedures/20_finops_run_lifecycle.sql` through `sql/20_procedures/28_finops_alert.sql`, the updated `tests/test_evidence_semantics.py`, and these new files:

- `tests/test_native_runtime_contract.py`
- `tests/sql/05_native_runtime_regression_test.sql`
- `tests/sql/06_collectors_real_source_smoke_test.sql`
- `docs/operations/native-runtime-validation.md`
- This guide.

Select a reviewed revision before using a clone or another controlled source-transfer method. Do not transfer local authentication files, tokens, private keys, browser sessions, or unrelated untracked artifacts. Do not deploy an older checkout just because it has the same branch name.

## 2. Destination configuration worksheet

Fill in the destination column privately. Names shown here are identifiers, not credentials.

| Setting | Repository/current convention | Destination decision |
| --- | --- | --- |
| CLI connection | `finops` was used for the original account | Create a distinct name, such as `finops_other`; do not overwrite the original connection |
| Account identifier | Not hardcoded into application SQL | `<DESTINATION_ACCOUNT_IDENTIFIER>` |
| Login user | Account-specific | `<DESTINATION_USER>`; must already exist or be provisioned by an administrator |
| Authentication | Original account used `OAUTH_AUTHORIZATION_CODE` | Method approved for the destination account; do not assume the same identity-provider setup |
| Database / operational schema | `FINOPS_DEV` / `FINOPS` | Keep these names for the lowest-change path, or apply all namespace changes in section 4 |
| Operational owner/deployer | `FINOPS_TASK_OWNER` | Usually keep; administrator assigns it to the destination user |
| CLI/validation warehouse | `COMPUTE_WH` | An approved existing warehouse; bootstrap grants usage but does not create this warehouse |
| Native dbt owner | `FINOPS_DBT_ROLE` | Needed only for dbt; usually keep |
| Native dbt warehouse | `FINOPS_DBT_WAREHOUSE` | Dedicated warehouse created by the dbt bootstrap; review size and cost controls |
| Native dbt object | `FINOPS_DEV.FINOPS.FINOPS_DBT_PROJECT` | Usually keep; created/deployed separately from the operational graph |
| Consumer role | An environment-specific role appears in `02_finops_grants.sql` | Replace with an approved destination role, or omit the optional consumer grants |
| Email integration / recipients | Seeded as null, with delivery disabled | Configure and approve in the destination; never copy the original recipient list blindly |
| Root schedule | `USING CRON 0 12 * * * UTC` | Keep unless another schedule is explicitly approved |
| Cost policy | Strictly greater than 25 credits or 30% growth | Review against destination policy; these are not universal account limits |

Authentication must be configured outside this repository using the destination's approved process. Do not put passwords, OAuth client secrets, access/refresh tokens, or private keys into SQL, dbt YAML, Markdown, or Git.

## 3. Files that require review even when names stay the same

All paths below are relative to the repository root.

| File | What to change or verify |
| --- | --- |
| `sql/00_setup/03_finops_task_owner_grants.sql` | Replace the existing quoted personal user in `GRANT ROLE ... TO USER` with `<DESTINATION_USER>`. Confirm `COMPUTE_WH`, or change that grant to the approved warehouse. Review the administrative role and account-level execution privileges before running. |
| `scripts/deploy.sh` | Invoke with the destination connection. It consumes only the connection argument and hardcodes database `FINOPS_DEV`, schema `FINOPS`, and role `FINOPS_TASK_OWNER`. It does not accept separate database/schema arguments. |
| `sql/00_setup/02_finops_grants.sql` | Optional. Replace the account-specific consumer role; the script does not create that role. Verify grant authority rather than assuming the destination has the same role hierarchy. |
| `sql/00_setup/04_finops_dbt_bootstrap.sql` | Optional dbt setup. Replace its existing quoted personal user assignment too. Review warehouse creation, imported access to `SNOWFLAKE`, destination schema grants, and consumer grants. |
| `dbt/finops_analytics/dbt_projects_profiles.yml` | Optional dbt. Supply the six `DBT_` execution variables listed in section 6. No credentials belong in this profile. |
| `sql/00_setup/01_finops_objects.sql` | Review configuration defaults. On a clean installation, email starts disabled. Its seed `MERGE` inserts missing keys only; changing seed text does not overwrite existing configuration. |
| `sql/30_tasks/30_finops_task_graph.sql` | Review noon UTC scheduling, previous-complete-UTC-day analysis, and no-overlap policy. The graph uses serverless tasks, not the dbt warehouse. |
| `sql/90_validation/90_validate_deployment.sql` | Expects ten named tasks, all suspended, before activation. Its final queries include configuration and operational records; handle output privately. |

Do not replace system sources such as `SNOWFLAKE.ACCOUNT_USAGE` with `FINOPS_DEV`. They provide metadata for the account where the code executes. Review available views, source history, feature availability, and privileges in that destination.

### Bootstrap privilege boundary

`03_finops_task_owner_grants.sql` currently selects `ACCOUNTADMIN` for one-time setup. Its operational grants include:

- Usage on the selected warehouse, database, and schema.
- Create privileges for tables, views, functions, procedures, and tasks in the operational schema.
- Account-level `EXECUTE TASK` and `EXECUTE MANAGED TASK`.
- Database roles `SNOWFLAKE.USAGE_VIEWER` and `SNOWFLAKE.GOVERNANCE_VIEWER`.

An authorized administrator must review and apply this baseline under destination policy. Do not use `ACCOUNTADMIN` for routine deployment or add unrelated grants to bypass an error. The deploy helper explicitly selects `FINOPS_TASK_OWNER` and disables secondary roles so task ownership stays consistent.

## 4. Additional changes only if you rename database, schema, or roles

Changing accounts alone does **not** require these renames. If you choose different names, review the following as one coordinated change:

| Area | Files / references to update |
| --- | --- |
| Deployment helper | Hardcoded `database`, `schema`, and `role` values in `scripts/deploy.sh` |
| Setup | Contexts, qualified names, and grant targets in `sql/00_setup/01_finops_objects.sql`, `02_finops_grants.sql`, `03_finops_task_owner_grants.sql`, and optional `04_finops_dbt_bootstrap.sql` |
| Core functions | `USE DATABASE` / `USE SCHEMA` in `sql/10_core/10_finops_cost_policy.sql` and `11_finops_status_precedence.sql` |
| Procedures | Contexts in all `sql/20_procedures/*.sql`, including `29_finops_finalizer.sql` |
| Graph lifecycle | Contexts and fully qualified task references in `sql/30_tasks/30_finops_task_graph.sql`, `31_resume_finops_task_graph.sql`, and `32_suspend_finops_task_graph.sql` |
| Validation | Contexts, qualified schemas, and functions in `sql/90_validation/90_validate_deployment.sql` and `tests/sql/*.sql` |
| dbt | Database/schema defaults and execution role/warehouse variables in `dbt/finops_analytics/dbt_projects_profiles.yml`; custom schema suffixes in `dbt/finops_analytics/dbt_project.yml` if intentionally changed |
| Python contracts | Destination-specific expectations in `tests/test_finops_dev_deployment.py`, `test_deploy_script.py`, `test_finops_grants_security.py`, and `test_dbt_finops_contract.py` |
| Operator documentation | Active command examples in the README and operations guides |

The deployment tests also assert an existing personal user assignment. Update those account-specific expectations when adapting the bootstrap user; do not disable the tests to hide a mismatch.

**CLI `--database` and `--schema` flags do not override later `USE DATABASE` / `USE SCHEMA` statements inside SQL files.** Changing only connection settings can therefore deploy into the wrong namespace within the selected account.

Avoid a blind repository-wide replacement: historical notes, research, and generated `openwiki/` pages are not live deployment configuration. Do not hand-edit generated OpenWiki artifacts as part of retargeting.

## 5. Clean-install sequence with the existing names

The examples in this section use `finops_other`, `FINOPS_DEV.FINOPS`, and `FINOPS_TASK_OWNER`. Run shell commands from the repository root. If the destination already contains FinOps objects or active tasks, stop and plan an update instead: the deploy helper replaces functions, procedures, and tasks and is not a data-migration tool.

### A. Configure and confirm the destination connection

Configure it interactively, outside source control:

```bash
snow connection add
snow connection test --connection finops_other
snow sql --connection finops_other --query \
  'SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE();'
```

Use an existing destination role for this initial check. Do not set connection defaults to a role, database, or schema that has not been created yet. Confirm the account identifier before any write, and keep using the explicit connection name rather than changing the global default.

If a configuration file is used, `config.toml` uses `[connections.finops_other]`, whereas shared `connections.toml` uses `[finops_other]`. When both files exist, Snowflake CLI reads connections from `connections.toml`. Choose authentication appropriate to the destination; Google/OIDC OAuth and SAML `EXTERNALBROWSER` are not interchangeable assumptions.

### B. Apply the reviewed administrative bootstrap

First ensure the selected user and warehouse exist. After editing the user/warehouse values in `03_finops_task_owner_grants.sql`, an authorized administrator runs:

```bash
snow sql --connection finops_other --role ACCOUNTADMIN \
  --secondary-roles NONE \
  --filename sql/00_setup/03_finops_task_owner_grants.sql
```

The script creates the database, schema, owner role, and grants. If destination policy requires delegated administration, the administrator must adapt the script, including its embedded `USE ROLE`, rather than relying only on the command-line role flag.

### C. Deploy the operational objects, leaving tasks suspended

```bash
bash scripts/deploy.sh finops_other
```

The helper executes these groups in order in one SQL session:

1. `sql/00_setup/01_finops_objects.sql`.
2. `sql/10_core/10_finops_cost_policy.sql`, then `11_finops_status_precedence.sql`.
3. `sql/20_procedures/20_finops_run_lifecycle.sql`, then the six collectors `21` through `26`, report `27`, alert `28`, and finalizer `29`.
4. `sql/30_tasks/30_finops_task_graph.sql`.
5. `sql/90_validation/90_validate_deployment.sql`.

It does **not** provision the selected warehouse or login user, run administrative bootstrap/consumer grants, configure email or Git integrations, deploy dbt, run native regression probes, or activate tasks. Bootstrap must happen **before** this first deployment, even though the helper's final message lists it as a manual step.

### D. Validate before enabling delivery or scheduling

Run local contracts from a canonical repository path, then the native probes in the authorized destination validation environment:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
bash -n scripts/deploy.sh

snow sql --connection finops_other --database FINOPS_DEV --schema FINOPS \
  --role FINOPS_TASK_OWNER --secondary-roles NONE \
  --filename tests/sql/05_native_runtime_regression_test.sql \
  --filename tests/sql/06_collectors_real_source_smoke_test.sql
```

Both native probes use unique run IDs and roll back their fixtures on success or failure. The first temporarily supplies an invalid alert boolean inside its transaction to test failure logging **before sending**, then rolls it back. The second reads real Account Usage sources and checks six collectors, seven metrics, and a report. Neither sends email or executes the graph/finalizer. Source queries and validation still consume compute.

Confirm ten suspended tasks under one owner and no unexpected tasks. A successful test in the original account is not proof of source access or feature support in the new account. See [native runtime validation](native-runtime-validation.md) for the checks and failure boundaries.

### E. Activate only after explicit approval

Only after validation, policy review, and the email decision:

```bash
snow sql --connection finops_other --database FINOPS_DEV --schema FINOPS \
  --role FINOPS_TASK_OWNER --secondary-roles NONE \
  --filename sql/30_tasks/31_resume_finops_task_graph.sql
```

This enables ongoing execution and serverless compute consumption. The script explicitly resumes the finalizer as well as enabling the dependent graph. Check `SHOW TASKS` afterward and confirm the root's `USING CRON 0 12 * * * UTC` schedule. Noon UTC is not necessarily noon in your local timezone; the analysis window remains the previous complete UTC day.

To stop future scheduling, `sql/30_tasks/32_suspend_finops_task_graph.sql` suspends the root. Already-running children can continue. Confirm no `EXECUTING` graph remains before changing procedures; do not drop objects or cancel queries as an automatic recovery step.

## 6. Optional: deploy the native dbt project

The operational Task Graph and dbt are separate. dbt is not automatically invoked by the current serverless graph and needs a user-managed warehouse.

1. Review `sql/00_setup/04_finops_dbt_bootstrap.sql`, replace its user assignment, and have an authorized administrator apply it after the operational database/schema exist.
2. Confirm `FINOPS_DBT_ROLE` and `FINOPS_DBT_WAREHOUSE`. The bootstrap's warehouse baseline is X-SMALL, auto-suspend after 60 seconds, initially suspended; execution can auto-resume it and incur costs.
3. Confirm a supported native dbt version in the destination. The original deployment used dbt Core `1.9.4` and adapter `1.9.2`; those observations are not a guarantee for another account. Replace the version placeholder below with an available compatible version.

```bash
snow dbt deploy FINOPS_DEV.FINOPS.FINOPS_DBT_PROJECT \
  --connection finops_other --database FINOPS_DEV --schema FINOPS \
  --role FINOPS_DBT_ROLE --warehouse FINOPS_DBT_WAREHOUSE \
  --secondary-roles NONE --source dbt/finops_analytics \
  --default-target prod --dbt-version '<SUPPORTED_DBT_VERSION>' \
  --no-force --no-auto-compile
```

Do not use `--force` for ordinary updates: it recreates the object and can remove project versions/run history. Uploading files is not the same as rebuilding the materialized marts.

The native profile requires these execution variables:

| Variable | Value |
| --- | --- |
| `DBT_SNOWFLAKE_ACCOUNT` | Destination account identifier |
| `DBT_SNOWFLAKE_USER` | Approved user executing the project |
| `DBT_FINOPS_DBT_ROLE` | `FINOPS_DBT_ROLE`, or your coordinated replacement |
| `DBT_FINOPS_DBT_WAREHOUSE` | `FINOPS_DBT_WAREHOUSE`, or your approved replacement |
| `DBT_FINOPS_DBT_DATABASE` | `FINOPS_DEV`, unless retargeted |
| `DBT_FINOPS_DBT_SCHEMA` | `FINOPS`, unless retargeted |

To build the selected marts, run the following in **one SQL session** connected to the destination. This is SQL for a worksheet or a separately prepared SQL file, not shell commands:

```sql
USE ROLE FINOPS_DBT_ROLE;
USE SECONDARY ROLES NONE;
USE WAREHOUSE FINOPS_DBT_WAREHOUSE;
USE DATABASE FINOPS_DEV;
USE SCHEMA FINOPS;
ALTER SESSION SET TIMEZONE = 'UTC';

SET FINOPS_DBT_ACCOUNT = CURRENT_ACCOUNT();
SET FINOPS_DBT_USER = CURRENT_USER();

EXECUTE DBT PROJECT FINOPS_DEV.FINOPS.FINOPS_DBT_PROJECT
  ARGS = 'build --select +finops_daily_cost +finops_warehouse_daily --quiet --warn-error'
  ENV_VARS = (
    'DBT_SNOWFLAKE_ACCOUNT' = $FINOPS_DBT_ACCOUNT,
    'DBT_SNOWFLAKE_USER' = $FINOPS_DBT_USER,
    'DBT_FINOPS_DBT_ROLE' = 'FINOPS_DBT_ROLE',
    'DBT_FINOPS_DBT_WAREHOUSE' = 'FINOPS_DBT_WAREHOUSE',
    'DBT_FINOPS_DBT_DATABASE' = 'FINOPS_DEV',
    'DBT_FINOPS_DBT_SCHEMA' = 'FINOPS'
  );
```

Check the returned `SUCCESS` value and any exception. The session-variable form worked in the original account; direct function expressions inside `ENV_VARS` did not. Destination support must still be validated. `ENV_VARS` values appear in query text/history: use only non-secret identifiers here, never credentials. The existing native profile is not a complete authenticated local dbt Core profile.

With the existing dbt schema configuration, relations resolve to:

- `FINOPS_DEV.FINOPS_FINOPS_STAGING`
- `FINOPS_DEV.FINOPS_FINOPS_INTERMEDIATE`
- `FINOPS_DEV.FINOPS_FINOPS_ANALYTICS`

These names combine the target schema `FINOPS` with custom suffixes from `dbt_project.yml`; changing the target schema changes the generated names and required grants. Recheck source timezone assumptions in the destination; setting the caller session alone is not evidence of every internal adapter session's timezone. See [dbt operations](dbt-finops-analytics.md).

## 7. Optional integrations and policy configuration

### Email

Leave email disabled until separately approved. The clean-install seed in `01_finops_objects.sql` creates these `FINOPS_CONFIG` keys:

| Module / key | Default | Destination action |
| --- | --- | --- |
| `ALERT / ENABLED` | `false` | Enable only after integration, recipients, and notification policy are approved |
| `ALERT / EMAIL_INTEGRATION` | null | Name of a separately created destination notification integration |
| `ALERT / RECIPIENTS` | null | Approved recipient list, verified in the destination account |
| `COST / DAILY_CREDIT_THRESHOLD` | `25` | Review the strict daily credit rule |
| `COST / GROWTH_RATIO_THRESHOLD` | `0.30` | Review the strict day-over-day growth rule |

An administrator must separately create/approve the notification integration and grant its usage to `FINOPS_TASK_OWNER`. Integration privileges and verified recipients do not transfer between accounts. Use the email configuration procedure in [the runbook](runbook.md); replace every example value.

For an existing installation, update the intended configuration rows explicitly; rerunning the seed will not change matched values. The operational collector reads thresholds from configuration, while the two-argument `FINOPS_CLASSIFY_COST` overload separately retains fixed defaults of 25 and 0.30. Changing configuration does not silently redefine that public function or its tests.

Do not call `SP_FINOPS_FINALIZE_RUN` as a supposedly report-only smoke: the finalizer also calls alert delivery. After activation, enabled notifications can be sent during normal scheduled runs.

### Git synchronization inside Snowflake

This is **not required** by `scripts/deploy.sh`, which deploys local files. If you choose Snowflake-hosted Git synchronization, create/review the destination API integration, Git repository object, repository schema, source URL/branch, and scoped synchronization role separately. The original account's integration/repository/grants are not portable configuration.

`FINOPS_REPO_OPERATOR` is for repository synchronization, not a substitute for `FINOPS_TASK_OWNER`. Repository fetch/synchronization does not deploy the SQL objects. Cortex CLI/tooling is optional as well; changing accounts alone does not require editing `.cortex/tooling.lock.json` or installing Cortex. See [Cortex tooling](cortex-tooling.md).

## 8. Expected results and remaining boundaries

On a clean installation, historical operational tables start empty. Transactional native probes leave no report behind. Reports appear after an explicitly authorized persisted validation run or scheduled graph execution; dbt marts require their separate build.

Do not expect the original account's row counts, credits, run IDs, findings, or reports in the destination. Account Usage history/publication and AI adoption can differ.

- `DATA_INCOMPLETE` can be an honest evidence state, not a deployment failure. AI history/publication can be absent.
- The optional financial collector currently can return `SOURCE_UNAVAILABLE`; the original deployment observed this fallback. Do not assume a larger grant is its proven fix or declare invoice reconciliation complete.
- The 48-hour financial margin remains a local reconciliation policy, not the source's publication-latency guarantee.
- Warehouse residual is not proven waste; credit representations overlap and must not be summed as separate expenses.
- Non-cost anomaly rules, ownership/allocation, currency/invoice reconciliation, and automatic remediation are not authorized by successful installation.

## 9. Destination readiness checklist

- [ ] Corrected source and native tests are present in the destination checkout.
- [ ] A distinct connection points to the intended account; identity was checked before writes.
- [ ] Both bootstrap user assignments were reviewed; the dbt assignment is needed only if dbt is used.
- [ ] Operational warehouse exists; its name and usage grant match the connection/script.
- [ ] Administrative privileges and any optional consumer role were reviewed.
- [ ] Namespace/role renames, if any, are consistent across scripts, SQL, dbt, and tests.
- [ ] Clean deployment validation reports exactly ten suspended tasks under the expected owner.
- [ ] Native regression and real-source smoke pass in the destination without sending email.
- [ ] dbt, if used, has a successful selected build and the expected generated schemas.
- [ ] Email is disabled or separately configured, verified, and approved.
- [ ] Activation and its compute/notification effects were explicitly approved.
- [ ] Started tasks, next scheduled UTC run, first report, and any delivery outcome were checked.

## References

- [Managing Snowflake CLI connections](https://docs.snowflake.com/en/developer-guide/snowflake-cli/connecting/configure-connections)
- [Snowflake CLI dbt deployment](https://docs.snowflake.com/en/developer-guide/snowflake-cli/command-reference/dbt-commands/deploy)
- [EXECUTE DBT PROJECT and execution variables](https://docs.snowflake.com/en/sql-reference/sql/execute-dbt-project)
- [Native runtime validation](native-runtime-validation.md)
- [Operational runbook](runbook.md)
- [dbt deployment and responsibility boundaries](dbt-finops-analytics.md)
