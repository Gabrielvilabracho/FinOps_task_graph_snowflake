USE DATABASE FINOPS_DEV;
USE SCHEMA FINOPS;

-- Suspending the root prevents future scheduled graph runs.
-- Already-running child tasks can finish using the captured graph version.
ALTER TASK FINOPS_ROOT_TASK SUSPEND;
