USE DATABASE FINOPS_DEV;
USE SCHEMA FINOPS;

BEGIN TRANSACTION;

CALL SP_FINOPS_BEGIN_RUN(
  'metric-completeness-invariant-test',
  CURRENT_DATE(),
  CURRENT_TIMESTAMP()
);

CALL SP_FINOPS_RECORD_METRIC(
  'metric-completeness-invariant-test',
  'COST',
  'CONTRADICTORY_INCOMPLETE_METRIC',
  'NORMAL',
  NULL, NULL, NULL, NULL, NULL, NULL, NULL,
  'credits',
  ARRAY_CONSTRUCT(),
  'The source has not published the requested window.',
  'Rerun after the source is expected to be complete.',
  'SNOWFLAKE.ACCOUNT_USAGE.METERING_HISTORY',
  DATEADD(DAY, -1, CURRENT_DATE())::TIMESTAMP_LTZ,
  CURRENT_DATE()::TIMESTAMP_LTZ,
  0,
  NULL,
  DATEADD(HOUR, 3, CURRENT_DATE()::TIMESTAMP_LTZ),
  FALSE,
  'SOURCE_PUBLICATION_ABSENT'
);

CALL SP_FINOPS_COMPLETE_MODULE_FROM_METRICS(
  'metric-completeness-invariant-test',
  'COST',
  OBJECT_CONSTRUCT('source', 'invariant-test')
);

SELECT SYSTEM$ASSERT_EQUALS(
  'DATA_INCOMPLETE',
  (SELECT STATUS
   FROM FINOPS_METRIC
   WHERE RUN_ID = 'metric-completeness-invariant-test'
     AND MODULE_NAME = 'COST'
     AND METRIC_KEY = 'CONTRADICTORY_INCOMPLETE_METRIC'),
  'The public metric API must normalize incomplete NORMAL input.'
);

SELECT SYSTEM$ASSERT_EQUALS(
  'DATA_INCOMPLETE',
  (SELECT STATUS
   FROM FINOPS_MODULE_RUN
   WHERE RUN_ID = 'metric-completeness-invariant-test'
     AND MODULE_NAME = 'COST'),
  'Metric-to-module folding must retain DATA_INCOMPLETE.'
);

ROLLBACK;
