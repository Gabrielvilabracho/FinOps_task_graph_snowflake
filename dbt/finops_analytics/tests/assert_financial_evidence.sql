-- Provisional values are nullable by design; only mature observed rows require values.
select *
from {{ ref('finops_daily_cost') }}
where (is_source_complete and (
    raw_credits_used is null or billed_credits is null
    or cloud_services_adjustment_credits is null or evidence_reason is not null
)) or (not is_source_complete and (
    raw_credits_used is not null or billed_credits is not null or evidence_reason is null
))
