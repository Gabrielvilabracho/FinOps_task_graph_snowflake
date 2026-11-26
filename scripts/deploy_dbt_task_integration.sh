#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <snowflake-connection-name>" >&2
  exit 2
fi

connection="$1"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

snow dbt deploy FINOPS_DEV.FINOPS.FINOPS_DBT_PROJECT \
  --connection "$connection" \
  --database FINOPS_DEV \
  --schema FINOPS \
  --role FINOPS_DBT_ROLE \
  --warehouse FINOPS_DBT_WAREHOUSE \
  --secondary-roles NONE \
  --client-store-temporary-credential \
  --oauth-enable-refresh-tokens \
  --server-session-keep-alive \
  --source "$repo_root/dbt/finops_analytics" \
  --default-target prod \
  --default-env prod \
  --dbt-version 1.9.4 \
  --no-force \
  --no-auto-compile

snow sql \
  --connection "$connection" \
  --database FINOPS_DEV \
  --schema FINOPS \
  --role FINOPS_DBT_ROLE \
  --secondary-roles NONE \
  --client-store-temporary-credential \
  --oauth-enable-refresh-tokens \
  --server-session-keep-alive \
  --filename "$repo_root/sql/20_procedures/30_finops_dbt_analytics.sql"

snow sql \
  --connection "$connection" \
  --database FINOPS_DEV \
  --schema FINOPS \
  --role FINOPS_TASK_OWNER \
  --secondary-roles NONE \
  --client-store-temporary-credential \
  --oauth-enable-refresh-tokens \
  --server-session-keep-alive \
  --filename "$repo_root/sql/30_tasks/33_integrate_finops_dbt_analytics.sql" \
  --filename "$repo_root/sql/90_validation/91_validate_dbt_task_integration.sql"

cat <<'EOF'
The native dbt node is installed and the full graph remains suspended.
Activation remains a separate explicit operation:
  sql/30_tasks/31_resume_finops_task_graph.sql
Rollback remains available while suspended:
  sql/30_tasks/34_remove_finops_dbt_analytics.sql
EOF
