select
    analysis_date,
    warehouse_id,
    count(*) as duplicate_rows
from {{ ref('finops_warehouse_utilization_daily') }}
group by 1, 2
having count(*) > 1
