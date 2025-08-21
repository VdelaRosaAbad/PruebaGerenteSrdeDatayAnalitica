#!/usr/bin/env python3
"""
Script de Análisis Exploratorio de Datos (EDA) para empresa de aceros largos
Analiza el dataset de 5 años para identificar patrones y oportunidades de rentabilización
"""

import os
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from google.cloud import bigquery
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
PROJECT_ID = os.getenv('PROJECT_ID') or 'your-project-id'
DATASET_NAME = 'acero_analysis'
TABLE_NAME = 'cdo_challenge'

# Configurar estilo de gráficos
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class SteelCompanyEDA:
    """Clase para análisis EDA de la empresa de aceros"""
    
    def __init__(self):
        """Inicializar cliente BigQuery"""
        try:
            self.client = bigquery.Client(project=PROJECT_ID)
            self.table_id = f"{PROJECT_ID}.{DATASET_NAME}.{TABLE_NAME}"
            logger.info(f"✅ Cliente BigQuery inicializado para tabla: {self.table_id}")
        except Exception as e:
            logger.error(f"❌ Error inicializando BigQuery: {e}")
            raise
    
    def get_data_overview(self):
        """Obtener vista general de los datos"""
        logger.info("🔍 Obteniendo vista general de los datos...")
        
        query = f"""
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT DATE(_PARTITIONTIME)) as unique_dates,
            MIN(DATE(_PARTITIONTIME)) as earliest_date,
            MAX(DATE(_PARTITIONTIME)) as latest_date,
            COUNT(DISTINCT _FILE_NAME) as source_files
        FROM `{self.table_id}`
        """
        
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            
            for row in results:
                logger.info(f"📊 Total de registros: {row.total_records:,}")
                logger.info(f"📅 Fechas únicas: {row.unique_dates}")
                logger.info(f"⏰ Rango temporal: {row.earliest_date} a {row.latest_date}")
                logger.info(f"📁 Archivos fuente: {row.source_files}")
                
                # Calcular duración del dataset
                duration = (row.latest_date - row.earliest_date).days
                logger.info(f"⏱️  Duración del dataset: {duration} días ({duration/365:.1f} años)")
                
                return row
                
        except Exception as e:
            logger.error(f"❌ Error obteniendo vista general: {e}")
            return None
    
    def analyze_schema(self):
        """Analizar esquema de la tabla"""
        logger.info("🏗️  Analizando esquema de la tabla...")
        
        try:
            table = self.client.get_table(self.table_id)
            
            logger.info(f"📋 Esquema de la tabla '{table.table_id}':")
            for field in table.schema:
                logger.info(f"   - {field.name}: {field.field_type} (nullable: {field.is_nullable})")
            
            return table.schema
            
        except Exception as e:
            logger.error(f"❌ Error analizando esquema: {e}")
            return None
    
    def analyze_temporal_patterns(self):
        """Analizar patrones temporales en los datos"""
        logger.info("⏰ Analizando patrones temporales...")
        
        query = f"""
        SELECT 
            DATE(_PARTITIONTIME) as date,
            COUNT(*) as daily_records,
            COUNT(DISTINCT _FILE_NAME) as daily_files
        FROM `{self.table_id}`
        WHERE _PARTITIONTIME IS NOT NULL
        GROUP BY DATE(_PARTITIONTIME)
        ORDER BY date
        """
        
        try:
            query_job = self.client.query(query)
            df = query_job.to_dataframe()
            
            # Crear gráfico de volumen temporal
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
            
            # Gráfico de registros diarios
            ax1.plot(df['date'], df['daily_records'], linewidth=2, alpha=0.7)
            ax1.set_title('Volumen de Registros por Día', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Fecha')
            ax1.set_ylabel('Número de Registros')
            ax1.grid(True, alpha=0.3)
            
            # Gráfico de archivos diarios
            ax2.plot(df['date'], df['daily_files'], linewidth=2, alpha=0.7, color='orange')
            ax2.set_title('Archivos Procesados por Día', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Fecha')
            ax2.set_ylabel('Número de Archivos')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig('notebooks/temporal_patterns.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info("✅ Gráfico de patrones temporales guardado")
            
            # Análisis de estacionalidad
            df['month'] = df['date'].dt.month
            df['year'] = df['date'].dt.year
            
            monthly_avg = df.groupby('month')['daily_records'].mean()
            
            fig, ax = plt.subplots(figsize=(12, 6))
            monthly_avg.plot(kind='bar', ax=ax, color='skyblue', alpha=0.7)
            ax.set_title('Promedio de Registros por Mes', fontsize=14, fontweight='bold')
            ax.set_xlabel('Mes')
            ax.set_ylabel('Promedio de Registros Diarios')
            ax.set_xticklabels(['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                               'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'])
            plt.tight_layout()
            plt.savefig('notebooks/monthly_patterns.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error analizando patrones temporales: {e}")
            return None
    
    def analyze_data_quality(self):
        """Analizar calidad de los datos"""
        logger.info("🔍 Analizando calidad de los datos...")
        
        # Obtener columnas del esquema
        table = self.client.get_table(self.table_id)
        columns = [field.name for field in table.schema]
        
        quality_metrics = {}
        
        for column in columns[:10]:  # Analizar primeras 10 columnas
            try:
                query = f"""
                SELECT 
                    COUNT(*) as total_rows,
                    COUNTIF({column} IS NULL) as null_count,
                    COUNTIF({column} = '') as empty_count,
                    COUNT(DISTINCT {column}) as unique_values
                FROM `{self.table_id}`
                """
                
                query_job = self.client.query(query)
                results = query_job.result()
                
                for row in results:
                    null_percentage = (row.null_count / row.total_rows) * 100 if row.total_rows > 0 else 0
                    empty_percentage = (row.empty_count / row.total_rows) * 100 if row.total_rows > 0 else 0
                    
                    quality_metrics[column] = {
                        'total_rows': row.total_rows,
                        'null_count': row.null_count,
                        'null_percentage': null_percentage,
                        'empty_count': row.empty_count,
                        'empty_percentage': empty_percentage,
                        'unique_values': row.unique_values
                    }
                    
                    logger.info(f"📊 {column}: {null_percentage:.2f}% nulos, {empty_percentage:.2f}% vacíos")
                    
            except Exception as e:
                logger.warning(f"⚠️  No se pudo analizar columna {column}: {e}")
                continue
        
        return quality_metrics
    
    def generate_summary_report(self):
        """Generar reporte resumen del EDA"""
        logger.info("📋 Generando reporte resumen...")
        
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'project_id': PROJECT_ID,
            'dataset': DATASET_NAME,
            'table': TABLE_NAME
        }
        
        # Obtener métricas
        overview = self.get_data_overview()
        if overview:
            report['data_overview'] = {
                'total_records': overview.total_records,
                'unique_dates': overview.unique_dates,
                'date_range': f"{overview.earliest_date} a {overview.latest_date}",
                'duration_years': (overview.latest_date - overview.earliest_date).days / 365
            }
        
        # Analizar esquema
        schema = self.analyze_schema()
        if schema:
            report['schema'] = {
                'total_columns': len(schema),
                'columns': [field.name for field in schema]
            }
        
        # Analizar calidad
        quality = self.analyze_data_quality()
        if quality:
            report['data_quality'] = quality
        
        # Guardar reporte
        import json
        with open('notebooks/eda_summary_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str, ensure_ascii=False)
        
        logger.info("✅ Reporte resumen guardado en notebooks/eda_summary_report.json")
        
        return report
    
    def run_complete_eda(self):
        """Ejecutar análisis EDA completo"""
        logger.info("🚀 Iniciando análisis EDA completo...")
        
        try:
            # 1. Vista general
            self.get_data_overview()
            
            # 2. Análisis de esquema
            self.analyze_schema()
            
            # 3. Patrones temporales
            self.analyze_temporal_patterns()
            
            # 4. Calidad de datos
            self.analyze_data_quality()
            
            # 5. Reporte resumen
            self.generate_summary_report()
            
            logger.info("🎉 Análisis EDA completado exitosamente!")
            logger.info("📁 Revisa los archivos generados en la carpeta notebooks/")
            
        except Exception as e:
            logger.error(f"💥 Error en análisis EDA: {e}")
            raise

def main():
    """Función principal"""
    logger.info("🚀 Iniciando análisis EDA para empresa de aceros...")
    
    try:
        eda = SteelCompanyEDA()
        eda.run_complete_eda()
        
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}")
        raise

if __name__ == "__main__":
    main()
