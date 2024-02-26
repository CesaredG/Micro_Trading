import pandas as pd
from utils.SMA import SMA
from utils.STO import STO

# Carga de datos
df_5m = pd.read_csv('./proyecto_2/data/aapl_5m_train.csv')

# Parámetros predefinidos
params = {
    'stop_loss_long': 0.024796600103236185,
    'take_profit_long': 0.38593322012654585,
    'stop_loss_short': 0.49615439857382665,
    'take_profit_short': 0.6340815141615455,
    'n_shares': 95,
    'sma_long_window': 24,
    'sma_short_window': 14,
    'sto_window': 10,
    'sto_upper_threshold': 81,
    'sto_lower_threshold': 19
}

# Variables iniciales
cash = 1_000_000
active_operations = []
com = 0.00125  # Comisión
strategy_value = [1_000_000]

# Función para ejecutar ambas estrategias con parámetros predefinidos
def run_strategies(df, params):
    # Ejecución de SMA
    sma_buy_signals, sma_sell_signals, sma_strategy_value = SMA(
        df, cash, active_operations, com, strategy_value,
        params['sma_long_window'], params['sma_short_window'],
        params['stop_loss_long'], params['take_profit_long'],
        params['stop_loss_short'], params['take_profit_short'], params['n_shares']
    )

    # Ejecución de STO
    sto_buy_signals, sto_sell_signals, sto_strategy_value = STO(
        df, cash, active_operations, com, strategy_value,
        params['sto_window'], params['sto_upper_threshold'], params['sto_lower_threshold'],
        params['stop_loss_long'], params['take_profit_long'],
        params['stop_loss_short'], params['take_profit_short'], params['n_shares']
    )

    return sma_strategy_value, sto_strategy_value

# Ejecución de la función con los parámetros predefinidos
sma_value, sto_value = run_strategies(df_5m, params)
