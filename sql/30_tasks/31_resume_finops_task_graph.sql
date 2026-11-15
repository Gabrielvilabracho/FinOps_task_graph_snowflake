USE DATABASE DATALAB;
USE SCHEMA SPAIN;

-- Finalizers are associated with, but are not ordinary descendants of, the root.
ALTER TASK FINOPS_FINALIZER RESUME;
SELECT SYSTEM$TASK_DEPENDENTS_ENABLE('DATALAB.SPAIN.FINOPS_ROOT_TASK');

-- Confirm the graph state before relying on the schedule.
SHOW TASKS IN SCHEMA DATALAB.SPAIN;
