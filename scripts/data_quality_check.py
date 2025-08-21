#!/usr/bin/env python3
"""
Script de verificación de calidad de datos para el pipeline de aceros
Monitorea la integridad y consistencia de los datos procesados
"""

import os
import logging
import pandas as pd
from google.cloud import bigquery
from datetime import datetime, timedelta
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
PROJECT_ID = os.getenv('PROJECT_ID') or 'your-project-id'
DATASET_NAME = 'acero_analysis'

class DataQualityChecker:
    """Clase para verificar calidad de datos"""
    
    def __init__(self):
        """Inicializar cliente BigQuery"""
        try:
            self.client = bigquery.Client(project=PROJECT_ID)
            logger.info(f"✅ Cliente BigQuery inicializado para proyecto: {PROJECT_ID}")
        except Exception as e:
            logger.error(f"❌ Error inicializando BigQuery: {e}")
            raise
    
    def check_data_freshness(self):
        """Verificar frescura de los datos"""
        logger.info("🔍 Verificando frescura de los datos...")
        
        query = f"""
        SELECT 
            MAX(_PARTITIONTIME) as latest_partition,
            CURRENT_TIMESTAMP() as current_time,
            TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(_PARTITIONTIME), HOUR) as hours_since_update
        FROM `{PROJECT_ID}.{DATASET_NAME}.cdo_challenge`
        WHERE _PARTITIONTIME IS NOT NULL
        """
        
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            
            for row in results:
                latest_update = row.latest_partition
                hours_since = row.hours_since_update
                current_time = row.current_time
                
                logger.info(f"📅 Última actualización: {latest_update}")
                logger.info(f"⏰ Hace {hours_since:.1f} horas")
                
                # Verificar si los datos están actualizados (menos de 24 horas)
                if hours_since < 24:
                    logger.info("✅ Datos están actualizados")
                    return True
                else:
                    logger.warning(f"⚠️  Datos desactualizados por {hours_since:.1f} horas")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error verificando frescura: {e}")
            return False
    
    def check_data_completeness(self):
        """Verificar completitud de los datos"""
        logger.info("🔍 Verificando completitud de los datos...")
        
        query = f"""
        SELECT 
            COUNT(*) as total_records,
            COUNTIF(_PARTITIONTIME IS NOT NULL) as valid_timestamps,
            COUNTIF(_FILE_NAME IS NOT NULL) as valid_filenames,
            COUNTIF(_FILE_LOAD_TIME IS NOT NULL) as valid_loadtimes
        FROM `{PROJECT_ID}.{DATASET_NAME}.cdo_challenge`
        """
        
        try:
            query_job = self.client.query(query)
            results = query_job.result()
            
            for row in results:
                total = row.total_records
                valid_timestamps = row.valid_timestamps
                valid_filenames = row.valid_filenames
                valid_loadtimes = row.valid_loadtimes
                
                # Calcular porcentajes de completitud
                timestamp_completeness = (valid_timestamps / total) * 100
                filename_completeness = (valid_filenames / total) * 100
                loadtime_completeness = (valid_loadtimes / total) * 100
                
                logger.info(f"📊 Completitud de datos:")
                logger.info(f"   - Timestamps: {timestamp_completeness:.2f}%")
                logger.info(f"   - Nombres de archivo: {filename_completeness:.2f}%")
                logger.info(f"   - Tiempos de carga: {loadtime_completeness:.2f}%")
                
                # Verificar si la completitud es aceptable (>95%)
                if timestamp_completeness > 95 and filename_completeness > 95:
                    logger.info("✅ Completitud de datos aceptable")
                    return True
                else:
                    logger.warning("⚠️  Completitud de datos por debajo del umbral")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error verificando completitud: {e}")
            return False
    
    def check_data_consistency(self):
        """Verificar consistencia de los datos"""
        logger.info("🔍 Verificando consistencia de los datos...")
        
        query = f"""
        SELECT 
            DATE(_PARTITIONTIME) as date,
            COUNT(*) as daily_records,
            COUNT(DISTINCT _FILE_NAME) as daily_files,
            AVG(COUNT(*)) OVER (ORDER BY DATE(_PARTITIONTIME) ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as moving_avg_7d
        FROM `{PROJECT_ID}.{DATASET_NAME}.cdo_challenge`
        WHERE _PARTITIONTIME IS NOT NULL
        GROUP BY DATE(_PARTITIONTIME)
        ORDER BY date DESC
        LIMIT 30
        """
        
        try:
            query_job = self.client.query(query)
            df = query_job.to_dataframe()
            
            if len(df) == 0:
                logger.warning("⚠️  No hay datos para verificar consistencia")
                return False
            
            # Calcular estadísticas de consistencia
            daily_records_std = df['daily_records'].std()
            daily_records_mean = df['daily_records'].mean()
            coefficient_variation = (daily_records_std / daily_records_mean) * 100
            
            logger.info(f"📈 Consistencia de datos:")
            logger.info(f"   - Promedio diario: {daily_records_mean:,.0f}")
            logger.info(f"   - Desviación estándar: {daily_records_std:,.0f}")
            logger.info(f"   - Coeficiente de variación: {coefficient_variation:.2f}%")
            
            # Verificar si la variación es aceptable (<50%)
            if coefficient_variation < 50:
                logger.info("✅ Consistencia de datos aceptable")
                return True
            else:
                logger.warning("⚠️  Alta variabilidad en los datos diarios")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error verificando consistencia: {e}")
            return False
    
    def check_dbt_models(self):
        """Verificar estado de los modelos dbt"""
        logger.info("🔍 Verificando modelos dbt...")
        
        models_to_check = [
            'stg_cdo_challenge',
            'int_daily_metrics',
            'mart_business_insights'
        ]
        
        results = {}
        
        for model in models_to_check:
            try:
                query = f"""
                SELECT COUNT(*) as record_count
                FROM `{PROJECT_ID}.{DATASET_NAME}.{model}`
                """
                
                query_job = self.client.query(query)
                count_result = query_job.result()
                
                for row in count_result:
                    record_count = row.record_count
                    results[model] = record_count
                    logger.info(f"   - {model}: {record_count:,} registros")
                    
            except Exception as e:
                logger.error(f"❌ Error verificando modelo {model}: {e}")
                results[model] = 0
        
        # Verificar si todos los modelos tienen datos
        all_models_have_data = all(count > 0 for count in results.values())
        
        if all_models_have_data:
            logger.info("✅ Todos los modelos dbt tienen datos")
            return True
        else:
            logger.warning("⚠️  Algunos modelos dbt no tienen datos")
            return False
    
    def generate_quality_report(self):
        """Generar reporte de calidad completo"""
        logger.info("📋 Generando reporte de calidad...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_id': PROJECT_ID,
            'dataset': DATASET_NAME,
            'checks': {}
        }
        
        # Ejecutar todas las verificaciones
        checks = [
            ('data_freshness', self.check_data_freshness),
            ('data_completeness', self.check_data_completeness),
            ('data_consistency', self.check_data_consistency),
            ('dbt_models', self.check_dbt_models)
        ]
        
        for check_name, check_function in checks:
            try:
                result = check_function()
                report['checks'][check_name] = {
                    'status': 'passed' if result else 'failed',
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                report['checks'][check_name] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        # Calcular score general
        passed_checks = sum(1 for check in report['checks'].values() if check['status'] == 'passed')
        total_checks = len(report['checks'])
        quality_score = (passed_checks / total_checks) * 100
        
        report['overall_score'] = quality_score
        report['summary'] = {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': total_checks - passed_checks,
            'quality_score': f"{quality_score:.1f}%"
        }
        
        # Guardar reporte
        os.makedirs('reports', exist_ok=True)
        report_filename = f"reports/data_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str, ensure_ascii=False)
        
        logger.info(f"✅ Reporte de calidad guardado en: {report_filename}")
        
        # Mostrar resumen
        logger.info(f"📊 RESUMEN DE CALIDAD:")
        logger.info(f"   - Score general: {quality_score:.1f}%")
        logger.info(f"   - Verificaciones pasadas: {passed_checks}/{total_checks}")
        
        if quality_score >= 80:
            logger.info("🎉 Calidad de datos EXCELENTE")
        elif quality_score >= 60:
            logger.info("✅ Calidad de datos ACEPTABLE")
        else:
            logger.warning("⚠️  Calidad de datos REQUIERE ATENCIÓN")
        
        return report

def main():
    """Función principal"""
    logger.info("🚀 Iniciando verificación de calidad de datos...")
    
    try:
        checker = DataQualityChecker()
        report = checker.generate_quality_report()
        
        logger.info("🎉 Verificación de calidad completada")
        
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}")
        raise

if __name__ == "__main__":
    main()
