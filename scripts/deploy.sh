#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <snowflake-connection-name>" >&2
  exit 2
fi

connection="$1"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

files=(
  "sql/00_setup/01_finops_objects.sql"
  "sql/10_core/10_finops_cost_policy.sql"
  "sql/10_core/11_finops_status_precedence.sql"
  "sql/20_procedures/20_finops_run_lifecycle.sql"
  "sql/20_procedures/21_finops_check_cost.sql"
  "sql/20_procedures/22_finops_check_errors.sql"
  "sql/20_procedures/23_finops_check_warehouse.sql"
  "sql/20_procedures/24_finops_check_queries.sql"
  "sql/20_procedures/25_finops_check_ai.sql"
  "sql/20_procedures/26_finops_check_other_costs.sql"
  "sql/20_procedures/27_finops_report.sql"
  "sql/20_procedures/28_finops_alert.sql"
  "sql/20_procedures/29_finops_finalizer.sql"
  "sql/30_tasks/30_finops_task_graph.sql"
  "sql/90_validation/90_validate_deployment.sql"
)

for file in "${files[@]}"; do
  snow sql --connection "$connection" --filename "$repo_root/$file"
done

cat <<'EOF'
Core objects are deployed with the graph suspended.
Administrative grants and graph resume remain explicit manual steps:
  sql/00_setup/02_finops_grants.sql
  sql/00_setup/03_finops_task_owner_grants.template.sql (template; requires confirmed owner)
  sql/30_tasks/31_resume_finops_task_graph.sql
EOF
