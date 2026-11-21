USE DATABASE FINOPS_DEV;
USE SCHEMA FINOPS;

-- Finalizers are associated with, but are not ordinary descendants of, the root.
ALTER TASK FINOPS_FINALIZER RESUME;
SELECT SYSTEM$TASK_DEPENDENTS_ENABLE('FINOPS_DEV.FINOPS.FINOPS_ROOT_TASK');

-- Confirm the graph state before relying on the schedule.
SHOW TASKS IN SCHEMA FINOPS_DEV.FINOPS;
