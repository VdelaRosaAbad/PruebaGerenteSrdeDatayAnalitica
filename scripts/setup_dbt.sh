#!/bin/bash

# Script de configuración y ejecución de dbt
# Análisis EDA - Empresa de Aceros Largos

echo "🚀 Configurando entorno dbt para análisis de aceros..."

# Verificar si estamos en Cloud Shell
if [ -z "$CLOUD_SHELL" ]; then
    echo "⚠️  Este script está diseñado para ejecutarse en Google Cloud Shell"
    echo "   Por favor, abre Cloud Shell y ejecuta este script nuevamente"
    exit 1
fi

echo "✅ Confirmado: Ejecutando en Google Cloud Shell"

# Configurar variables de entorno
export PROJECT_ID=$(gcloud config get-value project)
export DATASET_NAME="acero_analysis"

echo "📊 Proyecto GCP: $PROJECT_ID"
echo "🗃️  Dataset: $DATASET_NAME"

# Instalar dbt
echo "🔧 Instalando dbt..."
pip install dbt-bigquery

# Verificar instalación
if command -v dbt &> /dev/null; then
    echo "✅ dbt instalado correctamente"
    dbt --version
else
    echo "❌ Error instalando dbt"
    exit 1
fi

# Navegar al directorio dbt
cd dbt

# Instalar dependencias
echo "📦 Instalando dependencias dbt..."
dbt deps

# Verificar conexión
echo "🔍 Verificando conexión a BigQuery..."
dbt debug

# Ejecutar modelos
echo "🚀 Ejecutando modelos dbt..."
echo "   Esto puede tomar varios minutos..."

# Ejecutar modelos de staging
echo "📋 Ejecutando modelos de staging..."
dbt run --models staging

# Ejecutar modelos intermedios
echo "🔄 Ejecutando modelos intermedios..."
dbt run --models intermediate

# Ejecutar modelos de marts
echo "🎯 Ejecutando modelos de marts..."
dbt run --models marts

# Ejecutar tests
echo "🧪 Ejecutando tests de calidad..."
dbt test

# Generar documentación
echo "📚 Generando documentación..."
dbt docs generate

echo "✅ Configuración dbt completada exitosamente!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Revisar documentación en: dbt/target/index.html"
echo "2. Verificar modelos en BigQuery"
echo "3. Ejecutar análisis EDA: python scripts/eda_analysis.py"
echo "4. Revisar notebooks en la carpeta notebooks/"
