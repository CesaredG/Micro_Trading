from utils.EWMA import EWMA
from utils.RSI import RSI
from utils.SMA import SMA
from utils.ADX import ADX
from utils.SO import STO
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations
import optuna 

# Leemos nuestros Archivos de Entrenamiento

#df_1m = pd.read_csv('data/aapl_1m_train.csv')
#df_5m = pd.read_csv('data/aapl_5m_train.csv')
#df_1h = pd.read_csv('data/aapl_1h_train.csv')
#df_1d = pd.read_csv('data/aapl_1d_train.csv')

df_1m = pd.read_csv('./proyecto_2/data/aapl_1m_train.csv')
df_5m = pd.read_csv('./proyecto_2/data/aapl_5m_train.csv')
df_1h = pd.read_csv('./proyecto_2/data/aapl_1h_train.csv')
df_1d = pd.read_csv('./proyecto_2/data/aapl_1d_train.csv')


# # Definimos nuestros Parametros iniciales
# cash = 1_000_000
# active_operations = []
# com = 0.00125  # comision en GBM
# strategy_value = [1_000_000]
# n_shares = 40
# stop_loss_long = 0.95
# take_profit_long = 0.05
# stop_loss_short = 0.05
# take_profit_short = 0.95
# #RSI parametros
# rsi_window = 14
# rsi_upper_trheshold = 75
# rsi_lower_trheshold = 30
# #SMA parametros
# sma_long_window = 25
# sma_short_window = 5
# #EWMA parametros
# ewma_long_window = 32
# ewma_short_window = 7
# #ADX parametros
# adx_window = 20
# adx_trheshold = 10
# #STO parametros
# sto_window = 14
# stoch_upper_trheshold = 70
# stoch_lower_trheshold = 30

# # Creamos una instancia de RSI para el DataFrame df_5m
# rsi_5m = RSI(df_5m, cash, active_operations, com, strategy_value, n_shares, rsi_window, rsi_upper_trheshold, rsi_lower_trheshold, stop_loss_long, take_profit_long, stop_loss_short, take_profit_short)
# rsi_df_5m_buy, rsi_df_5m_sell, rsi_strategy_value_5m = rsi_5m.run_strategy()

# print(rsi_df_5m_buy)
# print(rsi_df_5m_sell)
# plt.figure(figsize=(12, 4))
# plt.title('RSI Trading Strategy')
# plt.plot(rsi_strategy_value_5m)
# plt.legend()
# plt.show()

# # Creamos una instancia de SMA para el DataFrame df_5m
# sma_5m = SMA(df_5m, cash, active_operations, com, strategy_value, n_shares, sma_long_window, sma_short_window, stop_loss_long, take_profit_long, stop_loss_short, take_profit_short)
# sma_df_5m_buy, sma_df_5m_sell ,sma_strategy_value_5m = sma_5m.run_strategy()

# print(sma_df_5m_buy)
# print(sma_df_5m_sell)
# plt.figure(figsize=(12, 4))
# plt.title('SMA Trading Strategy')
# plt.plot(sma_strategy_value_5m)
# plt.legend()
# plt.show()

# # Creamos una instancia de EWMA para el DataFrame df_5m
# ewma_5m = EWMA(df_5m, cash, active_operations, com, strategy_value, n_shares, ewma_long_window, ewma_short_window, stop_loss_long, take_profit_long, stop_loss_short, take_profit_short)
# ewma_df_5m_buy, ewma_df_5m_sell, ewma_strategy_value_5m = ewma_5m.run_strategy()

# print(ewma_df_5m_buy)
# print(ewma_df_5m_sell)
# plt.figure(figsize=(12, 4))
# plt.title('EWMA Trading Strategy')
# plt.plot(ewma_strategy_value_5m)
# plt.legend()
# plt.show()

# # Creamos una instancia de ADX para el DataFrame df_5m
# adx_5m = ADX(df_5m, cash, active_operations, com, strategy_value, n_shares, adx_window, adx_trheshold, stop_loss_long, take_profit_long, stop_loss_short, take_profit_short)
# adx_df_5m_buy, adx_df_5m_sell, adx_strategy_value_5m = adx_5m.run_strategy()

# print(adx_df_5m_buy)
# print(adx_df_5m_sell)
# plt.figure(figsize=(12, 4))
# plt.title('ADX Trading Strategy')
# plt.plot(adx_strategy_value_5m)
# plt.legend()
# plt.show()

# # Creamos una instancia de ADX para el DataFrame df_5m
# sto_5m = STO(df_5m, cash, active_operations, com, strategy_value, n_shares, sto_window, stoch_upper_trheshold, stoch_lower_trheshold, stop_loss_long, take_profit_long, stop_loss_short, take_profit_short)
# sto_df_5m_buy, sto_df_5m_sell, sto_strategy_value_5m = sto_5m.run_strategy()

# print(sto_df_5m_buy)
# print(sto_df_5m_sell)
# plt.figure(figsize=(12, 4))
# plt.title('STO Trading Strategy')
# plt.plot(sto_strategy_value_5m)
# plt.legend()
# plt.show()

## Optuna

indicadores = ['EWMA', 'RSI', 'SMA', 'ADX', 'STO']

combinaciones_indicadores = []
for i in range(1, len(indicadores) + 1):
    combinaciones_indicadores.extend(combinations(indicadores, i))


