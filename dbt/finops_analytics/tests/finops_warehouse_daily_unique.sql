select
    analysis_date,
    warehouse_id,
    count(*) as row_count
from {{ ref('finops_warehouse_daily') }}
group by 1, 2
having count(*) > 1
