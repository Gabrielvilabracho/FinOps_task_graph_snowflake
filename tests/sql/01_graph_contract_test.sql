-- Run after deployment with a role that can inspect FINOPS_DEV.FINOPS tasks.

SHOW TASKS IN SCHEMA FINOPS_DEV.FINOPS;

SELECT
  "name",
  "state",
  "schedule",
  "predecessors"
FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
WHERE "name" IN (
  'FINOPS_ROOT_TASK',
  'FINOPS_CHECK_COST',
  'FINOPS_CHECK_ERRORS',
  'FINOPS_CHECK_WAREHOUSE',
  'FINOPS_CHECK_QUERIES',
  'FINOPS_CHECK_AI',
  'FINOPS_CHECK_OTHER_COSTS',
  'FINOPS_REPORT_TASK',
  'FINOPS_ALERT_TASK',
  'FINOPS_FINALIZER'
)
ORDER BY "name";

-- Manual smoke run after child tasks and the finalizer are resumed:
-- EXECUTE TASK FINOPS_DEV.FINOPS.FINOPS_ROOT_TASK AWAIT;
