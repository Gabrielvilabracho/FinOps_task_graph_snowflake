with source as (

    select *
    from {{ source('snowflake_account_usage', 'warehouse_load_history') }}

),

renamed as (

    select
        start_time,
        end_time,
        warehouse_id,
        warehouse_name,
        avg_running,
        avg_queued_load,
        avg_queued_provisioning,
        avg_blocked
    from source

)

select * from renamed
