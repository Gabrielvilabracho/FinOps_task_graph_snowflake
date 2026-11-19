with date_spine as (

    select *
    from {{ ref('int_finops_date_spine') }}

),

metering as (

    select *
    from {{ ref('stg_account_usage__metering_daily_history') }}

),

source_state as (

    select max(usage_date) as source_latest_usage_date
    from metering

),

daily as (

    select
        usage_date as analysis_date,
        sum(credits_used_compute) as compute_credits,
        sum(credits_used_cloud_services) as cloud_services_credits,
        sum(credits_used) as raw_credits_used,
        sum(credits_adjustment_cloud_services) as cloud_services_adjustment_credits,
        sum(credits_billed) as billed_credits,
        count(distinct service_type) as service_type_count
    from metering
    group by usage_date

),

publication_window as (

    select
        date_spine.analysis_date,
        daily.compute_credits,
        daily.cloud_services_credits,
        daily.raw_credits_used,
        daily.cloud_services_adjustment_credits,
        daily.billed_credits,
        daily.service_type_count,
        source_state.source_latest_usage_date,
        dateadd(hour, 3, dateadd(day, 1, date_spine.analysis_date::timestamp_tz))
            as expected_complete_at
    from date_spine
    left join daily
        on date_spine.analysis_date = daily.analysis_date
    cross join source_state

),

publication as (

    select
        publication_window.*,
        current_timestamp() >= expected_complete_at
            and source_latest_usage_date > analysis_date
            as is_source_complete
    from publication_window

),

final as (

    select
        analysis_date,
        iff(is_source_complete, coalesce(compute_credits, 0), null) as compute_credits,
        iff(is_source_complete, coalesce(cloud_services_credits, 0), null)
            as cloud_services_credits,
        iff(is_source_complete, coalesce(raw_credits_used, 0), null) as raw_credits_used,
        iff(is_source_complete, coalesce(cloud_services_adjustment_credits, 0), null)
            as cloud_services_adjustment_credits,
        iff(is_source_complete, coalesce(billed_credits, 0), null) as billed_credits,
        iff(is_source_complete, coalesce(service_type_count, 0), null) as service_type_count,
        source_latest_usage_date,
        expected_complete_at,
        is_source_complete
    from publication

)

select * from final
