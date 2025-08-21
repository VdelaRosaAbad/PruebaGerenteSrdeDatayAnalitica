#!/bin/bash

# Script de configuración para Cloud Shell
# Análisis EDA - Empresa de Aceros Largos

echo "🚀 Configurando entorno para análisis EDA..."

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
export TABLE_NAME="cdo_challenge"

echo "📊 Proyecto GCP: $PROJECT_ID"
echo "🗃️  Dataset: $DATASET_NAME"
echo "📋 Tabla: $TABLE_NAME"

# Habilitar APIs necesarias
echo "🔧 Habilitando APIs de Google Cloud..."
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable dataflow.googleapis.com

# Instalar dependencias Python
echo "🐍 Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Configurar autenticación
echo "🔐 Configurando autenticación..."
gcloud auth application-default login

# Crear dataset en BigQuery
echo "🗄️  Creando dataset en BigQuery..."
bq mk --dataset --description "Dataset para análisis de aceros largos" $PROJECT_ID:$DATASET_NAME

echo "✅ Configuración completada exitosamente!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Ejecutar: python scripts/load_data.py"
echo "2. Ejecutar: python scripts/eda_analysis.py"
echo "3. Ejecutar: dbt run"
echo "4. Revisar notebooks en la carpeta notebooks/"
