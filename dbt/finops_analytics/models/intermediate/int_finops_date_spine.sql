select
    dateadd(day, -seq4() - 1, current_date())::date as analysis_date
from table(generator(rowcount => 365))
