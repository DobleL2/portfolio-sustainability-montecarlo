<!-- markdownlint-disable -->
# 📊 Explicación de los Gráficos del Proyecto

Este documento explica el significado y la interpretación de cada tipo de gráfico generado en el proyecto de simulación de carteras de inversión.

---

## 📈 1. Gráficos de Evolución del Capital (Individual)

**Archivos:** `evolution_{cartera}_{escenario}.png`  
**Total:** 9 gráficos (3 carteras × 3 escenarios)

### ¿Qué muestran?

Estos gráficos muestran cómo evoluciona el valor de una cartera específica a lo largo del tiempo (120 meses = 10 años), basándose en miles de simulaciones Monte Carlo.

### Elementos del gráfico:

- **Líneas grises transparentes**: Representan caminos individuales de simulaciones (ejemplos de escenarios posibles). Muestran la variabilidad de resultados.

- **Línea azul sólida (Mediana)**: El valor que separa el 50% superior del 50% inferior de todas las simulaciones en cada mes. Es un valor central robusto.

- **Línea roja punteada (Media)**: El promedio de todos los valores de las simulaciones en cada mes.

- **Banda azul oscura (IQR - Rango Intercuartílico)**: Zona sombreada que contiene el 50% central de las simulaciones (entre el percentil 25 y 75). Es donde se espera que caiga la mayoría de los resultados.

- **Banda azul clara (Rango 5-95%)**: Zona más amplia que contiene el 90% de las simulaciones (entre el percentil 5 y 95). Muestra el rango probable de resultados.

- **Línea verde punteada (Capital inicial)**: Marca el valor inicial de $100,000. Ayuda a ver si la cartera crece o disminuye respecto al capital inicial.

- **Línea roja (Quiebra)**: Marca el valor $0. Si una simulación cruza esta línea, significa que la cartera se agotó antes de completar los 10 años.

### ¿Cómo interpretarlo?

- **Tendencia ascendente**: La cartera está creciendo, probablemente generando más que los retiros mensuales.
- **Tendencia descendente**: La cartera se está consumiendo más rápido de lo que genera retornos.
- **Ancho de las bandas**: Mayor ancho = mayor incertidumbre y volatilidad.
- **Cruce de la línea de quiebra**: Si muchas simulaciones cruzan $0, significa alto riesgo de agotar el capital.

---

## 📊 2. Gráficos de Comparación de Evolución del Capital

**Archivos:** `evolution_comparison_{escenario}.png`  
**Total:** 3 gráficos (uno por escenario: base, optimistic, pessimistic)

### ¿Qué muestran?

Estos gráficos comparan simultáneamente las tres carteras de inversión bajo el mismo escenario económico, permitiendo ver cuál estrategia funciona mejor a lo largo del tiempo.

### Elementos del gráfico:

- **Líneas de colores diferentes**: Cada color representa una cartera diferente:
  - Cartera 1: 60% Acciones / 40% Bonos
  - Cartera 2: 50% Acciones / 30% Bonos / 20% Oro
  - Cartera 3: 70% Acciones / 20% Bonos / 10% Efectivo

- **Líneas gruesas**: Representan la mediana (percentil 50) de cada cartera.

- **Bandas sombreadas**: Representan el rango de confianza del 90% (percentil 5-95%) para cada cartera.

### ¿Cómo interpretarlo?

- **Comparación directa**: Permite ver qué cartera mantiene mejor el capital a lo largo del tiempo.
- **Separación entre líneas**: Mayor separación = mayor diferencia en el desempeño.
- **Intersecciones**: Si las líneas se cruzan, significa que en diferentes momentos del tiempo, diferentes carteras tienen mejor rendimiento.
- **Bandas más estrechas**: Indican menor incertidumbre en los resultados.

---

## 📉 3. Gráfico de Comparación de Tasas de Supervivencia

**Archivo:** `comparison_survival_rate.png`

### ¿Qué muestran?

Este gráfico muestra el porcentaje de simulaciones donde cada cartera logró mantener capital suficiente para completar los 10 años de retiros mensuales, comparado entre diferentes escenarios económicos.

### Elementos del gráfico:

- **Barras agrupadas**: Cada grupo de barras representa una cartera.
- **Colores diferentes**: Cada color representa un escenario económico:
  - **Base**: Condiciones económicas normales
  - **Optimistic**: Condiciones económicas favorables (baja inflación, bajos costos)
  - **Pessimistic**: Condiciones económicas adversas (alta inflación, altos costos)

- **Altura de las barras**: Representa el porcentaje de supervivencia (0-100%).

### ¿Cómo interpretarlo?

- **Barras más altas = mejor**: Mayor probabilidad de que la cartera sobreviva los 10 años.
- **Comparación entre escenarios**: Muestra qué tan sensible es cada cartera a las condiciones económicas.
- **Comparación entre carteras**: Permite identificar qué estrategia es más robusta.

**Ejemplo**: Si una cartera tiene 95% en base y 80% en pesimista, es relativamente resistente. Si tiene 90% en base y 30% en pesimista, es muy sensible a malas condiciones.

---

## 💰 4. Gráfico de Comparación de Valores Finales

**Archivo:** `comparison_final_values.png`

### ¿Qué muestran?

Este gráfico compara el valor final promedio (después de 10 años) de cada cartera bajo diferentes escenarios económicos.

### Elementos del gráfico:

- Similar al gráfico de supervivencia, pero muestra **valores monetarios** (USD) en lugar de porcentajes.
- Muestra cuánto capital queda en promedio al final del período de 10 años.

### ¿Cómo interpretarlo?

