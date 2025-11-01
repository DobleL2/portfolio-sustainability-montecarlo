<!-- markdownlint-disable -->
# 📊 Comparación de Rentabilidades en Instrumentos Financieros Reales

**Trabajo Grupal 1 – Matemática Actuarial**

**Autores:** Luis Lapo, Cristian Ojeda

## 🎯 Objetivo

Evaluar la sostenibilidad de una cartera de inversión inicial de **USD 100,000** bajo distintas estrategias de asignación de activos y rebalanceo, determinando su capacidad para sostener pagos mensuales de **USD 1,200** durante 10 años. El enfoque maximiza la rentabilidad y minimiza el riesgo de agotamiento del capital.

## 📋 Descripción del Proyecto

Este proyecto implementa un sistema completo de simulación Monte Carlo para evaluar diferentes estrategias de inversión. Utiliza datos históricos reales de activos financieros (acciones, bonos, oro y efectivo) para calcular estadísticas y simular múltiples escenarios económicos.

### Características principales:

- 📥 **Descarga automática de datos** desde Yahoo Finance
- 🎲 **Simulación Monte Carlo** con 10,000 iteraciones por cartera y escenario
- 🔄 **Estrategias de rebalanceo** (basadas en tiempo y umbral)
- 📈 **Análisis de escenarios** económicos (base, optimista, pesimista)
- 📊 **Visualizaciones** profesionales de resultados
- 📝 **Notebooks Jupyter** para exploración interactiva
- 💰 **Contribuciones periódicas** y cambios en retiros (décimos sueldos) configurables

## 🏗️ Estructura del Proyecto

```
Trabajo_Grupal_1/
│
├── README.md                      # Este archivo
├── requirements.txt               # Dependencias del proyecto
├── main.ipynb                     # Notebook principal
│
├── config/
│   └── settings.yaml             # Configuración centralizada
│
├── data/
│   ├── raw/                      # Datos históricos descargados
│   ├── processed/                # Datos procesados y estadísticas
│   └── external/                 # Datos externos adicionales
│
├── notebooks/
│   ├── 01_exploracion_datos.ipynb
│   ├── 02_simulacion_montecarlo.ipynb
│   ├── 03_analisis_escenarios.ipynb
│   └── 04_resultados_visualizacion.ipynb
│
├── src/
│   ├── data_preprocessing.py     # Descarga y procesamiento de datos
│   ├── simulation.py             # Simulación Monte Carlo
│   ├── rebalance_strategies.py   # Estrategias de rebalanceo
│   ├── sensitivity_analysis.py   # Análisis de sensibilidad
│   └── visualization.py          # Generación de visualizaciones
│
├── results/
│   ├── figures/                  # Gráficos generados
│   ├── tables/                   # Tablas comparativas
│   └── simulations/              # Resultados de simulaciones
│
├── tests/
│   ├── test_simulation.py
│   ├── test_data_integrity.py
│   └── test_rebalance.py
│
└── reports/
    └── overleaf/
        ├── informe_final.tex       # Informe LaTeX principal
        └── figures/                # Gráficos para compilar en Overleaf
```

## 🚀 Instalación

### Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. **Clonar o descargar el repositorio** (si aplica)

2. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

3. **Verificar instalación:**

```bash
python -c "import pandas, numpy, yfinance, matplotlib; print('✅ Dependencias instaladas correctamente')"
```

## 📖 Uso

### Flujo de trabajo básico

El proyecto está diseñado para ejecutarse en orden:

#### 1. Descargar y procesar datos

```bash
python src/data_preprocessing.py
```

Esto descargará los datos históricos de Yahoo Finance y calculará las estadísticas necesarias para las simulaciones.

#### 2. Ejecutar simulaciones Monte Carlo

```bash
python src/simulation.py
```

**Nota:** Este paso puede tardar varios minutos (dependiendo de la cantidad de iteraciones configuradas).

#### 3. Análisis de sensibilidad

```bash
python src/sensitivity_analysis.py
```

Genera tablas comparativas de resultados.

#### 4. Generar visualizaciones

```bash
python src/visualization.py
```

Crea todos los gráficos y guarda en `results/figures/`.

### Uso con Jupyter Notebooks

También puedes usar los notebooks interactivos:

1. **Iniciar Jupyter:**

```bash
jupyter notebook
```

2. **Abrir `main.ipynb`** para ejecutar todo el flujo, o los notebooks individuales para análisis específicos.

## ⚙️ Configuración

Todos los parámetros del proyecto están centralizados en `config/settings.yaml`. Los principales parámetros incluyen:

