{{
  config(
    materialized='view',
    tags=['staging', 'raw_data']
  )
}}

WITH source AS (
    SELECT 
        *,
        _PARTITIONTIME as partition_time,
        _FILE_NAME as source_file,
        _FILE_LOAD_TIME as file_load_time
    FROM {{ source('raw', 'cdo_challenge') }}
    WHERE _PARTITIONTIME IS NOT NULL
),

cleaned AS (
    SELECT 
        -- Identificadores únicos
        ROW_NUMBER() OVER() as record_id,
        
        -- Metadatos del archivo
        partition_time,
        source_file,
        file_load_time,
        
        -- Datos principales (ajustar según el esquema real)
        *,
        
        -- Campos calculados
        DATE(partition_time) as partition_date,
        EXTRACT(YEAR FROM partition_time) as partition_year,
        EXTRACT(MONTH FROM partition_time) as partition_month,
        EXTRACT(DAY FROM partition_time) as partition_day,
        
        -- Timestamps de procesamiento
        CURRENT_TIMESTAMP() as processed_at,
        '{{ invocation_id }}' as dbt_run_id
        
    FROM source
)

SELECT * FROM cleaned