- **Barras más altas = más capital restante**: La cartera conservó más dinero.
- **Valores negativos o cerca de cero**: La cartera está agotada o muy cerca de agotarse.
- **Diferencia entre escenarios**: Muestra el impacto económico en el capital final.

**Nota importante**: Una cartera puede tener alta tasa de supervivencia pero bajo valor final, o viceversa. Ambos son importantes:
- **Supervivencia alta**: Probabilidad de no quebrar.
- **Valor final alto**: Capital restante para continuar después de los 10 años.

---

## 📊 5. Gráficos de Distribución de Valores Finales

**Archivos:** `distribution_{cartera}_{escenario}.png`  
**Total:** 9 gráficos (3 carteras × 3 escenarios)

### ¿Qué muestran?

Estos gráficos muestran la distribución de los valores finales de la cartera después de 10 años, basados en todas las simulaciones realizadas.

### Elementos del gráfico:

El gráfico tiene dos paneles:

**Panel izquierdo - Histograma:**
- **Barras**: Frecuencia (número de simulaciones) que terminaron con cada rango de valores.
- **Línea roja punteada**: Valor medio (promedio).
- **Línea verde punteada**: Mediana (valor que divide las simulaciones en dos mitades iguales).

**Panel derecho - Box Plot:**
- **Caja**: Contiene el 50% central de los valores (entre percentil 25 y 75).
- **Línea dentro de la caja**: Mediana.
- **Bigotes**: Extensión hasta el percentil 5 y 95.
- **Puntos**: Valores atípicos (outliers).

### ¿Cómo interpretarlo?

- **Distribución hacia la derecha**: Más simulaciones terminaron con valores altos = buena señal.
- **Distribución hacia la izquierda o en cero**: Muchas simulaciones terminaron con poco o nada = riesgo alto.
- **Distribución amplia**: Alta variabilidad = alta incertidumbre en los resultados.
- **Distribución estrecha**: Resultados más predecibles.
- **Mediana vs Media**: Si la mediana está muy a la izquierda de la media, hay algunos valores muy altos que "inflan" el promedio.

**Ejemplo**: Si el histograma muestra un pico grande en $0, significa que muchas simulaciones resultaron en quiebra.

---

## ⏱️ 6. Gráficos de Probabilidad de Supervivencia

**Archivos:** `survival_{cartera}_{escenario}.png`  
**Total:** 9 gráficos (3 carteras × 3 escenarios)

### ¿Qué muestran?

Estos gráficos muestran la distribución de cuántos meses sobrevivió cada simulación antes de agotar el capital (o completar los 10 años).

### Elementos del gráfico:

- **Barras del histograma**: Muestran cuántas simulaciones sobrevivieron exactamente X meses.
- **Línea verde vertical**: Marca los 120 meses (10 años completos = éxito total).
- **Línea roja vertical**: Marca el promedio de meses sobrevividos.
- **Tasa de supervivencia**: Muestra el porcentaje de simulaciones que completaron los 10 años.

### ¿Cómo interpretarlo?

- **Pico cerca de 120 meses**: La mayoría de simulaciones completaron el período = buena señal.
- **Pico cerca de 0-30 meses**: Muchas simulaciones quebraron temprano = muy malo.
- **Distribución uniforme**: Riesgo distribuido a lo largo del tiempo.
- **Tasa de supervivencia**: El porcentaje muestra directamente la probabilidad de éxito.

**Ejemplo**: 
- Tasa de supervivencia del 95% = Solo 5 de cada 100 simulaciones fallaron.
- Tasa de supervivencia del 60% = 40 de cada 100 simulaciones fallaron = riesgo significativo.

---

## 🎯 Resumen: ¿Qué buscar en cada gráfico?

### Para evaluar **SEGURIDAD** (probabilidad de no quebrar):
- ✅ **Gráfico de Supervivencia**: Buscar tasas altas (>90%)
- ✅ **Histograma de Supervivencia**: Pico cerca de 120 meses
- ✅ **Gráfico de Comparación de Supervivencia**: Barras altas

### Para evaluar **RENTABILIDAD** (cuánto capital queda):
- ✅ **Gráfico de Comparación de Valores Finales**: Barras altas
- ✅ **Distribución de Valores Finales**: Distribución hacia valores positivos altos
- ✅ **Evolución del Capital**: Tendencia ascendente o estable

### Para evaluar **RIESGO** (variabilidad):
- ✅ **Bandas en Evolución**: Bandas más estrechas = menor riesgo
- ✅ **Distribución de Valores Finales**: Distribución estrecha = resultados más predecibles
- ✅ **Ancho de bandas de confianza**: Menor ancho = menor incertidumbre

### Para **COMPARAR** estrategias:
- ✅ **Gráficos de Comparación de Evolución**: Ver qué cartera mantiene mejor el capital
- ✅ **Gráficos de Comparación de Métricas**: Ver diferencias cuantitativas claras

---

## 📝 Nota Final

Todos estos gráficos trabajan juntos para darte una visión completa del desempeño de cada estrategia de inversión. **No hay un solo gráfico "mejor"** - cada uno aporta información diferente y complementaria:

- **Evolución**: Te dice **qué pasa a lo largo del tiempo**
- **Comparaciones**: Te dice **cuál estrategia es mejor**
- **Distribuciones**: Te dice **cuán confiable es cada resultado**
- **Supervivencia**: Te dice **cuál es la probabilidad de éxito**

Usa todos estos gráficos en conjunto para tomar decisiones informadas sobre qué cartera elegir según tus objetivos de riesgo y rentabilidad.

