{{
  config(
    materialized='table',
    tags=['marts', 'business_insights']
  )
}}

WITH monthly_summary AS (
    SELECT 
        year,
        month,
        DATE(year, month, 1) as month_start_date,
        
        -- Métricas de volumen mensual
        SUM(total_records) as monthly_total_records,
        AVG(total_records) as monthly_avg_daily_records,
        SUM(source_files_count) as monthly_total_source_files,
        
        -- Métricas de calidad mensual
        SUM(null_timestamp_count) as monthly_null_timestamps,
        SUM(null_source_file_count) as monthly_null_source_files,
        
        -- Métricas de tendencia
        AVG(daily_change_percentage) as monthly_avg_daily_change,
        AVG(moving_avg_7d) as monthly_avg_7d_moving_avg,
        AVG(moving_avg_30d) as monthly_avg_30d_moving_avg,
        
        -- Estadísticas de variabilidad
        STDDEV(total_records) as monthly_stddev_records,
        MIN(total_records) as monthly_min_records,
        MAX(total_records) as monthly_max_records
        
    FROM {{ ref('int_daily_metrics') }}
    GROUP BY 1, 2, 3
),

quarterly_summary AS (
    SELECT 
        year,
        CASE 
            WHEN month BETWEEN 1 AND 3 THEN 1
            WHEN month BETWEEN 4 AND 6 THEN 2
            WHEN month BETWEEN 7 AND 9 THEN 3
            WHEN month BETWEEN 10 AND 12 THEN 4
        END as quarter,
        
        -- Métricas trimestrales
        SUM(monthly_total_records) as quarterly_total_records,
        AVG(monthly_avg_daily_records) as quarterly_avg_daily_records,
        SUM(monthly_total_source_files) as quarterly_total_source_files,
        
        -- Métricas de calidad trimestral
        SUM(monthly_null_timestamps) as quarterly_null_timestamps,
        SUM(monthly_null_source_files) as quarterly_null_source_files,
        
        -- Tendencias trimestrales
        AVG(monthly_avg_daily_change) as quarterly_avg_daily_change,
        AVG(monthly_avg_7d_moving_avg) as quarterly_avg_7d_moving_avg,
        AVG(monthly_avg_30d_moving_avg) as quarterly_avg_30d_moving_avg
        
    FROM monthly_summary
    GROUP BY 1, 2
),

annual_summary AS (
    SELECT 
        year,
        
        -- Métricas anuales
        SUM(monthly_total_records) as annual_total_records,
        AVG(monthly_avg_daily_records) as annual_avg_daily_records,
        SUM(monthly_total_source_files) as annual_total_source_files,
        
        -- Métricas de calidad anuales
        SUM(monthly_null_timestamps) as annual_null_timestamps,
        SUM(monthly_null_source_files) as annual_null_source_files,
        
        -- Tendencias anuales
        AVG(monthly_avg_daily_change) as annual_avg_daily_change,
        AVG(monthly_avg_7d_moving_avg) as annual_avg_7d_moving_avg,
        AVG(monthly_avg_30d_moving_avg) as annual_avg_30d_moving_avg,
        
        -- Estadísticas de variabilidad anual
        STDDEV(monthly_total_records) as annual_stddev_monthly_records,
        MIN(monthly_total_records) as annual_min_monthly_records,
        MAX(monthly_total_records) as annual_max_monthly_records
        
    FROM monthly_summary
    GROUP BY 1
),

business_insights AS (
    SELECT 
        'monthly' as granularity,
        year,
        month as period,
        month_start_date as period_start,
        
        -- Métricas principales
        monthly_total_records,
        monthly_avg_daily_records,
        monthly_total_source_files,
        
        -- Indicadores de calidad
        CASE 
            WHEN monthly_total_records > 0 
            THEN (monthly_null_timestamps / monthly_total_records) * 100
            ELSE 0 
        END as data_quality_percentage,
        
        -- Indicadores de tendencia
        monthly_avg_daily_change,
        monthly_avg_7d_moving_avg,
        monthly_avg_30d_moving_avg,
        
        -- Indicadores de variabilidad
        monthly_stddev_records,
        monthly_min_records,
        monthly_max_records,
        
        -- Timestamps
        CURRENT_TIMESTAMP() as processed_at,
        '{{ invocation_id }}' as dbt_run_id
        
    FROM monthly_summary
    
    UNION ALL
    
    SELECT 
        'quarterly' as granularity,
        year,
        quarter as period,
        DATE(year, (quarter-1)*3+1, 1) as period_start,
        
        -- Métricas principales
        quarterly_total_records,
        quarterly_avg_daily_records,
        quarterly_total_source_files,
        
        -- Indicadores de calidad
        CASE 
            WHEN quarterly_total_records > 0 
            THEN (quarterly_null_timestamps / quarterly_total_records) * 100
            ELSE 0 
        END as data_quality_percentage,
        
        -- Indicadores de tendencia
        quarterly_avg_daily_change,
        quarterly_avg_7d_moving_avg,
        quarterly_avg_30d_moving_avg,
        
        -- Indicadores de variabilidad (NULL para trimestral)
        NULL as monthly_stddev_records,
        NULL as monthly_min_records,
        NULL as monthly_max_records,
        
        -- Timestamps
        CURRENT_TIMESTAMP() as processed_at,
        '{{ invocation_id }}' as dbt_run_id
        
    FROM quarterly_summary
    
    UNION ALL
    
    SELECT 
        'annual' as granularity,
        year,
        year as period,
        DATE(year, 1, 1) as period_start,
        
        -- Métricas principales
        annual_total_records,
        annual_avg_daily_records,
        annual_total_source_files,
        
        -- Indicadores de calidad
        CASE 
            WHEN annual_total_records > 0 
            THEN (annual_null_timestamps / annual_total_records) * 100
            ELSE 0 
        END as data_quality_percentage,
        
        -- Indicadores de tendencia
        annual_avg_daily_change,
        annual_avg_7d_moving_avg,
        annual_avg_30d_moving_avg,
        
        -- Indicadores de variabilidad
        annual_stddev_monthly_records,
        annual_min_monthly_records,
        annual_max_monthly_records,
        
        -- Timestamps
        CURRENT_TIMESTAMP() as processed_at,
        '{{ invocation_id }}' as dbt_run_id
        
    FROM annual_summary
)

SELECT * FROM business_insights
ORDER BY granularity, year, period
