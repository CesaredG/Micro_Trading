from itertools import combinations
import opt
import pandas as pd
import optuna



df_1m = pd.read_csv('./proyecto_2/data/aapl_1m_train.csv')
df_5m = pd.read_csv('./proyecto_2/data/aapl_5m_train.csv')
df_1h = pd.read_csv('./proyecto_2/data/aapl_1h_train.csv')
df_1d = pd.read_csv('./proyecto_2/data/aapl_1d_train.csv')



indicadores = ['EWMA', 'RSI', 'SMA', 'ADX', 'STO']

combinaciones_indicadores = []
for i in range(1, len(indicadores) + 1):
    combinaciones_indicadores.extend(combinations(indicadores, i))


cash = 1_000_000
active_operations = []
com = 0.00125  # comision en GBM
strategy_value = [1_000_000]

def optimize(trial, strat):
    stop_loss_long = trial.suggest_float('stop_loss_long', (0.01, 0.95))
    take_profit_long = trial.suggest_float('take_profit_long', (0.01, 0.95))
    stop_loss_short = trial.suggest_float('stop_loss_short', (0.01, 0.95))
    take_profit_short = trial.suggest_float('take_profit_short', (0.01, 0.95))
    n_shares = trial.suggest_int('n_shares', (10, 100))
   

    strategy_params = {}

    buy_signals = pd.DataFrame()
    sell_signals = pd.DataFrame()

    if "RSI" in strat:
        strategy_params["RSI"] = {
        "window" : trial.suggest_int('rsi_window', (10, 100)),
        "upper_treshold" : trial.suggest_int('rsi_upper_trheshold', (51, 95)),
        "lower_treshold" : trial.suggest_int('rsi_lower_trheshold', (5, 49))
        }
        rsi = RSI(df_5m, cash, active_operations, com, strategy_value, n_shares, strategy_params["RSI"]["window"], strategy_params["RSI"]["upper_treshold"], strategy_params["RSI"]["lower_treshold"], stop_loss_long, take_profit_long, stop_loss_short, take_profit_short)
        rsi_buy_signals, rsi_sell_signals, rsi_strategy_value = rsi.run_strategy()
        buy_signals["RSI"] = rsi_buy_signals
        sell_signals["RSI"] = rsi_sell_signals
    if "EWMA" in strat:
        strategy_params["EWMA"] = {
        "long_window" : trial.suggest_int('ewma_long_window', (50, 250)),
        "short_window" : trial.suggest_int('ewma_short_window', (5, 49))
        }
        ewma = EWMA(df_5m, cash, active_operations, com, strategy_value, n_shares, strategy_params["EWMA"]["long_window"], strategy_params["EWMA"]["short_window"], stop_loss_long, take_profit_long, stop_loss_short, take_profit_short)
        ewma_buy_signals, ewma_sell_signals, ewma_strategy_value = ewma.run_strategy()
        buy_signals["EWMA"] = ewma_buy_signals
        sell_signals["EWMA"] = ewma_sell_signals

    if "SMA" in strat:
        strategy_params["SMA"] = {
        "long_window" : trial.suggest_int('sma_long_window', (20, 50)),
        "short_window" : trial.suggest_int('sma_short_window', (2, 10))
        }
        sma = SMA(df_5m, cash, active_operations, com, strategy_value, n_shares, strategy_params["SMA"]["long_window"], strategy_params["SMA"]["short_window"], stop_loss_long, take_profit_long, stop_loss_short, take_profit_short)
        sma_buy_signals, sma_sell_signals, sma_strategy_value = sma.run_strategy()
        buy_signals["SMA"] = sma_buy_signals
        sell_signals["SMA"] = sma_sell_signals
    
    if "ADX" in strat:
        strategy_params["ADX"] = {
        "window" : trial.suggest_int('adx_window', (10, 100)),
        "threshold" : trial.suggest_int('adx_threshold', (5, 50))
        }
        adx = ADX(df_5m, cash, active_operations, com, strategy_value, n_shares, strategy_params["ADX"]["window"], strategy_params["ADX"]["threshold"], stop_loss_long, take_profit_long, stop_loss_short, take_profit_short)
        adx_buy_signals, adx_sell_signals, adx_strategy_value = adx.run_strategy()
        buy_signals["ADX"] = adx_buy_signals
        sell_signals["ADX"] = adx_sell_signals

    if "STO" in strat:
        strategy_params["STO"] = {
        "window" : trial.suggest_int('sto_window', (10, 100)),
        "upper_threshold" : trial.suggest_int('sto_upper_threshold', (51, 95)),
        "lower_threshold" : trial.suggest_int('sto_lower_threshold', (5, 49))
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