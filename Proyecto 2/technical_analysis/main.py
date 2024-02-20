from utils.utils import Operation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ta

# Leemos nuestros Archivos de Entrenamiento
df_1m = pd.read_csv('../data/aapl_1m_train.csv')
df_5m = pd.read_csv('../data/aapl_5m_train.csv')
df_1h = pd.read_csv('../data/aapl_1h_train.csv')
df_1d = pd.read_csv('../data/aapl_1d_train.csv')

# Definimos nuestros Parametros iniciales
cash = 1_000_000
active_operations = []
com = 0.00125  # comision en GBM
strategy_value = [1_000_000]
n_shares = 40

# Agregamos RSI
rsi_data = ta.momentum.RSIIndicator(close=df_5m.Close, window=14)
df_5m['RSI'] = rsi_data.rsi()
# Eliminamos las primeras 14 rows ya que como es nuestra ventana, aparecen las primeras 14 como nan
df_5m = df_5m.dropna()
# Grafico
fi, axs= plt.subplots(2,1, figsize=(12,8))
#Price chart
axs[0].plot(df_5m.Close[:214])
# Oscilator
axs[1].plot(df_5m.RSI[:214])
axs[1].plot([0,214],[70,70], 'g--',label='Upper Threshold')
axs[1].plot([0,214],[30,30], 'r--',label='Lower Threshold')
plt.legend()
plt.show()

# Agregamos SMA
short_ma = ta.trend.SMAIndicator(df_5m.Close, window=5)
long_ma = ta.trend.SMAIndicator(df_5m.Close, window=25)
df_5m['Short_SMA'] = short_ma.sma_indicator()
df_5m['Long_SMA'] = long_ma.sma_indicator()
df_5m = df_5m.dropna()
df_5m.head()
# Grafico
plt.figure(figsize=(20,6))
plt.plot(df_5m.Close[:250], label='Price')
plt.plot(df_5m.Short_SMA[:250], label= 'SMA(5)')
plt.plot(df_5m.Long_SMA[:250], label='SMA(25])')
plt.legend()
plt.show()

sma_sell_signal = df_5m.iloc[0].Long_SMA > df_5m.iloc[0].Short_SMA
sma_buy_signal = df_5m.iloc[0].Long_SMA < df_5m.iloc[0].Short_SMA

for i, row in df_5m.iterrows():
    # Close Operations
    temp_operations = []
    for op in active_operations:

        if op.stop_loss > row.Close:  # Close losing operations
            cash += row.Close * op.n_shares * (1 - com)

        elif op.take_profit < row.Close:  # Close profits
            cash += row.Close * op.n_shares * (1 - com)

        else:
            temp_operations.append(op)
    active_operations = temp_operations

    # Do we have enough cash?
    if cash > row.Close * n_shares * (1 + com):
        # See if buy signal has changed
        if (row.Long_SMA < row.Short_SMA) and sma_buy_signal == False:
            sma_buy_signal = True
            # if op.operation_type == 'Short':
            #     # Calculate commission and update cash
            #     cash -= row.Close * op.n_shares * (1 + com)
            #     # Remove operation from active_operations
            #     active_operations.remove(op)
            # Buy
            active_operations.append(Operation(operation_type='Long',
                                                bought_at=row.Close,
                                                timestamp=row.Timestamp,
                                                n_shares=n_shares,
                                                stop_loss=(row.Close * .95),
                                                take_profit=(row.Close * 1.05)))
            cash -= row.Close * n_shares * (1 + com)

        elif row.Long_SMA > row.Short_SMA:
            sma_buy_signal = False

        # See if sell signal has changed
        if (row.Long_SMA > row.Short_SMA) and sma_sell_signal == False:
            sma_sell_signal = True
            # if op.operation_type == 'Long':
            #     # Calculate commission and update cash
            #     cash += row.Close * op.n_shares * (1 - com)
            #     # Remove operation from active_operations
            #     active_operations.remove(op)
            # Sell
            active_operations.append(Operation(operation_type='Short',
                                               bought_at=row.Close,
                                               timestamp=row.Timestamp,
                                               n_shares=n_shares,
                                               stop_loss=(row.Close * 1.05),
                                               take_profit=(row.Close * .95)))
            cash += row.Close * n_shares * (1 - com)

        elif row.Long_SMA < row.Short_SMA:
            sma_sell_signal = False



        # # Buy Signal if RSI < 30
        # if row.RSI < 30:
        #     active_operations.append(Operation(operation_type='Long',
        #                                         bought_at=row.Close,
        #                                         timestamp=row.Timestamp,
        #                                         n_shares=n_shares,
        #                                         stop_loss=(row.Close * .95),
        #                                         take_profit=(row.Close * 1.05)))
        #     cash -= row.Close * n_shares * (1 + com)
        #
        # # Sell Signal if RSI > 75
        # if row.RSI < 30:
        #     active_operations.append(Operation(operation_type='Short',
        #                                        bought_at=row.Close,
        #                                        timestamp=row.Timestamp,
        #                                        n_shares=n_shares,
        #                                        stop_loss=(row.Close * 1.05),
        #                                        take_profit=(row.Close * .95)))
        #     cash += row.Close * n_shares * (1 - com)

    # Cuando no tenemos dinero
    else:
        print('No Money No Honey')

    # Calculate open positions value
    total_value = len(active_operations) * row.Close * n_shares
    strategy_value.append(cash + total_value)

plt.figure(figsize=(12, 4))
plt.title('First Trading Strategy')
plt.plot(strategy_value)
plt.legend()
plt.show()


