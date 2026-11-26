with source as (

    select *
    from {{ source('snowflake_account_usage', 'warehouse_events_history') }}

),

renamed as (

    select
        timestamp as event_timestamp,
        warehouse_id,
        warehouse_name,
        cluster_number,
        event_name,
        event_reason,
        event_state,
        user_name,
        role_name,
        query_id,
        size as warehouse_size,
        cluster_count,
        warehouse_type,
        generation,
        resource_constraint
    from source

)

select * from renamed
