# Mapa de dbt - Línea de Datos

## Visualización de la Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATASET: acero_analysis                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        RAW DATA: cdo_challenge                            │
│                    (2,003,599,864 registros)                              │
│                    (113.33 GB comprimido)                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STAGING: stg_cdo_challenge                             │
│                           (View)                                          │
│                    • Limpieza de metadatos                                │
│                    • Validación de esquema                                │
│                    • Campos calculados                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   INTERMEDIATE: int_daily_metrics                         │
│                           (Table)                                         │
│                    • Agregaciones diarias                                 │
│                    • Métricas temporales                                  │
│                    • Promedios móviles                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                  MARTS: mart_business_insights                            │
│                           (Table)                                         │
│                    • Resúmenes mensuales                                  │
│                    • Resúmenes trimestrales                               │
│                    • Resúmenes anuales                                    │
│                    • Métricas de calidad                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BUSINESS INTELLIGENCE                              │
│                    • Análisis EDA                                         │
│                    • Dashboards                                           │
│                    • Reportes ejecutivos                                  │
│                    • Estrategia de rentabilización                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Detalle de Transformaciones

### 1. Raw Data → Staging
```sql
-- stg_cdo_challenge.sql
WITH source AS (
    SELECT * FROM {{ source('raw', 'cdo_challenge') }}
),
cleaned AS (
    SELECT 
        ROW_NUMBER() OVER() as record_id,
        _PARTITIONTIME as partition_time,
        _FILE_NAME as source_file,
        _FILE_LOAD_TIME as file_load_time,
        *,
        DATE(_PARTITIONTIME) as partition_date,
        EXTRACT(YEAR FROM _PARTITIONTIME) as partition_year,
        EXTRACT(MONTH FROM _PARTITIONTIME) as partition_month,
        EXTRACT(DAY FROM _PARTITIONTIME) as partition_day,
        CURRENT_TIMESTAMP() as processed_at
    FROM source
)
SELECT * FROM cleaned
```

### 2. Staging → Intermediate
```sql
-- int_daily_metrics.sql
WITH daily_aggregation AS (
    SELECT 
        DATE(partition_time) as date,
        EXTRACT(YEAR FROM partition_time) as year,
        EXTRACT(MONTH FROM partition_time) as month,
        COUNT(*) as total_records,
        COUNT(DISTINCT source_file) as source_files_count,
        COUNTIF(partition_time IS NULL) as null_timestamp_count
    FROM {{ ref('stg_cdo_challenge') }}
    GROUP BY 1, 2, 3
),
daily_stats AS (
    SELECT *,
        LAG(total_records) OVER (ORDER BY date) as prev_day_records,
        AVG(total_records) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as moving_avg_7d
    FROM daily_aggregation
)
SELECT * FROM daily_stats
```

### 3. Intermediate → Marts
```sql
-- mart_business_insights.sql
WITH monthly_summary AS (
    SELECT 
        year, month,
        SUM(total_records) as monthly_total_records,
        AVG(total_records) as monthly_avg_daily_records,
        STDDEV(total_records) as monthly_stddev_records
    FROM {{ ref('int_daily_metrics') }}
    GROUP BY 1, 2
),
quarterly_summary AS (
    SELECT 
        year,
        CASE WHEN month BETWEEN 1 AND 3 THEN 1
             WHEN month BETWEEN 4 AND 6 THEN 2
             WHEN month BETWEEN 7 AND 9 THEN 3
             WHEN month BETWEEN 10 AND 12 THEN 4
        END as quarter,
        SUM(monthly_total_records) as quarterly_total_records
    FROM monthly_summary
    GROUP BY 1, 2
)
SELECT * FROM monthly_summary
UNION ALL
SELECT * FROM quarterly_summary
```

## Dependencias y Orden de Ejecución

### Orden de Ejecución
1. **stg_cdo_challenge** (staging)
2. **int_daily_metrics** (intermediate) - depende de staging
3. **mart_business_insights** (marts) - depende de intermediate

### Comandos de Ejecución
```bash
# Ejecutar en orden correcto
dbt run --models staging+intermediate+marts

# O ejecutar por separado
dbt run --models staging
dbt run --models intermediate
dbt run --models marts
```

## Tests de Calidad

### Tests por Modelo
- **stg_cdo_challenge**: not_null, unique
- **int_daily_metrics**: not_null, relationships
- **mart_business_insights**: not_null, unique

### Tests Personalizados
- **data_freshness**: Verificar actualización de datos
- **data_completeness**: Verificar completitud
- **data_consistency**: Verificar consistencia

## Monitoreo y Métricas

### KPIs del Pipeline
- **Tiempo de ejecución**: < 30 minutos para todos los modelos
- **Tasa de éxito**: > 95% de ejecuciones exitosas
- **Calidad de datos**: > 98% de completitud
- **Frescura**: < 24 horas de latencia

### Alertas
- Fallos en la ejecución
- Degradación de rendimiento
- Problemas de calidad de datos
- Exceso de costos de BigQuery

## Optimizaciones

### BigQuery
- Particionamiento por fecha
- Clustering por campos frecuentes
- Optimización de consultas
- Monitoreo de costos

### dbt
- Materialización apropiada (view vs table)
- Tests de calidad automatizados
- Documentación generada automáticamente
- Pipeline de CI/CD con GitHub Actions
