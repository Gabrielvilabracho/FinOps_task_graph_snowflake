select *
from {{ ref('int_finops_query_performance_periods') }}
where period_type = 'WEEK'
