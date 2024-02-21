from proyecto_2.utils.EWMA import EWMA
from utils.RSI import RSI
from utils.SMA import SMA
import pandas as pd
import matplotlib.pyplot as plt

# Leemos nuestros Archivos de Entrenamiento
df_1m = pd.read_csv('data/aapl_1m_train.csv')
df_5m = pd.read_csv('data/aapl_5m_train.csv')
df_1h = pd.read_csv('data/aapl_1h_train.csv')
df_1d = pd.read_csv('data/aapl_1d_train.csv')

# Definimos nuestros Parametros iniciales
cash = 1_000_000
active_operations = []
com = 0.00125  # comision en GBM
strategy_value = [1_000_000]
n_shares = 40

# Creamos una instancia de RSI para el DataFrame df_5m
rsi_5m = RSI(df_5m, cash, active_operations, com, strategy_value, n_shares)
df_5m_result, strategy_value_5m = rsi_5m.run_strategy()

print(df_5m_result)
plt.figure(figsize=(12, 4))
plt.title('RSI Trading Strategy')
plt.plot(strategy_value_5m)
plt.legend()
plt.show()

# Creamos una instancia de SMA para el DataFrame df_5m
sma_5m = SMA(df_5m, cash, active_operations, com, strategy_value, n_shares)
df_5m_result, strategy_value_5m = sma_5m.run_strategy()

print(df_5m_result)
plt.figure(figsize=(12, 4))
plt.title('SMA Trading Strategy')
plt.plot(strategy_value_5m)
plt.legend()
plt.show()

# Creamos una instancia de EWMA para el DataFrame df_5m
ewma_5m = EWMA(df_5m, cash, active_operations, com, strategy_value, n_shares)
df_5m_result, strategy_value_5m = ewma_5m.run_strategy()

print(df_5m_result)
plt.figure(figsize=(12, 4))
plt.title('EWMA Trading Strategy')
plt.plot(strategy_value_5m)
plt.legend()
plt.show()
