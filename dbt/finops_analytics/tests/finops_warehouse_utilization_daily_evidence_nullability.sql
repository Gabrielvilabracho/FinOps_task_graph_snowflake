select *
from {{ ref('finops_warehouse_utilization_daily') }}
where (idle_evidence_state in (
        'INSUFFICIENT_EVENT_BOUNDARY',
        'INSUFFICIENT_LOAD_COVERAGE'
    ) and estimated_idle_seconds is not null)
    or (idle_evidence_state = 'ESTIMATED_FROM_EVENT_AND_LOAD'
        and estimated_idle_seconds is null)
