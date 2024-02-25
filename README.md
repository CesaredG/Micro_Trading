# Proyecto: 002 Technical Analysis

El análisis técnico en los mercados financieros consiste en el examen de datos históricos para prever tendencias futuras en los precios de los activos. Proporciona un marco metodológico para interpretar el comportamiento del mercado, permitiendo la toma de decisiones informadas y la gestión de riesgos. Aunque no se trata de un enfoque infalible, se reconoce como una herramienta valiosa para una amplia gama de operadores del mercado. Diversas estrategias, como EWMA, SMA, ADX, RSI y el Oscilador Estocástico, se emplean con el fin de optimizar estrategias de inversión basadas en el análisis técnico.

### Parámetros por operación

1. **Stop Loss Long:**
   - Rango: Entre 0.01 y 0.95.
   - Descripción: Este parámetro establece el nivel de precio al cual se activará una orden de venta para cerrar una posición larga y limitar las pérdidas.

2. **Take Profit Long:**
   - Rango: Entre 0.01 y 0.95.
   - Descripción: Especifica el nivel de precio al cual se activará una orden de venta para cerrar una posición larga y asegurar las ganancias.

3. **Stop Loss Short:**
   - Rango: Entre 0.01 y 0.95.
   - Descripción: Determina el nivel de precio al cual se activará una orden de compra para cerrar una posición corta y limitar las pérdidas.

4. **Take Profit Short:**
   - Rango: Entre 0.01 y 0.95.
   - Descripción: Indica el nivel de precio al cual se activará una orden de compra para cerrar una posición corta y asegurar las ganancias.

5. **Número de Acciones (n_shares):**
   - Rango: Entre 10 y 100.
   - Descripción: Este parámetro define la cantidad de acciones a comprar o vender en cada operación.

### Parámetros por Indicador

1. **RSI:**
   - `rsi_window`: Ventana para el cálculo del RSI (entero entre 10 y 50).
   - `rsi_upper_threshold`: Umbral superior del RSI (entero entre 50 y 95).
   - `rsi_lower_threshold`: Umbral inferior del RSI (entero entre 5 y 49).

2. **EWMA:**
   - `ewma_long_window`: Ventana para la media móvil exponencial larga (entero entre 50 y 100).
   - `ewma_short_window`: Ventana para la media móvil exponencial corta (entero entre 5 y 49).

3. **SMA:**
   - `sma_long_window`: Ventana para la media móvil simple larga (entero entre 20 y 50).
   - `sma_short_window`: Ventana para la media móvil simple corta (entero entre 2 y 19).

4. **ADX:**
   - `adx_window`: Ventana para el cálculo del ADX (entero entre 10 y 50).
   - `adx_threshold`: Umbral del ADX (entero entre 15 y 30).

5. **STO:**
   - `sto_window`: Ventana para el cálculo del indicador estocástico (entero entre 10 y 50).
   - `sto_upper_threshold`: Umbral superior del indicador estocástico (entero entre 50 y 95).
   - `sto_lower_threshold`: Umbral inferior del indicador estocástico (entero entre 5 y 49).



