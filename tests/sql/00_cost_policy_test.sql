-- Run after deployment in a non-production Snowflake environment.
-- The assertions exercise the public cost-policy function directly.

EXECUTE IMMEDIATE $$
BEGIN
  ASSERT (
    FINOPS_DEV.FINOPS.FINOPS_CLASSIFY_COST(20, 18):status::STRING = 'NORMAL'
  ), 'Expected usage below both thresholds to be NORMAL';

  ASSERT (
    FINOPS_DEV.FINOPS.FINOPS_CLASSIFY_COST(25.01, 25):status::STRING = 'ATTENTION'
  ), 'Expected usage above 25 credits to require attention';

  ASSERT (
    FINOPS_DEV.FINOPS.FINOPS_CLASSIFY_COST(13.01, 10):status::STRING = 'ATTENTION'
  ), 'Expected growth above 30 percent to require attention';

  ASSERT (
    FINOPS_DEV.FINOPS.FINOPS_CLASSIFY_COST(10, NULL):status::STRING = 'NORMAL'
  ), 'Expected a missing baseline to avoid a fabricated growth alert';

  ASSERT (
    FINOPS_DEV.FINOPS.FINOPS_CLASSIFY_COST(13, 10):status::STRING = 'NORMAL'
  ), 'Expected the exact 30 percent boundary to remain NORMAL';
END;
$$;
