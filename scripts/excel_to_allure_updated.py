import pandas as pd
import json
import uuid
import os
from datetime import datetime
from pathlib import Path
import hashlib

class ExcelToAllureConverter:
    """
    Convierte casos de prueba manuales de Excel a formato Allure Report.
    """
    
    # Mapeo de prioridades Excel → Allure
    PRIORITY_MAP = {
        'Critical': 'critical',
        'High': 'high',
        'Medium': 'normal',
        'Low': 'minor',
        'CRITICAL': 'critical',
        'HIGH': 'high',
        'MEDIUM': 'normal',
        'LOW': 'minor'
    }
    
    # Mapeo de estados Excel → Allure (ACTUALIZADOS)
    STATUS_MAP = {
        'PENDING': 'unknown',
        'PASSED': 'passed',
        'FAILED': 'failed',
        'BLOCKED': 'broken',
        'SKIPPED': 'skipped',
        # Alternativas en minúsculas
        'Pending': 'unknown',
        'Passed': 'passed',
        'Failed': 'failed',
        'Blocked': 'broken',
        'Skipped': 'skipped',
        # Por si vienen sin formato
        'pending': 'unknown',
        'passed': 'passed',
        'failed': 'failed',
        'blocked': 'broken',
        'skipped': 'skipped'
    }
    
    def __init__(self, excel_path, output_dir='allure-results'):
        self.excel_path = excel_path
        self.output_dir = output_dir
        self.timestamp = int(datetime.now().timestamp() * 1000)
        
        # Crear directorio de salida
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
    def read_excel(self):
        """Lee el archivo Excel con casos de prueba desde múltiples tabs"""
        try:
            # Leer todas las hojas disponibles
            excel_file = pd.ExcelFile(self.excel_path)
            sheet_names = excel_file.sheet_names
            print(f"📋 Hojas encontradas: {sheet_names}")
            
            # Listas de tabs a buscar
            tabs_to_read = ['Functional TC', 'Non functional TC']
            dfs = []
            
            for tab in tabs_to_read:
                if tab in sheet_names:
                    df_tab = pd.read_excel(self.excel_path, sheet_name=tab)
                    dfs.append(df_tab)
                    print(f"✅ Tab '{tab}' cargada: {len(df_tab)} casos encontrados")
                else:
                    print(f"⚠️ Tab '{tab}' no encontrada")
            
            if not dfs:
                print(f"❌ Error: No se encontraron las tabs esperadas")
                raise ValueError("Tabs 'Functional TC' o 'Non Functional TC' no encontradas")
            
            # Combinar todos los DataFrames
            df_combined = pd.concat(dfs, ignore_index=True)
            print(f"✅ Excel cargado: {len(df_combined)} casos de prueba encontrados en total")
            return df_combined
        except FileNotFoundError:
            print(f"❌ Error: Archivo no encontrado: {self.excel_path}")
            raise
        except Exception as e:
            print(f"❌ Error leyendo Excel: {e}")
            raise
    
    def generate_uuid(self, test_id):
        """Genera UUID consistente basado en test ID"""
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, test_id))
    
    def parse_steps(self, steps_text):
        """Parsea los pasos de prueba desde texto"""
        if pd.isna(steps_text):
            return []
        
        steps = []
        lines = str(steps_text).split('\n')
        
        for line in lines:
            line = line.strip()
            if line:
                # Remover numeración si existe (1., 2., etc)
                step_text = line.lstrip('0123456789.-) ')
                steps.append({
                    "name": step_text,
                    "status": "passed",
                    "start": self.timestamp,
                    "stop": self.timestamp + 100
                })
        
        return steps
    
    def create_allure_result(self, row):
        """Crea un resultado de prueba en formato Allure"""
        
        # Obtener valores con defaults
        test_id = str(row.get('ID', f"TC{uuid.uuid4().hex[:6]}"))
        title = str(row.get('Title', 'Sin título'))
        category = str(row.get('Category', 'General'))
        priority = str(row.get('Priority', 'Medium'))
        test_type = str(row.get('Type', 'Functional'))
        description = str(row.get('Description', ''))
        steps_text = row.get('Steps', '')
        expected = str(row.get('Expected Result', ''))
        test_data = str(row.get('Test Data', ''))
        status_raw = str(row.get('Status', 'PENDING'))
        notes = str(row.get('Linked Reports/Notes', ''))
        
        # Mapear estado - ACTUALIZADO
        status = self.STATUS_MAP.get(status_raw, 'unknown')
        
        # Mapear prioridad
        severity = self.PRIORITY_MAP.get(priority, 'normal')
        
        # Parsear pasos
        steps = self.parse_steps(steps_text)
        
        # Crear descripción enriquecida
        full_description = f"{description}\n\n"
        if expected and expected != 'nan':
            full_description += f"**Resultado Esperado:**\n{expected}\n\n"
        if test_data and test_data != 'nan':
            full_description += f"**Datos de Prueba:**\n{test_data}\n\n"
        if notes and notes != 'nan':
            full_description += f"**Notas:**\n{notes}"
        
        # Generar UUID consistente
        test_uuid = self.generate_uuid(test_id)
        history_id = hashlib.md5(test_id.encode()).hexdigest()
        
        # Estructura JSON de Allure
        allure_result = {
            "uuid": test_uuid,
            "historyId": history_id,
            "name": title,
            "fullName": f"{category}.{test_id}",
            "status": status,
            "statusDetails": {
                "known": False,
                "muted": False,
                "flaky": False
            },
            "start": self.timestamp,
            "stop": self.timestamp + 1000,
            "labels": [
                {"name": "feature", "value": category},
                {"name": "severity", "value": severity},
                {"name": "tag", "value": test_type},
                {"name": "testId", "value": test_id},
                {"name": "testType", "value": "manual"},
                {"name": "suite", "value": category}
            ],
            "links": [],
            "parameters": []
        }
        
        # Agregar descripción si existe
        if description and description != 'nan':
            allure_result["description"] = full_description
            allure_result["descriptionHtml"] = full_description.replace('\n', '<br>')
        
        # Agregar pasos si existen
        if steps:
            allure_result["steps"] = steps
        
        # Agregar datos de prueba como parámetros
        if test_data and test_data != 'nan':
            for param in str(test_data).split('\n'):
                if ':' in param:
                    key, value = param.split(':', 1)
                    allure_result["parameters"].append({
                        "name": key.strip(),
                        "value": value.strip()
                    })
        
        # Agregar notas como links si contienen JIRA, BUG, etc
        if notes and notes != 'nan':
            notes_str = str(notes)
            if 'JIRA-' in notes_str or 'BUG' in notes_str or 'http' in notes_str:
                allure_result["links"].append({
                    "type": "issue",
                    "name": notes_str,
                    "url": notes_str if notes_str.startswith('http') else ""
                })
        
        return allure_result, test_uuid
    
    def save_result(self, result, test_uuid):
        """Guarda el resultado en formato JSON de Allure"""
        filename = f"{test_uuid}-result.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def generate_categories(self, df):
        """Genera archivo de categorías para Allure - ACTUALIZADO"""
        categories = [
            {
                "name": "🔴 Product Defects (Failed)",
                "description": "Tests que fallaron - bugs encontrados en el producto",
                "matchedStatuses": ["failed"]
            },
            {
                "name": "🚫 Blocked Tests",
                "description": "Tests bloqueados por dependencias o ambiente",
                "matchedStatuses": ["broken"]
            },
            {
                "name": "⏸️ Pending Execution",
                "description": "Tests pendientes de ejecutar",
                "matchedStatuses": ["unknown"]
            },
            {
                "name": "⏭️ Skipped Tests",
                "description": "Tests omitidos intencionalmente",
                "matchedStatuses": ["skipped"]
            }
        ]
        
        # Categorías por tipo de prueba
        if 'Type' in df.columns:
            test_types = df['Type'].unique()
            for test_type in test_types:
                if pd.notna(test_type):
                    categories.append({
                        "name": f"📋 {test_type} Tests",
                        "matchedStatuses": [],
                        "messageRegex": f".*{test_type}.*"
                    })
        
        # Categorías por prioridad
        categories.extend([
            {
                "name": "🔥 Critical Priority",
                "matchedStatuses": [],
                "messageRegex": ".*Critical.*"
            },
            {
                "name": "⚡ High Priority",
                "matchedStatuses": [],
                "messageRegex": ".*High.*"
            }
        ])
        
        # Guardar categories.json
        categories_path = os.path.join(self.output_dir, 'categories.json')
        with open(categories_path, 'w', encoding='utf-8') as f:
            json.dump(categories, f, indent=2)
        
        print(f"✅ Categorías generadas: {categories_path}")
        return categories_path
    
    def generate_environment(self):
        """Genera archivo environment.properties"""
        env_content = f"""Test.Environment=Dev
Execution.Date={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Tester=Falon Strada
Test.Type=Manual
Report.Version=1.0
Status.Values=PENDING, PASSED, FAILED, BLOCKED, SKIPPED
"""
        env_path = os.path.join(self.output_dir, 'environment.properties')
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Environment generado: {env_path}")
        return env_path
    
    def convert(self):
        """Proceso principal de conversión"""
        print("\n🚀 Iniciando conversión Excel → Allure\n")
        print("📊 Status soportados: PENDING, PASSED, FAILED, BLOCKED, SKIPPED\n")
        
        # Leer Excel
        df = self.read_excel()
        
        # Validar columnas requeridas
        required_cols = ['ID', 'Title', 'Status']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"❌ Error: Columnas faltantes en Excel: {missing_cols}")
            return False
        
        # Convertir cada caso de prueba
        converted = 0
        status_icons = {
            'unknown': '⏸️',    # PENDING
            'passed': '✅',     # PASSED
            'failed': '❌',     # FAILED
            'broken': '🚫',     # BLOCKED
            'skipped': '⏭️'     # SKIPPED
        }
        
        for idx, row in df.iterrows():
            try:
                result, test_uuid = self.create_allure_result(row)
                filepath = self.save_result(result, test_uuid)
                converted += 1
                
                status_emoji = status_icons.get(result['status'], '❓')
                status_label = row.get('Status', 'Unknown')
                print(f"{status_emoji} [{status_label}] {row.get('ID')}: {row.get('Title')}")
            except Exception as e:
                print(f"❌ Error procesando {row.get('ID', idx)}: {e}")
        
        # Generar archivos adicionales
        self.generate_categories(df)
        self.generate_environment()
        
        # Resumen
        print(f"\n✅ Conversión completada: {converted}/{len(df)} casos convertidos")
        print(f"📁 Resultados guardados en: {self.output_dir}")
        
        # Estadísticas
        if 'Status' in df.columns:
            stats = df['Status'].value_counts().to_dict()
            print("\n📊 Estadísticas por Status:")
            for status, count in stats.items():
                icon = {
                    'PENDING': '⏸️',
                    'PASSED': '✅',
                    'FAILED': '❌',
                    'BLOCKED': '🚫',
                    'SKIPPED': '⏭️'
                }.get(status, '❓')
                percentage = (count / len(df) * 100)
                print(f"   {icon} {status}: {count} ({percentage:.1f}%)")
            
            # Calcular métricas
            passed = stats.get('PASSED', 0)
            failed = stats.get('FAILED', 0)
            blocked = stats.get('BLOCKED', 0)
            executed = passed + failed + blocked
            
            if executed > 0:
                pass_rate = (passed / executed * 100)
                print(f"\n📈 Métricas:")
                print(f"   Pass Rate: {pass_rate:.1f}%")
                print(f"   Executed: {executed}/{len(df)} ({executed/len(df)*100:.1f}%)")
        
        return True

