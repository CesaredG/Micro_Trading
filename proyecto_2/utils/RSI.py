from .utils import Operation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ta

class RSI:
    def __init__(self, df, cash, active_operations, com, strategy_value, n_shares):
        self.df = df
        self.cash = cash
        self.active_operations = active_operations
        self.com = com
        self.strategy_value = strategy_value
        self.n_shares = n_shares

        # Agregamos RSI
        rsi_data = ta.momentum.RSIIndicator(close=self.df.Close, window=14)
        self.df['RSI'] = rsi_data.rsi()
        # Eliminamos las primeras 14 rows ya que como es nuestra ventana, aparecen las primeras 14 como nan
        self.df = self.df

        self.rsi_sell_signal = False
        self.rsi_buy_signal = False

    def run_strategy(self):
        for i, row in self.df.iterrows():

            # Close Operations
            temp_operations = []
            for op in self.active_operations:
                if op.operation_type == 'Long':
                    if op.stop_loss > row.Close:  # Close losing operations
                        self.cash += row.Close * op.n_shares * (1 - self.com)
                    elif op.take_profit < row.Close:  # Close profits
                        self.cash += row.Close * op.n_shares * (1 - self.com)
                    else:
                        temp_operations.append(op)
                elif op.operation_type == 'Short':
                    if op.stop_loss < row.Close:  # Close losing operations
                        self.cash -= row.Close * op.n_shares * (1 + self.com)
                    elif op.take_profit > row.Close:  # Close profits
                        self.cash -= row.Close * op.n_shares * (1 + self.com)
                    else:
                        temp_operations.append(op)
            self.active_operations = temp_operations
            
            # Do we have enough cash?
            if self.cash > row.Close * self.n_shares * (1 + self.com):

                # Buy Signal if RSI < 30
                if row.RSI < 30 and not self.rsi_buy_signal:
                    self.rsi_buy_signal = True
                    self.active_operations.append(Operation(operation_type='Long',
                                                             bought_at=row.Close,
                                                             timestamp=row.Timestamp,
                                                             n_shares=self.n_shares,
                                                             stop_loss=(row.Close * .95),
                                                             take_profit=(row.Close * 1.05)))
                    self.cash -= row.Close * self.n_shares * (1 + self.com)
                    self.df.loc[i, 'RSI_buy'] = True

                elif row.RSI >= 30:
                    self.rsi_buy_signal = False
                    

                # Sell Signal if RSI > 75
                if row.RSI > 75 and not self.rsi_sell_signal:
                    self.rsi_sell_signal = True
                    self.active_operations.append(Operation(operation_type='Short',
                                                             bought_at=row.Close,
                                                             timestamp=row.Timestamp,
                                                             n_shares=self.n_shares,
                                                             stop_loss=(row.Close * 1.05),
                                                             take_profit=(row.Close * .95)))
                    self.cash += row.Close * self.n_shares * (1 - self.com)
                    
                elif row.RSI <= 75:
                    self.rsi_sell_signal = False
                
                #DATAframe con las señales de compra y venta
                if not hasattr(self, 'signals_df'):
                    self.signals_df = pd.DataFrame(index=self.df.index, columns=['RSI_buy', 'RSI_sell'])

                self.signals_df.loc[i, 'RSI_buy'] = int(self.rsi_buy_signal)
                self.signals_df.loc[i, 'RSI_sell'] = int(self.rsi_sell_signal)
                    

            # Cuando no tenemos dinero
            else:
                print('No Money No Honey')

            # Calculate open positions value
            total_value = len(self.active_operations) * row.Close * self.n_shares
            self.strategy_value.append(self.cash + total_value)

        return self.signals_df, self.strategy_value
