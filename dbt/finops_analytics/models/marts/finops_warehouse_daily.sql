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
        case
            when count(credits_attributed_compute_queries) = count(*)
                then greatest(
                    sum(credits_used_compute) - sum(credits_attributed_compute_queries),
                    0
                )
        end as estimated_idle_credits
    from metering
    group by 1, 2, 3

),

publication as (

    select
        daily.*,
        daily.estimated_idle_credits / nullif(daily.compute_credits, 0)
            as estimated_idle_ratio,
        source_state.source_watermark,
        dateadd(hour, 8, dateadd(day, 1, daily.analysis_date::timestamp_tz))
            as expected_complete_at
    from daily
    cross join source_state

),

final as (

    select
        publication.*,
        current_timestamp() >= expected_complete_at
            and source_watermark >= dateadd(day, 1, analysis_date::timestamp_tz)
            as is_source_complete
    from publication

)

select * from final
