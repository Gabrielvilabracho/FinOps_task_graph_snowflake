select *
from {{ ref('finops_warehouse_utilization_daily') }}
where event_bounded_on_seconds < 0
    or active_observed_interval_seconds < 0
    or running_query_seconds < 0
    or queued_load_seconds < 0
    or queued_provisioning_seconds < 0
    or blocked_query_seconds < 0
    or estimated_idle_seconds < 0
