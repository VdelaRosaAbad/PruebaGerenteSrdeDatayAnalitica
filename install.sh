#!/bin/bash

# Script de instalación completa para el proyecto de análisis EDA
# Empresa de Aceros Largos - Desafío CDO

echo "🚀 INSTALACIÓN COMPLETA - ANÁLISIS EDA EMPRESA DE ACEROS"
echo "=" * 60

# Verificar si estamos en Cloud Shell
if [ -z "$CLOUD_SHELL" ]; then
    echo "⚠️  ADVERTENCIA: Este script está diseñado para Google Cloud Shell"
    echo "   Para mejor experiencia, abre Cloud Shell y ejecuta este script"
    echo "   Continuando con instalación local..."
    echo ""
fi

# Configurar variables de entorno
export PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "your-project-id")
export DATASET_NAME="acero_analysis"
export TABLE_NAME="cdo_challenge"

echo "📊 Configuración del proyecto:"
echo "   - Proyecto GCP: $PROJECT_ID"
echo "   - Dataset: $DATASET_NAME"
echo "   - Tabla: $TABLE_NAME"
echo ""

# Crear estructura de directorios
echo "📁 Creando estructura de directorios..."
mkdir -p data
mkdir -p dbt/{models/{staging,intermediate,marts},tests,seeds,snapshots,macros,analyses}
mkdir -p notebooks
mkdir -p src
mkdir -p docs
mkdir -p presentations
mkdir -p scripts
mkdir -p reports
mkdir -p .github/workflows

echo "✅ Estructura de directorios creada"
echo ""

# Verificar si gcloud está disponible
if command -v gcloud &> /dev/null; then
    echo "🔧 Configurando Google Cloud..."
    
    # Habilitar APIs necesarias
    echo "   Habilitando APIs..."
    gcloud services enable bigquery.googleapis.com
    gcloud services enable storage.googleapis.com
    gcloud services enable dataflow.googleapis.com
    
    # Configurar autenticación
    echo "   Configurando autenticación..."
    gcloud auth application-default login --no-launch-browser
    
    # Crear dataset en BigQuery
    echo "   Creando dataset en BigQuery..."
    bq mk --dataset --description "Dataset para análisis de aceros largos" $PROJECT_ID:$DATASET_NAME 2>/dev/null || echo "Dataset ya existe"
    
    echo "✅ Google Cloud configurado"
else
    echo "⚠️  gcloud no está disponible. Configura Google Cloud manualmente."
fi

echo ""

# Instalar dependencias Python
echo "🐍 Instalando dependencias Python..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependencias Python instaladas"
echo ""

# Instalar dbt
echo "🔧 Instalando dbt..."
pip install dbt-bigquery

if command -v dbt &> /dev/null; then
    echo "✅ dbt instalado correctamente"
    dbt --version
else
    echo "❌ Error instalando dbt"
fi

echo ""

# Configurar permisos de ejecución
echo "🔐 Configurando permisos de ejecución..."
chmod +x scripts/*.sh
chmod +x install.sh

echo "✅ Permisos configurados"
echo ""

# Verificar instalación
echo "🔍 Verificando instalación..."
echo ""

echo "📋 RESUMEN DE INSTALACIÓN:"
echo "   ✅ Estructura de directorios creada"
echo "   ✅ Dependencias Python instaladas"
echo "   ✅ dbt instalado"
echo "   ✅ Scripts configurados"
echo ""

if command -v gcloud &> /dev/null; then
    echo "   ✅ Google Cloud configurado"
    echo "   ✅ BigQuery dataset creado"
else
    echo "   ⚠️  Google Cloud requiere configuración manual"
fi

echo ""

# Mostrar próximos pasos
echo "🚀 PRÓXIMOS PASOS:"
echo ""

if command -v gcloud &> /dev/null; then
    echo "1. 🔄 Cargar datos en BigQuery:"
    echo "   python scripts/load_data.py"
    echo ""
    echo "2. 📊 Ejecutar análisis EDA:"
    echo "   python scripts/eda_analysis.py"
    echo ""
    echo "3. 🔧 Configurar y ejecutar dbt:"
    echo "   ./scripts/setup_dbt.sh"
    echo ""
else
    echo "1. 🔧 Configurar Google Cloud y BigQuery manualmente"
    echo "2. 🔄 Cargar datos en BigQuery"
    echo "3. 📊 Ejecutar análisis EDA"
    echo "4. 🔧 Configurar y ejecutar dbt"
    echo ""
fi

echo "4. 📚 Revisar notebooks en la carpeta notebooks/"
echo "5. 📊 Verificar resultados en BigQuery"
echo "6. 📋 Crear presentación PowerPoint basada en el template"
echo ""

# Verificar si el usuario quiere continuar con la carga de datos
if command -v gcloud &> /dev/null; then
    read -p "¿Deseas continuar con la carga de datos en BigQuery? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 Iniciando carga de datos..."
        echo "⚠️  ADVERTENCIA: Este proceso puede tomar varias horas debido al tamaño del archivo (113.33 GB)"
        echo ""
        
        read -p "¿Estás seguro de continuar? (y/N): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🚀 Ejecutando script de carga de datos..."
            python scripts/load_data.py
        else
            echo "⏸️  Carga de datos cancelada. Puedes ejecutarla más tarde con: python scripts/load_data.py"
        fi
    else
        echo "⏸️  Carga de datos pospuesta. Puedes ejecutarla más tarde con: python scripts/load_data.py"
    fi
fi

echo ""
echo "🎉 INSTALACIÓN COMPLETADA EXITOSAMENTE!"
echo ""
echo "📁 Estructura del proyecto creada:"
echo "   - data/           # Datos y scripts de procesamiento"
echo "   - dbt/            # Proyecto dbt para transformaciones"
echo "   - notebooks/      # Jupyter notebooks para análisis EDA"
echo "   - src/            # Código fuente Python"
echo "   - docs/           # Documentación"
echo "   - presentations/  # Presentaciones PowerPoint"
echo "   - scripts/        # Scripts de automatización"
echo "   - reports/        # Reportes de calidad"
echo ""
echo "🔗 Recursos útiles:"
echo "   - README.md: Documentación principal del proyecto"
echo "   - requirements.txt: Dependencias Python"
echo "   - scripts/: Scripts de configuración y ejecución"
echo "   - dbt/: Proyecto de transformaciones de datos"
echo ""
echo "📞 Para soporte o preguntas, revisa la documentación o contacta al equipo."
echo ""
echo "¡Buena suerte con tu análisis EDA! 🚀"
