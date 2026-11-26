with source as (

    select *
    from {{ source('snowflake_account_usage', 'query_history') }}

),

renamed as (

    select
        query_id,
        query_type,
        execution_status,
        user_name,
        role_name,
        warehouse_id,
        warehouse_name,
        warehouse_size,
        warehouse_type,
        query_tag,
        query_hash,
        query_parameterized_hash,
        start_time,
        end_time,
        total_elapsed_time as total_elapsed_time_ms,
        compilation_time as compilation_time_ms,
        execution_time as execution_time_ms,
        queued_provisioning_time as queued_provisioning_time_ms,
        queued_repair_time as queued_repair_time_ms,
        queued_overload_time as queued_overload_time_ms,
        transaction_blocked_time as transaction_blocked_time_ms,
        bytes_scanned,
        rows_produced,
        credits_used_cloud_services,
        is_client_generated_statement,
        query_retry_time as query_retry_time_ms,
        fault_handling_time as fault_handling_time_ms
    from source

)

select * from renamed