- **Capital inicial:** USD 100,000
- **Horizonte de simulación:** 10 años (120 meses)
- **Retiros mensuales:** USD 1,200
- **Iteraciones Monte Carlo:** 10,000 por cartera y escenario
- **Activos:** S&P 500, Bonos del Tesoro, Oro, Efectivo
- **Carteras:** 3 estrategias diferentes de asignación
- **Escenarios económicos:** Base, Optimista, Pesimista
- **Contribuciones periódicas:** Configurables (USD 100/mes por defecto)
- **Retiros adicionales:** Décimos sueldos configurables

Puedes modificar estos valores editando el archivo YAML.

## 📊 Carteras Evaluadas

1. **Cartera 1:** 60% Acciones / 40% Bonos
   - Rebalanceo: Anual

2. **Cartera 2:** 50% Acciones / 30% Bonos / 20% Oro
   - Rebalanceo: Basado en umbral (5%)

3. **Cartera 3:** 70% Acciones / 20% Bonos / 10% Efectivo
   - Rebalanceo: Trimestral

## 🧪 Testing

Ejecutar todos los tests:

```bash
pytest tests/ -v
```

O ejecutar tests individuales:

```bash
pytest tests/test_simulation.py -v
pytest tests/test_data_integrity.py -v
pytest tests/test_rebalance.py -v
```

## 📄 Generación de Reporte

El proyecto genera automáticamente un informe LaTeX completo con todos los resultados:

```bash
python src/generate_report.py
```

El informe se guarda en `reports/overleaf/informe_final.tex` junto con los gráficos necesarios en `reports/overleaf/figures/`. Para compilar el PDF, sube la carpeta `reports/overleaf/` completa a Overleaf.

## 📈 Resultados

Los resultados se guardan automáticamente en:

- **Datos procesados:** `data/processed/`
  - `asset_statistics.csv`: Estadísticas anualizadas de activos
  - `returns.csv`: Retornos históricos consolidados
- **Métricas de simulación:** `results/simulations/metrics_*.csv`
  - Incluye: valores finales, tasas de supervivencia, flujos de caja, contribuciones
- **Historiales de simulación:** `results/simulations/histories_*.csv`
  - Evolución mensual del capital para cada iteración
- **Tablas comparativas:** `results/tables/*.csv`
  - Comparación entre escenarios y carteras
- **Visualizaciones:** `results/figures/*.png`
  - Gráficos de evolución, distribuciones, comparaciones y supervivencia
- **Informe LaTeX:** `reports/overleaf/informe_final.tex`
  - Informe completo con todos los resultados, listo para compilar en Overleaf

## 🔧 Desarrollo

### Estructura del código

- **`src/data_preprocessing.py`:** Maneja descarga de datos y cálculo de estadísticas
- **`src/simulation.py`:** Implementa el motor de simulación Monte Carlo
- **`src/rebalance_strategies.py`:** Define estrategias de rebalanceo
- **`src/sensitivity_analysis.py`:** Compara escenarios y genera métricas
- **`src/visualization.py`:** Crea visualizaciones profesionales
- **`src/generate_report.py`:** Genera informe LaTeX completo con todos los resultados

### Extender el proyecto

Para agregar nuevas carteras o escenarios:

1. Edita `config/settings.yaml`
2. Ejecuta nuevamente las simulaciones

Para agregar nuevas estrategias de rebalanceo:

1. Extiende la clase `RebalanceStrategy` en `src/rebalance_strategies.py`
2. Implementa los métodos requeridos
3. Actualiza `create_rebalance_strategy()` si es necesario

## 📝 Metodología

1. **Recopilación de datos:** Se utilizan datos históricos reales de Yahoo Finance (2015-2025)
2. **Cálculo de estadísticas:** Retornos anualizados y desviaciones estándar por activo
3. **Simulación:** Monte Carlo con distribución normal de retornos (10,000 iteraciones por escenario)
4. **Aplicación de estrategias:** Rebalanceo según reglas definidas (temporal o por umbral)
5. **Flujos de caja:** Incorporación de contribuciones periódicas y retiros adicionales (décimos sueldos)
6. **Análisis:** Comparación de tasas de supervivencia, valores finales y distribuciones de resultados

## 🤝 Contribuciones

Este es un proyecto académico. Para sugerencias o mejoras, por favor contacta al equipo del proyecto.

## 📄 Licencia

Este proyecto es de uso educativo/académico.

## 👥 Autores

**Luis Lapo, Cristian Ojeda**

Trabajo Grupal 1 – Matemática Actuarial

## 📚 Referencias

- Datos financieros: Yahoo Finance
- Metodología: Simulación Monte Carlo para análisis de carteras
- Bibliotecas: pandas, numpy, matplotlib, yfinance, scipy

---

**Última actualización:** 2025


