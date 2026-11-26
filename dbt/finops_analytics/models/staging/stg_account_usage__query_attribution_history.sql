with source as (

    select *
    from {{ source('snowflake_account_usage', 'query_attribution_history') }}

),

renamed as (

    select
        query_id,
        parent_query_id,
        root_query_id,
        warehouse_id,
        warehouse_name,
        query_hash,
        query_parameterized_hash,
        query_tag,
        user_name,
        start_time,
        end_time,
        credits_attributed_compute,
        credits_used_query_acceleration
    from source

)

select * from renamed
