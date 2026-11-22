with metering as (

    select *
    from {{ ref('stg_account_usage__warehouse_metering_history') }}

),

source_state as (

    select max(end_time) as source_watermark
    from metering

),

daily as (

    select
        to_date(convert_timezone('UTC', start_time)) as analysis_date,
        warehouse_id,
        warehouse_name,
        sum(credits_used) as raw_credits_used,
        sum(credits_used_compute) as compute_credits,
        sum(credits_used_cloud_services) as cloud_services_credits,
        sum(credits_attributed_compute_queries) as query_attributed_compute_credits,
        count(*) as source_rows,
        count(case when credits_used is not null and credits_used_compute is not null
            then 1 end) as known_metering_rows,
        count(credits_attributed_compute_queries) as attribution_known_rows,
        case
            when count(credits_attributed_compute_queries) = count(*)
                and count(credits_used_compute) = count(*)
                then sum(credits_used_compute) - sum(credits_attributed_compute_queries)
        end as compute_residual_credits
    from metering
    group by 1, 2, 3

),

publication as (

    select
        daily.*,
        greatest(daily.compute_residual_credits, 0) as estimated_idle_credits,
        greatest(daily.compute_residual_credits, 0) / nullif(daily.compute_credits, 0)
            as estimated_idle_ratio,
        'UNKNOWN' as ownership_state,
        case when known_metering_rows <> source_rows then 'COMPUTE_VALUES_INCOMPLETE'
            when attribution_known_rows = source_rows then 'OBSERVED'
            else 'ATTRIBUTION_UNAVAILABLE' end as attribution_state,
        source_state.source_watermark,
        dateadd(hour, 8, dateadd(day, 1,
            to_timestamp_tz(to_char(daily.analysis_date, 'YYYY-MM-DD') || ' 00:00:00 +00:00')))
            as expected_complete_at
    from daily
    cross join source_state

),

final as (

    select
        publication.*,
        coalesce(known_metering_rows = source_rows and current_timestamp() >= expected_complete_at
            and source_watermark >= dateadd(day, 1,
                to_timestamp_tz(to_char(analysis_date, 'YYYY-MM-DD') || ' 00:00:00 +00:00')), false)
            as is_source_complete
    from publication

)

select * from final
