select *
from {{ ref('int_finops_query_history') }}
where total_elapsed_time_ms < 0
    or compilation_time_ms < 0
    or execution_time_ms < 0
    or queued_provisioning_time_ms < 0
    or queued_repair_time_ms < 0
    or queued_overload_time_ms < 0
    or transaction_blocked_time_ms < 0
    or query_retry_time_ms < 0
    or fault_handling_time_ms < 0
