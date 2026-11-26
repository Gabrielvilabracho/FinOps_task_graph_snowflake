{{ config(
    materialized='incremental',
    unique_key='query_id',
    incremental_strategy='merge',
    on_schema_change='fail'
) }}

{% if is_incremental() %}
with incremental_cutoff as (

    select dateadd(day, -2, coalesce(
        max(start_time), to_timestamp_ltz('1970-01-01 00:00:00 +00:00')
    )) as start_time
    from {{ this }}

),
{% else %}
with
{% endif %}

query_history as (

    select *
    from {{ ref('stg_account_usage__query_history') }}
    {% if is_incremental() %}
    where start_time >= (select start_time from incremental_cutoff)
    {% endif %}

),

query_attribution as (

    select *
    from {{ ref('stg_account_usage__query_attribution_history') }}
    {% if is_incremental() %}
    where start_time >= (select start_time from incremental_cutoff)
    {% endif %}

),

joined as (

    select
        query_history.query_id,
        to_date(convert_timezone('UTC', query_history.start_time)) as analysis_date,
        query_history.query_type,
        query_history.execution_status,
        query_history.user_name,
        query_history.role_name,
        query_history.warehouse_id,
        query_history.warehouse_name,
        query_history.warehouse_size,
        query_history.warehouse_type,
        query_history.query_tag,
        query_history.query_hash,
        query_history.query_parameterized_hash,
        query_history.start_time,
        query_history.end_time,
        query_history.total_elapsed_time_ms,
        query_history.compilation_time_ms,
        query_history.execution_time_ms,
        query_history.queued_provisioning_time_ms,
        query_history.queued_repair_time_ms,
        query_history.queued_overload_time_ms,
        query_history.transaction_blocked_time_ms,
        query_history.bytes_scanned,
        query_history.rows_produced,
        query_history.credits_used_cloud_services,
        query_history.is_client_generated_statement,
        query_history.query_retry_time_ms,
        query_history.fault_handling_time_ms,
        query_attribution.credits_attributed_compute,
        query_attribution.credits_used_query_acceleration,
        dateadd(minute, 45, query_history.end_time) as query_history_expected_complete_at,
        dateadd(hour, 8, query_history.end_time) as attribution_expected_complete_at,
        current_timestamp() >= dateadd(minute, 45, query_history.end_time)
            as is_query_history_complete,
        current_timestamp() >= dateadd(hour, 8, query_history.end_time)
            as is_attribution_window_complete,
        case
            when query_attribution.query_id is not null then 'OBSERVED'
            when current_timestamp() < dateadd(hour, 8, query_history.end_time) then 'PENDING'
            else 'UNAVAILABLE'
        end as attribution_state,
        current_timestamp() as collected_at
    from query_history
    left join query_attribution using (query_id)

)

select * from joined