def main():
    """Función principal"""
    import sys
    
    # Configuración - FLEXIBLE con nombre de archivo
    # Puedes especificar el nombre como argumento o usar el default
    if len(sys.argv) > 1:
        EXCEL_FILE = sys.argv[1]
    else:
        # Buscar cualquier archivo .xlsx en test_data/
        import glob
        excel_files = glob.glob('test_data/*.xlsx')
        
        if not excel_files:
            print("❌ Error: No se encontró ningún archivo Excel en test_data/")
            print("   Por favor, coloca tu archivo Excel en la carpeta test_data/")
            return False
        
        if len(excel_files) > 1:
            print(f"⚠️  Se encontraron múltiples archivos Excel:")
            for i, file in enumerate(excel_files, 1):
                print(f"   {i}. {file}")
            print(f"\n✅ Usando: {excel_files[0]}")
        
        EXCEL_FILE = excel_files[0]
    
    OUTPUT_DIR = 'allure-results'
    
    print(f"\n📂 Archivo Excel: {EXCEL_FILE}")
    
    # Verificar que existe el Excel
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ Error: No se encontró el archivo {EXCEL_FILE}")
        return False
    
    # Convertir
    converter = ExcelToAllureConverter(EXCEL_FILE, OUTPUT_DIR)
    success = converter.convert()
    
    if success:
        print("\n✅ ¡Listo! Ahora puedes generar el reporte Allure.")
        print("\n📖 Comandos siguientes:")
        print("   1. Instalar Allure: npm install -g allure-commandline")
        print("   2. Generar reporte: allure generate allure-results -o allure-report --clean")
        print("   3. Ver reporte: allure open allure-report")
    
    return success

if __name__ == "__main__":
    main()
