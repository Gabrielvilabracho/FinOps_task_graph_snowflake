with date_spine as (

    select analysis_date
    from {{ ref('int_finops_date_spine') }}

),

credit_daily as (

    select *
    from {{ ref('finops_warehouse_daily') }}

),

load_history as (

    select *
    from {{ ref('stg_account_usage__warehouse_load_history') }}

),

state_intervals as (

    select *
    from {{ ref('int_finops_warehouse_state_intervals') }}

),

events as (

    select *
    from {{ ref('stg_account_usage__warehouse_events_history') }}

),

load_daily as (

    select
        to_date(convert_timezone('UTC', start_time)) as analysis_date,
        warehouse_id,
        max_by(warehouse_name, end_time) as warehouse_name,
        sum(datediff(second, start_time, end_time)) as observed_load_interval_seconds,
        sum(iff(coalesce(avg_running, 0) > 0,
            datediff(second, start_time, end_time), 0))
            as active_observed_interval_seconds,
        sum(coalesce(avg_running, 0) * datediff(second, start_time, end_time))
            as running_query_seconds,
        sum(coalesce(avg_queued_load, 0) * datediff(second, start_time, end_time))
            as queued_load_seconds,
        sum(coalesce(avg_queued_provisioning, 0) * datediff(second, start_time, end_time))
            as queued_provisioning_seconds,
        sum(coalesce(avg_blocked, 0) * datediff(second, start_time, end_time))
            as blocked_query_seconds,
        count(*) as load_interval_count
    from load_history
    group by 1, 2

),

state_daily as (

    select
        date_spine.analysis_date,
        state_intervals.warehouse_id,
        max_by(state_intervals.warehouse_name, state_intervals.estimated_on_end)
            as warehouse_name,
        sum(datediff(
            second,
            greatest(
                state_intervals.estimated_on_start,
                to_timestamp_tz(to_char(date_spine.analysis_date, 'YYYY-MM-DD')
                    || ' 00:00:00 +00:00')
            ),
            least(
                state_intervals.estimated_on_end,
                dateadd(day, 1, to_timestamp_tz(
                    to_char(date_spine.analysis_date, 'YYYY-MM-DD')
                    || ' 00:00:00 +00:00'))
            )
        )) as event_bounded_on_seconds
    from state_intervals
    inner join date_spine
        on state_intervals.estimated_on_start < dateadd(day, 1, to_timestamp_tz(
            to_char(date_spine.analysis_date, 'YYYY-MM-DD') || ' 00:00:00 +00:00'))
        and state_intervals.estimated_on_end > to_timestamp_tz(
            to_char(date_spine.analysis_date, 'YYYY-MM-DD') || ' 00:00:00 +00:00')
    group by 1, 2

),

event_daily as (

    select
        to_date(convert_timezone('UTC', event_timestamp)) as analysis_date,
        warehouse_id,
        max_by(warehouse_name, event_timestamp) as warehouse_name,
        count_if(upper(event_name) = 'RESUME_WAREHOUSE') as resume_event_count,
        count_if(upper(event_name) = 'SUSPEND_WAREHOUSE') as suspend_event_count
    from events
    group by 1, 2

),

warehouse_days as (

    select analysis_date, warehouse_id from credit_daily
    union
    select analysis_date, warehouse_id from load_daily
    union
    select analysis_date, warehouse_id from state_daily
    union
    select analysis_date, warehouse_id from event_daily

),

combined as (

    select
        warehouse_days.analysis_date,
        warehouse_days.warehouse_id,
        coalesce(
            load_daily.warehouse_name,
            event_daily.warehouse_name,
            state_daily.warehouse_name,
            credit_daily.warehouse_name
        ) as warehouse_name,
        credit_daily.raw_credits_used,
        credit_daily.compute_credits,
        credit_daily.query_attributed_compute_credits,
        credit_daily.compute_residual_credits,
        credit_daily.estimated_idle_credits,
        credit_daily.is_source_complete as is_credit_source_complete,
        load_daily.observed_load_interval_seconds,
        load_daily.active_observed_interval_seconds,
        load_daily.running_query_seconds,
        load_daily.queued_load_seconds,
        load_daily.queued_provisioning_seconds,
        load_daily.blocked_query_seconds,
        load_daily.load_interval_count,
        state_daily.event_bounded_on_seconds,
        event_daily.resume_event_count,
        event_daily.suspend_event_count,
        case
            when state_daily.event_bounded_on_seconds is null then null
            when load_daily.observed_load_interval_seconds is null
                or load_daily.observed_load_interval_seconds + 300
                    < state_daily.event_bounded_on_seconds then null
            else greatest(
                state_daily.event_bounded_on_seconds
                    - coalesce(load_daily.active_observed_interval_seconds, 0),
                0
            )
        end as estimated_idle_seconds,
        case
            when state_daily.event_bounded_on_seconds is null
                then 'INSUFFICIENT_EVENT_BOUNDARY'
            when load_daily.observed_load_interval_seconds is null
                or load_daily.observed_load_interval_seconds + 300
                    < state_daily.event_bounded_on_seconds
                then 'INSUFFICIENT_LOAD_COVERAGE'
            else 'ESTIMATED_FROM_EVENT_AND_LOAD'
        end as idle_evidence_state,
        dateadd(hour, 3, dateadd(day, 1, to_timestamp_tz(
            to_char(warehouse_days.analysis_date, 'YYYY-MM-DD')
            || ' 00:00:00 +00:00'))) as expected_complete_at
    from warehouse_days
    left join credit_daily using (analysis_date, warehouse_id)
    left join load_daily using (analysis_date, warehouse_id)
    left join state_daily using (analysis_date, warehouse_id)
    left join event_daily using (analysis_date, warehouse_id)

),

final as (

    select
        combined.*,
        current_timestamp() >= expected_complete_at as is_utilization_source_complete
    from combined

)

select * from final
