import json
import requests
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

def extract_metrics_by_category():
    """Extrae métricas del Excel por categoría (Functional vs Non functional)"""
    try:
        excel_path = Path('test_data/test_cases_Hoopit.xlsx')
        
        if not excel_path.exists():
            print(f"❌ Archivo no encontrado: {excel_path}")
            return None
        
        # Leer ambas tabs
        tabs = {
            'Functional TC': pd.read_excel(excel_path, sheet_name='Functional TC'),
            'Non functional TC': pd.read_excel(excel_path, sheet_name='Non functional TC')
        }
        
        metrics = {}
        
        for category, df in tabs.items():
            # Encontrar columna de Status (generalmente contiene "Status" en el nombre)
            status_col = None
            for col in df.columns:
                if 'status' in col.lower():
                    status_col = col
                    break
            
            total = len(df)
            passed = 0
            failed = 0
            pending = 0
            
            if status_col:
                passed = len(df[df[status_col].astype(str).str.upper() == 'PASSED'])
                failed = len(df[df[status_col].astype(str).str.upper() == 'FAILED'])
                pending = len(df[df[status_col].astype(str).str.upper() == 'PENDING'])
            
            pass_rate = (passed / total * 100) if total > 0 else 0
            
            metrics[category] = {
                'total': total,
                'passed': passed,
                'failed': failed,
                'pending': pending,
                'pass_rate': round(pass_rate, 2)
            }
            
            print(f"✅ {category}: Total={total}, Passed={passed}, Failed={failed}, Pending={pending}")
        
        return metrics
    except Exception as e:
        print(f"❌ Error extrayendo métricas: {e}")
        import traceback
        traceback.print_exc()
        return None

def send_teams_notification(webhook_url, metrics):
    """Envía notificación a Teams con resumen por categoría"""
    if not metrics:
        print("❌ No hay métricas para enviar")
        return False
    
    # Calcular totales
    total_cases = sum(m['total'] for m in metrics.values())
    total_passed = sum(m['passed'] for m in metrics.values())
    total_failed = sum(m['failed'] for m in metrics.values())
    total_pending = sum(m['pending'] for m in metrics.values())
    overall_pass_rate = (total_passed / total_cases * 100) if total_cases > 0 else 0
    
    # Determinar color según pass rate general
    if overall_pass_rate >= 80:
        color = "28a745"  # Verde
        status = "✅ EXITOSO"
    elif overall_pass_rate >= 60:
        color = "ffc107"  # Amarillo
        status = "⚠️ ADVERTENCIA"
    else:
        color = "dc3545"  # Rojo
        status = "❌ CRÍTICO"
    
    # Construir tabla de categorías
    category_facts = []
    for category, data in metrics.items():
        category_facts.append({
            "name": f"📋 {category}",
            "value": f"Total: {data['total']} | ✅ {data['passed']} | ❌ {data['failed']} | ⏳ {data['pending']} | {data['pass_rate']}%"
        })
    
    # Crear mensaje para Teams
    payload = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": f"Reporte Semanal - {status}",
        "themeColor": color,
        "sections": [
            {
                "activityTitle": "📊 Reporte Semanal de Pruebas - Allure",
                "activitySubtitle": f"Semana del {datetime.now().strftime('%d/%m/%Y')}",
                "facts": [
                    {
                        "name": "📈 Resumen General",
                        "value": f"Total: {total_cases} | ✅ {total_passed} | ❌ {total_failed} | ⏳ {total_pending}"
                    },
                    {
                        "name": "🎯 Tasa de Éxito General",
                        "value": f"{overall_pass_rate}%"
                    }
                ] + category_facts,
                "markdown": True
            }
        ],
        "potentialAction": [
            {
                "@type": "OpenUri",
                "name": "Ver Reporte Completo en Allure",
                "targets": [
                    {
                        "os": "default",
                        "uri": "https://falonst.github.io/qa-dashboard/"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code in [200, 201]:
            print("✅ Notificación enviada a Teams exitosamente")
            return True
        else:
            print(f"❌ Error al enviar notificación: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error enviando notificación: {e}")
        return False

if __name__ == "__main__":
    webhook_url = os.getenv('TEAMS_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ Error: TEAMS_WEBHOOK_URL no está configurada")
        exit(1)
    
    metrics = extract_metrics_by_category()
    if metrics:
        send_teams_notification(webhook_url, metrics)
    else:
        print("❌ No se pudieron extraer métricas")
        exit(1)
