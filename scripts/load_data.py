#!/usr/bin/env python3
"""
Script para cargar el dataset de aceros largos en BigQuery
Maneja el archivo de 113.33 GB de manera eficiente
"""

import os
import logging
from google.cloud import bigquery
from google.cloud import storage
import pandas as pd
from tqdm import tqdm
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
PROJECT_ID = os.getenv('PROJECT_ID') or 'your-project-id'
DATASET_NAME = 'acero_analysis'
TABLE_NAME = 'cdo_challenge'
SOURCE_URI = 'gs://desafio-deacero-143d30a0-d8f8-4154-b7df-1773cf286d32/cdo_challenge.csv.gz'

def create_bigquery_client():
    """Crear cliente de BigQuery"""
    try:
        client = bigquery.Client(project=PROJECT_ID)
        logger.info(f"✅ Cliente BigQuery creado para proyecto: {PROJECT_ID}")
        return client
    except Exception as e:
        logger.error(f"❌ Error creando cliente BigQuery: {e}")
        raise

def create_dataset_and_table(client):
    """Crear dataset y tabla en BigQuery"""
    try:
        dataset_id = f"{PROJECT_ID}.{DATASET_NAME}"
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"  # Ajustar según tu región
        dataset = client.create_dataset(dataset, exists_ok=True)
        logger.info(f"✅ Dataset creado: {dataset_id}")
        
        # Crear tabla con esquema automático
        table_id = f"{dataset_id}.{TABLE_NAME}"
        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,  # Saltar encabezados
            autodetect=True,  # Detección automática de esquema
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            max_bad_records=1000  # Permitir algunos registros malos
        )
        
        logger.info(f"✅ Tabla configurada: {table_id}")
        return table_id, job_config
        
    except Exception as e:
        logger.error(f"❌ Error creando dataset/tabla: {e}")
        raise

def load_data_from_gcs(client, table_id, job_config):
    """Cargar datos desde Google Cloud Storage a BigQuery"""
    try:
        logger.info(f"🚀 Iniciando carga de datos desde: {SOURCE_URI}")
        logger.info("📊 Este proceso puede tomar varias horas debido al tamaño del archivo...")
        
        # Iniciar job de carga
        load_job = client.load_table_from_uri(
            SOURCE_URI,
            table_id,
            job_config=job_config
        )
        
        # Monitorear progreso
        logger.info("⏳ Monitoreando progreso de la carga...")
        while not load_job.done():
            time.sleep(30)  # Verificar cada 30 segundos
            logger.info(f"📈 Estado: {load_job.state}")
        
        # Verificar resultado
        if load_job.errors:
            logger.error(f"❌ Errores en la carga: {load_job.errors}")
            return False
        
        # Obtener estadísticas
        table = client.get_table(table_id)
        logger.info(f"✅ Carga completada exitosamente!")
        logger.info(f"📊 Registros cargados: {table.num_rows:,}")
        logger.info(f"🗂️  Tamaño de tabla: {table.num_bytes / (1024**3):.2f} GB")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en la carga de datos: {e}")
        return False

def validate_data_quality(client, table_id):
    """Validar calidad de los datos cargados"""
    try:
        logger.info("🔍 Validando calidad de los datos...")
        
        # Consulta para verificar estructura
        query = f"""
        SELECT 
            COUNT(*) as total_rows,
            COUNT(DISTINCT _FILE_NAME) as files_processed,
            MIN(_FILE_LOAD_TIME) as earliest_load,
            MAX(_FILE_LOAD_TIME) as latest_load
        FROM `{table_id}`
        """
        
        query_job = client.query(query)
        results = query_job.result()
        
        for row in results:
            logger.info(f"📊 Total de filas: {row.total_rows:,}")
            logger.info(f"📁 Archivos procesados: {row.files_processed}")
            logger.info(f"⏰ Rango de carga: {row.earliest_load} a {row.latest_load}")
        
        # Verificar columnas
        table = client.get_table(table_id)
        logger.info(f"🏗️  Esquema de tabla:")
        for field in table.schema:
            logger.info(f"   - {field.name}: {field.field_type}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en validación: {e}")
        return False

def main():
    """Función principal"""
    logger.info("🚀 Iniciando proceso de carga de datos...")
    
    try:
        # Crear cliente
        client = create_bigquery_client()
        
        # Crear dataset y tabla
        table_id, job_config = create_dataset_and_table(client)
        
        # Cargar datos
        success = load_data_from_gcs(client, table_id, job_config)
        
        if success:
            # Validar calidad
            validate_data_quality(client, table_id)
            logger.info("🎉 Proceso de carga completado exitosamente!")
        else:
            logger.error("💥 Fallo en el proceso de carga")
            
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}")
        raise

if __name__ == "__main__":
    main()
