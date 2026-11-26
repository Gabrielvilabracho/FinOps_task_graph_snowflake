with queries as (

    select *
    from {{ ref('int_finops_query_history') }}

),

source_state as (

    select
        min(analysis_date) as source_first_analysis_date,
        max(end_time) as source_watermark
    from queries

),

periodized as (

    select
        'WEEK' as period_type,
        dateadd(day, 1 - dayofweekiso(analysis_date), analysis_date)
            as period_start_date,
        queries.* exclude analysis_date
    from queries

    union all

    select
        'MONTH' as period_type,
        to_date(date_trunc('month', analysis_date)) as period_start_date,
        queries.* exclude analysis_date
    from queries

),

aggregated as (

    select
        period_type,
        period_start_date,
        coalesce(to_varchar(warehouse_id), 'NO_WAREHOUSE') as warehouse_key,
        warehouse_id,
        max_by(warehouse_name, end_time) as warehouse_name,
        query_type,
        count(*) as query_count,
        count_if(is_client_generated_statement) as client_generated_query_count,
        count_if(not coalesce(is_client_generated_statement, false)) as user_query_count,
        count_if(coalesce(upper(execution_status), 'UNKNOWN') <> 'SUCCESS')
            as unsuccessful_query_count,
        sum(total_elapsed_time_ms) as total_elapsed_time_ms,
        avg(total_elapsed_time_ms) as average_elapsed_time_ms,
        percentile_cont(0.50) within group (order by total_elapsed_time_ms)
            as p50_elapsed_time_ms,
        percentile_cont(0.90) within group (order by total_elapsed_time_ms)
            as p90_elapsed_time_ms,
        percentile_cont(0.99) within group (order by total_elapsed_time_ms)
            as p99_elapsed_time_ms,
        sum(coalesce(queued_provisioning_time_ms, 0)
            + coalesce(queued_repair_time_ms, 0)
            + coalesce(queued_overload_time_ms, 0)
            + coalesce(transaction_blocked_time_ms, 0)) as total_queue_time_ms,
        count_if(total_elapsed_time_ms <= 1000) as queries_le_1_second,
        count_if(total_elapsed_time_ms > 1000
            and total_elapsed_time_ms <= 5000) as queries_1_to_5_seconds,
        count_if(total_elapsed_time_ms > 5000
            and total_elapsed_time_ms <= 30000) as queries_5_to_30_seconds,
        count_if(total_elapsed_time_ms > 30000
            and total_elapsed_time_ms <= 60000) as queries_30_to_60_seconds,
        count_if(total_elapsed_time_ms > 60000
            and total_elapsed_time_ms <= 300000) as queries_1_to_5_minutes,
        count_if(total_elapsed_time_ms > 300000) as queries_gt_5_minutes,
        count(*) as source_rows
    from periodized
    group by 1, 2, 3, 4, 6

),

publication as (

    select
        aggregated.*,
        case
            when period_type = 'WEEK' then dateadd(day, 7, period_start_date)
            else dateadd(month, 1, period_start_date)
        end as period_end_date,
        source_state.source_first_analysis_date,
        source_state.source_watermark
    from aggregated
    cross join source_state

),

final as (

    select
        publication.*,
        dateadd(minute, 45, to_timestamp_tz(
            to_char(period_end_date, 'YYYY-MM-DD') || ' 00:00:00 +00:00'))
            as expected_complete_at,
        coalesce(
            source_first_analysis_date <= period_start_date
                and current_timestamp() >= dateadd(minute, 45, to_timestamp_tz(
                    to_char(period_end_date, 'YYYY-MM-DD') || ' 00:00:00 +00:00'))
                and source_watermark >= to_timestamp_tz(
                    to_char(period_end_date, 'YYYY-MM-DD') || ' 00:00:00 +00:00'),
            false
        ) as is_source_complete
    from publication

)

select * from final
