# Proyecto dbt - Análisis de Aceros Largos

## Descripción
Este proyecto dbt implementa la transformación de datos para el análisis EDA de la empresa de aceros largos, procesando un dataset de más de 2 mil millones de registros.

## Arquitectura del Proyecto

### Estructura de Modelos

```
dbt/
├── models/
│   ├── staging/           # Datos crudos limpiados
│   │   └── stg_cdo_challenge.sql
│   ├── intermediate/      # Transformaciones intermedias
│   │   └── int_daily_metrics.sql
│   └── marts/            # Modelos finales para análisis
│       └── mart_business_insights.sql
├── tests/                 # Tests de calidad
├── seeds/                 # Datos de referencia
├── snapshots/             # Capturas de cambios
├── macros/                # Macros reutilizables
├── analyses/              # Análisis ad-hoc
└── docs/                  # Documentación generada
```

### Flujo de Datos

```
Raw Data (BigQuery)
       ↓
stg_cdo_challenge (Staging)
       ↓
int_daily_metrics (Intermediate)
       ↓
mart_business_insights (Marts)
       ↓
Business Analysis & Reporting
```

## Modelos Principales

### 1. Staging (`stg_cdo_challenge`)
- **Propósito**: Limpieza y estandarización de datos crudos
- **Materialización**: View
- **Funciones**:
  - Limpieza de metadatos
  - Validación de esquema
  - Enriquecimiento con campos calculados

### 2. Intermediate (`int_daily_metrics`)
- **Propósito**: Agregaciones diarias y métricas temporales
- **Materialización**: Table
- **Funciones**:
  - Agregación por día
  - Cálculo de tendencias
  - Promedios móviles

### 3. Marts (`mart_business_insights`)
- **Propósito**: Modelos finales para análisis de negocio
- **Materialización**: Table
- **Funciones**:
  - Resúmenes mensuales, trimestrales y anuales
  - Métricas de calidad de datos
  - Indicadores de rendimiento

## Configuración

### Variables de Entorno
```bash
export PROJECT_ID="your-gcp-project-id"
export DATASET_NAME="acero_analysis"
```

### Perfiles
- **dev**: Desarrollo con dataset de desarrollo
- **prod**: Producción con dataset de producción
- **test**: Testing con dataset de pruebas

## Uso

### Instalación
```bash
# Instalar dependencias
dbt deps

# Verificar conexión
dbt debug
```

### Ejecución
```bash
# Ejecutar todos los modelos
dbt run

# Ejecutar modelos específicos
dbt run --models staging
dbt run --models intermediate
dbt run --models marts

# Ejecutar en orden específico
dbt run --models staging+intermediate+marts
```

### Testing
```bash
# Ejecutar todos los tests
dbt test

# Ejecutar tests específicos
dbt test --models stg_cdo_challenge
```

### Documentación
```bash
# Generar documentación
dbt docs generate

# Servir documentación localmente
dbt docs serve
```

## Tests de Calidad

### Tests Automáticos
- **not_null**: Verificar campos obligatorios
- **unique**: Verificar unicidad de identificadores
- **relationships**: Verificar integridad referencial

### Tests Personalizados
- **data_freshness**: Verificar actualización de datos
- **data_completeness**: Verificar completitud
- **data_consistency**: Verificar consistencia

## Monitoreo

### Métricas de Rendimiento
- Tiempo de ejecución por modelo
- Número de registros procesados
- Uso de recursos de BigQuery

### Alertas
- Fallos en la ejecución
- Degradación de rendimiento
- Problemas de calidad de datos

## Mantenimiento

### Actualizaciones
- Revisar logs de ejecución
- Monitorear costos de BigQuery
- Optimizar consultas según sea necesario

### Backup y Recuperación
- Snapshots automáticos de datos críticos
- Scripts de recuperación en caso de fallo
- Documentación de procedimientos de emergencia

## Contribución

### Desarrollo
1. Crear rama feature
2. Implementar cambios
3. Ejecutar tests localmente
4. Crear pull request

### Code Review
- Verificar sintaxis SQL
- Validar lógica de negocio
- Revisar tests de calidad
- Confirmar documentación

## Recursos Adicionales

### Documentación
- [dbt Documentation](https://docs.getdbt.com/)
- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [dbt BigQuery Adapter](https://docs.getdbt.com/reference/warehouse-profiles/bigquery-profile)

### Comunidad
- [dbt Community](https://community.getdbt.com/)
- [dbt Slack](https://community.getdbt.com/join-the-community)

## Contacto
Para preguntas o soporte sobre este proyecto dbt, contacta al equipo de datos.
