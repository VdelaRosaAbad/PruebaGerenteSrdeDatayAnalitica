# Análisis EDA - Empresa de Aceros Largos

## Descripción del Proyecto
Análisis de datos comerciales de una empresa de aceros largos para un periodo de 5 años, con el objetivo de proponer una estrategia de rentabilización para los próximos 12 meses.

## Estructura del Proyecto
```
├── data/                   # Datos y scripts de procesamiento
├── dbt/                    # Proyecto dbt para transformaciones
├── notebooks/              # Jupyter notebooks para análisis EDA
├── src/                    # Código fuente Python
├── docs/                   # Documentación
├── presentations/          # Presentaciones PowerPoint
└── scripts/                # Scripts de automatización
```

## Tecnologías Utilizadas
- **BigQuery**: Almacenamiento y consulta de datos
- **Python**: Análisis de datos y automatización
- **dbt**: Transformaciones de datos
- **GitHub**: Control de versiones
- **Cloud Shell**: Entorno de ejecución

## Setup Inicial
1. Configurar Google Cloud Project
2. Habilitar BigQuery API
3. Crear dataset en BigQuery
4. Configurar dbt
5. Instalar dependencias Python

## Datos del Dataset
- **Tamaño**: 113.33 GB comprimido / ~373 GB descomprimido
- **Registros**: 2,003,599,864
- **Fuente**: gs://desafio-deacero-143d30a0-d8f8-4154-b7df-1773cf286d32/cdo_challenge.csv.gz
