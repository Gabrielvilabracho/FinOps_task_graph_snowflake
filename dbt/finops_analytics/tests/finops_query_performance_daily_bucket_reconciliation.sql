select *
from {{ ref('finops_query_performance_daily') }}
where queries_le_1_second
    + queries_1_to_5_seconds
    + queries_5_to_30_seconds
    + queries_30_to_60_seconds
    + queries_1_to_5_minutes
    + queries_gt_5_minutes
    <> query_count
