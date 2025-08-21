{{
  config(
    materialized='table',
    tags=['intermediate', 'daily_metrics']
  )
}}

WITH daily_aggregation AS (
    SELECT 
        DATE(partition_time) as date,
        EXTRACT(YEAR FROM partition_time) as year,
        EXTRACT(MONTH FROM partition_time) as month,
        EXTRACT(DAY FROM partition_time) as day,
        EXTRACT(DAYOFWEEK FROM partition_time) as day_of_week,
        
        -- Métricas de volumen
        COUNT(*) as total_records,
        COUNT(DISTINCT source_file) as source_files_count,
        
        -- Métricas de calidad
        COUNTIF(partition_time IS NULL) as null_timestamp_count,
        COUNTIF(source_file IS NULL) as null_source_file_count,
        
        -- Métricas de procesamiento
        MIN(partition_time) as earliest_record_time,
        MAX(partition_time) as latest_record_time,
        
        -- Timestamps de procesamiento
        CURRENT_TIMESTAMP() as processed_at,
        '{{ invocation_id }}' as dbt_run_id
        
    FROM {{ ref('stg_cdo_challenge') }}
    WHERE partition_time IS NOT NULL
    GROUP BY 1, 2, 3, 4, 5
),

daily_stats AS (
    SELECT 
        *,
        
        -- Estadísticas adicionales
        LAG(total_records) OVER (ORDER BY date) as prev_day_records,
        LEAD(total_records) OVER (ORDER BY date) as next_day_records,
        
        -- Cambios porcentuales
        CASE 
            WHEN LAG(total_records) OVER (ORDER BY date) > 0 
            THEN ((total_records - LAG(total_records) OVER (ORDER BY date)) / LAG(total_records) OVER (ORDER BY date)) * 100
            ELSE NULL 
        END as daily_change_percentage,
        
        -- Promedio móvil de 7 días
        AVG(total_records) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as moving_avg_7d,
        
        -- Promedio móvil de 30 días
        AVG(total_records) OVER (ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) as moving_avg_30d
        
    FROM daily_aggregation
)

SELECT * FROM daily_stats
ORDER BY date