cash = 1_000_000
active_operations = []
com = 0.00125  # comision en GBM
strategy_value = [1_000_000]

def optimize(trial, strat):
    stop_loss_long = trial.suggest_float('stop_loss_long', 0.01, 0.95)
    take_profit_long = trial.suggest_float('take_profit_long', 0.01, 0.95)
    stop_loss_short = trial.suggest_float('stop_loss_short', 0.01, 0.95)
    take_profit_short = trial.suggest_float('take_profit_short', 0.01, 0.95)
    n_shares = trial.suggest_int('n_shares', 10, 100)
   

    strategy_params = {}

    buy_signals = pd.DataFrame()
    sell_signals = pd.DataFrame()

    if "RSI" in strat:
        strategy_params["RSI"] = {
        "window" : trial.suggest_int('rsi_window', 10, 100),
        "upper_treshold" : trial.suggest_int('rsi_upper_trheshold', 51, 95),
        "lower_treshold" : trial.suggest_int('rsi_lower_trheshold', 5, 49)
        }
        rsi = RSI(df_5m, cash, active_operations, com, strategy_value, n_shares, strategy_params["RSI"]["window"], strategy_params["RSI"]["upper_treshold"], strategy_params["RSI"]["lower_treshold"], stop_loss_long, take_profit_long, stop_loss_short, take_profit_short)
        rsi_buy_signals, rsi_sell_signals, rsi_strategy_value = rsi.run_strategy()
        buy_signals["RSI"] = rsi_buy_signals
        sell_signals["RSI"] = rsi_sell_signals
    if "EWMA" in strat:
        strategy_params["EWMA"] = {
        "long_window" : trial.suggest_int('ewma_long_window', 50, 250),
        "short_window" : trial.suggest_int('ewma_short_window', 5, 49)
        }
        ewma = EWMA(df_5m, cash, active_operations, com, strategy_value, n_shares, strategy_params["EWMA"]["long_window"], strategy_params["EWMA"]["short_window"], stop_loss_long, take_profit_long, stop_loss_short, take_profit_short)
        ewma_buy_signals, ewma_sell_signals, ewma_strategy_value = ewma.run_strategy()
        buy_signals["EWMA"] = ewma_buy_signals
        sell_signals["EWMA"] = ewma_sell_signals

    if "SMA" in strat:
        strategy_params["SMA"] = {
        "long_window" : trial.suggest_int('sma_long_window', 20, 50),
        "short_window" : trial.suggest_int('sma_short_window', 2, 10)
        }
        sma = SMA(df_5m, cash, active_operations, com, strategy_value, n_shares, strategy_params["SMA"]["long_window"], strategy_params["SMA"]["short_window"], stop_loss_long, take_profit_long, stop_loss_short, take_profit_short)
        sma_buy_signals, sma_sell_signals, sma_strategy_value = sma.run_strategy()
        buy_signals["SMA"] = sma_buy_signals
        sell_signals["SMA"] = sma_sell_signals
    
    if "ADX" in strat:
        strategy_params["ADX"] = {
        "window" : trial.suggest_int('adx_window', 10, 100),
        "threshold" : trial.suggest_int('adx_threshold', 5, 50)
        }
        adx = ADX(df_5m, cash, active_operations, com, strategy_value, n_shares, strategy_params["ADX"]["window"], strategy_params["ADX"]["threshold"], stop_loss_long, take_profit_long, stop_loss_short, take_profit_short)
        adx_buy_signals, adx_sell_signals, adx_strategy_value = adx.run_strategy()
        buy_signals["ADX"] = adx_buy_signals
        sell_signals["ADX"] = adx_sell_signals

    if "STO" in strat:
        strategy_params["STO"] = {
        "window" : trial.suggest_int('sto_window', 10, 100),
        "upper_threshold" : trial.suggest_int('sto_upper_threshold', 51, 95),
        "lower_threshold" : trial.suggest_int('sto_lower_threshold', 5, 49)
        }
        sto = STO(df_5m, cash, active_operations, com, strategy_value, n_shares, strategy_params["STO"]["window"], strategy_params["STO"]["upper_threshold"], strategy_params["STO"]["lower_threshold"], stop_loss_long, take_profit_long, stop_loss_short, take_profit_short)
        sto_buy_signals, sto_sell_signals, sto_strategy_value = sto.run_strategy()
        buy_signals["STO"] = sto_buy_signals
        sell_signals["STO"] = sto_sell_signals

    for i, row in buy_signals.iterrows():
        buy_signal = False
        sell_signal = False
        if sum(buy_signals.iloc[i, :]) == len(buy_signals.columns):
            buy_signal = True
            
        if sum(sell_signals.iloc[i, :]) == len(sell_signals.columns):
            sell_signal = True

        strategy_value.append(strategy_value[-1])
        
    if sum(buy_signals.iloc[i, :]) == len(buy_signals.columns):
        buy_signal = True
        
    if sum(sell_signals.iloc[i, :]) == len(sell_signals.columns):
        sell_signal = True

    return strategy_value[-1]

for strat in combinaciones_indicadores:
    study = optuna.create_study(direction='maximize')
    study.optimize(lambda trial: optimize(trial, strat), n_trials=5)

    # Get the best parameters and their corresponding value
    best_params = study.best_params
    best_value = study.best_value

    print("Best parameters:", best_params)
    print("Best value:", best_value)

