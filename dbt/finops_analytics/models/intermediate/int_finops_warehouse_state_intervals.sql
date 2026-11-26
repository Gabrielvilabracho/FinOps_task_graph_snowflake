with lifecycle_events as (

    select
        warehouse_id,
        warehouse_name,
        event_timestamp,
        upper(event_name) as event_name
    from {{ ref('stg_account_usage__warehouse_events_history') }}
    where upper(event_name) in ('RESUME_WAREHOUSE', 'SUSPEND_WAREHOUSE')
        and upper(event_state) = 'STARTED'

),

sequenced as (

    select
        warehouse_id,
        warehouse_name,
        event_timestamp,
        event_name,
        lead(event_timestamp) over (
            partition by warehouse_id order by event_timestamp
        ) as next_event_timestamp,
        lead(event_name) over (
            partition by warehouse_id order by event_timestamp
        ) as next_event_name
    from lifecycle_events

),

bounded as (

    select
        warehouse_id,
        warehouse_name,
        event_timestamp as estimated_on_start,
        next_event_timestamp as estimated_on_end,
        datediff(second, event_timestamp, next_event_timestamp)
            as event_bounded_on_seconds,
        'EVENT_BOUNDED_ESTIMATE' as interval_evidence
    from sequenced
    where event_name = 'RESUME_WAREHOUSE'
        and next_event_name = 'SUSPEND_WAREHOUSE'
        and next_event_timestamp > event_timestamp

)

select * from bounded
