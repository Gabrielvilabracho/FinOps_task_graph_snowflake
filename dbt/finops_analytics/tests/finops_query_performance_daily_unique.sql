select
    analysis_date,
    warehouse_key,
    query_type,
    count(*) as duplicate_rows
from {{ ref('finops_query_performance_daily') }}
group by 1, 2, 3
having count(*) > 1
