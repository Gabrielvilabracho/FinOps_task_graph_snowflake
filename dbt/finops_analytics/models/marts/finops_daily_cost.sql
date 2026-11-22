with date_spine as (

    select *
    from {{ ref('int_finops_date_spine') }}

),

metering as (

    select *
    from {{ ref('stg_account_usage__metering_daily_history') }}

),

source_state as (

    select min(usage_date) as source_first_usage_date,
        max(usage_date) as source_latest_usage_date
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
        count(distinct service_type) as service_type_count,
        count(*) as source_rows,
        count(case when credits_used_compute is not null
            and credits_used_cloud_services is not null and credits_used is not null
            and credits_adjustment_cloud_services is not null and credits_billed is not null
            then 1 end) as known_rows
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
        daily.source_rows,
        daily.known_rows,
        source_state.source_first_usage_date,
        source_state.source_latest_usage_date,
        -- Local reconciliation margin, not the source's three-hour latency SLA.
        dateadd(hour, 48, dateadd(day, 1,
            to_timestamp_tz(to_char(date_spine.analysis_date, 'YYYY-MM-DD') || ' 00:00:00 +00:00')))
            as expected_complete_at
    from date_spine
    left join daily
        on date_spine.analysis_date = daily.analysis_date
    cross join source_state

),

publication as (

    select
        publication_window.*,
        coalesce(current_timestamp() >= expected_complete_at
            and source_latest_usage_date > analysis_date
            and source_first_usage_date < analysis_date
            and source_rows > 0 and known_rows = source_rows, false) as is_source_complete,
        case
            when current_timestamp() < expected_complete_at then 'SOURCE_NOT_EXPECTED_COMPLETE'
            when source_first_usage_date is null or source_first_usage_date >= analysis_date
                then 'HISTORY_NOT_COVERED'
            when coalesce(source_rows, 0) = 0 then 'SOURCE_PUBLICATION_ABSENT'
            when known_rows <> source_rows then 'SOURCE_VALUES_INCOMPLETE'
            when source_latest_usage_date <= analysis_date then 'SOURCE_PUBLICATION_INCOMPLETE'
            else null
        end as evidence_reason
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
        source_first_usage_date,
        coalesce(source_rows, 0) as source_rows,
        evidence_reason,
        'CREDITS_NOT_CURRENCY' as financial_basis,
        expected_complete_at,
        is_source_complete
    from publication

)

select * from final
