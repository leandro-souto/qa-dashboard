# Excellure Dashboard

Dashboard interactivo para gestionar y visualizar casos de prueba manuales con reportes Allure automatizados.

## 📋 Descripción

Excellure Dashboard es una herramienta que permite:
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
cd qa-dashboard
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

## ⚙️ Configuración Inicial en GitHub

Después de clonar el repositorio, realiza estos pasos **una sola vez**:

### 1. Habilitar GitHub Pages
1. Ve a tu repositorio en GitHub
2. Settings → Pages
3. Selecciona "Deploy from a branch"
4. Branch: `gh-pages` / Folder: `/ (root)`
5. Click en "Save"

> **Nota**: La rama `gh-pages` se crea automáticamente en el primer push después de que el workflow se ejecute.

### 2. Verificar que GitHub Actions esté habilitado
1. Ve a Settings → Actions → General
2. Asegúrate que "Allow all actions and reusable workflows" esté seleccionado
3. Los workflows en `.github/workflows/` deben estar activos

### 3. Configurar webhook de Teams (opcional)
Si quieres recibir alertas semanales en Teams:

1. Ve a Settings → Secrets and variables → Actions
2. Click en "New repository secret"
3. Name: `TEAMS_WEBHOOK_URL`
4. Value: Tu URL de webhook de Teams
5. Click en "Add secret"

> Para obtener la URL del webhook: Teams → Configurar conector → Webhook entrante

### 4. Primer push para generar el reporte
```bash
git add .
git commit -m "Initial setup"
git push origin main
```

El workflow se ejecutará automáticamente. En 2-3 minutos tu reporte estará disponible en:
```
https://<tu-usuario>.github.io/qa-dashboard/
```

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
| Description | Descripción detallada | Verificar que el usuario puede ingresar... |
| Steps | Pasos de ejecución | 1. Abrir login\n2. Ingresar credenciales... |
| Expected Result | Resultado esperado | Usuario autenticado correctamente |
| Test Data | Datos de prueba | user@example.com, password123 |
| Status | Estado actual | PASSED, FAILED, PENDING, BLOCKED, SKIPPED |
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

### Paso 5: Actualizar datos y regenerar (Flujo rápido)

Cuando actualices el Excel, ejecuta:

```bash
# 1. Convertir Excel a Allure
python scripts/excel_to_allure_updated.py

# 2. Hacer commit y push (dispara el workflow automáticamente)
git add .
git commit -m "Update test cases"
git push origin main
```

El workflow `generate-report.yml` se ejecutará automáticamente y publicará el reporte en GitHub Pages en 2-3 minutos.

## 🤖 Automatización con GitHub Actions

### Workflow: Generar Reporte Allure

El workflow `generate-report.yml` se ejecuta automáticamente cuando:
- Haces push a cambios en archivos `.xlsx` en `test_data/`
- Ejecutas manualmente el workflow desde GitHub Actions

**Pasos del workflow:**
1. ✅ Checkout del código
2. ✅ Instalación de dependencias Python
3. ✅ Conversión de Excel a Allure
4. ✅ Instalación de Allure CLI
5. ✅ Generación del reporte
6. ✅ Publicación en GitHub Pages

**Ver reporte en línea:**
```
https://FalonSt.github.io/qa-dashboard/
```

### Workflow: Alertas Semanales en Teams

El workflow `send-teams-alert.yml` se ejecuta automáticamente:
- **Todos los viernes a las 18:00 (UTC-3)**
- Envía un resumen de métricas por categoría a Teams

**Configuración requerida:**
1. Ve a GitHub → Settings → Secrets and variables → Actions
2. Crea un secret llamado `TEAMS_WEBHOOK_URL` con la URL del webhook de Teams
3. El workflow enviará automáticamente:
   - Total de casos por categoría (Functional TC, Non functional TC)
   - Casos pasados, fallidos y pendientes
   - Tasa de éxito general
   - Link al reporte completo en Allure

**Prueba manual:**
```bash
# Ve a GitHub Actions → "Send Teams Weekly Alert" → "Run workflow"
```

## 📊 Estructura del Proyecto

```
qa-dashboard/
├── test_data/
│   └── test_cases_Hoopit.xlsx           # Archivo con casos de prueba
├── scripts/
│   ├── excel_to_allure_updated.py       # Script de conversión Excel → Allure
│   └── send_teams_alert.py              # Script de alertas a Teams
├── allure-results/                      # Resultados generados (JSON)
├── allure-report/                       # Reporte HTML generado
├── .github/
│   └── workflows/
│       ├── generate-report.yml          # Workflow: Generar reporte Allure
│       └── send-teams-alert.yml         # Workflow: Alertas semanales a Teams
├── requirements.txt                     # Dependencias Python
└── README.md                            # Este archivo
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
cd qa-dashboard
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
