# QA Dashboard

Dashboard interactivo para gestionar y visualizar casos de prueba manuales con reportes Allure automatizados.

## 📋 Descripción

QA Dashboard es una herramienta que permite:
- 📊 Convertir casos de prueba desde Excel a formato Allure Report
- 📈 Generar reportes visuales interactivos automáticamente
- 🔄 Automatizar la publicación de reportes en GitHub Pages
- 📱 Visualizar métricas de calidad en tiempo real
- 🏷️ Organizar pruebas por categoría, prioridad y estado

## 🚀 Características

### Conversión Excel → Allure
- Importa casos de prueba desde archivos `.xlsx`
- Mapeo automático de columnas (ID, Title, Status, Priority, etc.)
- Soporte para múltiples estados: PENDING, PASSED, FAILED, BLOCKED, SKIPPED
- Generación de categorías y métricas automáticas

### Reportes Interactivos
- Dashboard visual con estadísticas en tiempo real
- Filtros por estado, prioridad, tipo de prueba
- Historial de ejecuciones
- Descarga de reportes en PDF
- Gráficos de tendencias

### Automatización CI/CD
- Workflow de GitHub Actions automático
- Publicación en GitHub Pages
- Actualización de reportes con cada cambio
- Sin requiere configuración manual

## 📦 Requisitos

- Python 3.11+
- Node.js (para Allure CLI)
- Java 17+ (para generar reportes)
- Git

## 🔧 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/FalonSt/qa-dashboard.git
cd qa-dashboard/qa-dashboard
```

### 2. Instalar dependencias Python
```bash
pip install -r requirements.txt
```

### 3. Instalar Allure CLI
```bash
npm install -g allure-commandline
```

### 4. Instalar Java (si no lo tienes)
Descarga desde: https://adoptium.net/temurin/releases/?version=17

## 📝 Uso

### Paso 1: Preparar datos de prueba

Crea un archivo Excel (`test_cases.xlsx`) en la carpeta `test_data/` con las siguientes columnas:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| ID | Identificador único | TC-001 |
| Title | Nombre del caso | Login con credenciales válidas |
| Category | Categoría/Feature | Autenticación |
| Priority | Prioridad | High, Medium, Low, Critical |
| Type | Tipo de prueba | Functional, Regression, Smoke |
| Status | Estado actual | PASSED, FAILED, PENDING, BLOCKED, SKIPPED |
| Description | Descripción detallada | Verificar que el usuario puede ingresar... |
| Steps | Pasos de ejecución | 1. Abrir login\n2. Ingresar credenciales... |
| Expected Result | Resultado esperado | Usuario autenticado correctamente |
| Test Data | Datos de prueba | user@example.com, password123 |
| Linked Reports/Notes | Notas o links | JIRA-123, Bug encontrado en... |

### Paso 2: Convertir Excel a Allure

```bash
python scripts/excel_to_allure_updated.py
```

Este comando:
- Lee el archivo Excel
- Convierte cada caso a formato Allure JSON
- Genera categorías automáticas
- Crea archivo de ambiente

### Paso 3: Generar reporte

```bash
allure generate allure-results -o allure-report --clean
```

### Paso 4: Ver reporte

```bash
allure open allure-report
```

Se abrirá automáticamente en tu navegador.

## 🤖 Automatización con GitHub Actions

El workflow `generate-report.yml` se ejecuta automáticamente cuando:
- Haces push a cambios en archivos `.xlsx` en `test_data/`
- Ejecutas manualmente el workflow desde GitHub Actions

### Pasos del workflow:
1. ✅ Checkout del código
2. ✅ Instalación de dependencias Python
3. ✅ Conversión de Excel a Allure
4. ✅ Instalación de Allure CLI
5. ✅ Generación del reporte
6. ✅ Publicación en GitHub Pages

### Ver reporte en línea

Una vez que el workflow termine, accede a:
```
https://FalonSt.github.io/qa-dashboard/
```

## 📊 Estructura del Proyecto

```
qa-dashboard/
├── test_data/
│   └── test_cases_Hoopit.xlsx      # Archivo con casos de prueba
├── scripts/
│   └── excel_to_allure_updated.py  # Script de conversión
├── allure-results/                 # Resultados generados (JSON)
├── allure-report/                  # Reporte HTML generado
├── .github/
│   └── workflows/
│       └── generate-report.yml     # Workflow de GitHub Actions
├── requirements.txt                # Dependencias Python
└── README.md                        # Este archivo
```

## 📈 Estadísticas y Métricas

El reporte genera automáticamente:
- **Pass Rate**: Porcentaje de casos ejecutados exitosamente
- **Execution Rate**: Porcentaje de casos ejecutados vs pendientes
- **Status Distribution**: Desglose por estado (PASSED, FAILED, PENDING, etc.)
- **Priority Distribution**: Casos por nivel de prioridad
- **Type Distribution**: Casos por tipo de prueba

## 🔍 Estados Soportados

| Estado | Icono | Descripción |
|--------|-------|-------------|
| PASSED | ✅ | Caso ejecutado exitosamente |
| FAILED | ❌ | Caso que falló |
| PENDING | ⏸️ | Caso pendiente de ejecutar |
| BLOCKED | 🚫 | Caso bloqueado por dependencias |
| SKIPPED | ⏭️ | Caso omitido intencionalmente |

## 🎯 Prioridades Soportadas

- **Critical**: Crítica - Bloquea el release
- **High**: Alta - Importante
- **Medium**: Media - Normal
- **Low**: Baja - Menor importancia

## 🛠️ Troubleshooting

### Error: JAVA_HOME no configurado
```bash
# Windows
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.17.10-hotspot"

# Linux/Mac
export JAVA_HOME=/usr/libexec/java_home -v 17
```

### Error: requirements.txt no encontrado
Asegúrate de estar en el directorio correcto:
```bash
cd qa-dashboard/qa-dashboard
pip install -r requirements.txt
```

### Error: Archivo Excel no encontrado
Verifica que el archivo `.xlsx` esté en la carpeta `test_data/`:
```bash
ls test_data/
```

## 📚 Documentación Adicional

- [Allure Report Docs](https://docs.qameta.io/allure/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [GitHub Pages Docs](https://docs.github.com/en/pages)

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

## 👤 Autor

**FalonSt** - QA Engineer

## 📞 Soporte

Para reportar bugs o solicitar features, abre un issue en GitHub.

---

**Última actualización**: Enero 2026
