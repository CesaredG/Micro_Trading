from .utils import Operation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ta

class SMA:
    def __init__(self, df, cash, active_operations, com, strategy_value, n_shares, sma_long_window, sma_short_window,  stop_loss_long, take_profit_long, stop_loss_short, take_profit_short):
        self.df = df
        self.cash = cash
        self.active_operations = active_operations
        self.com = com
        self.strategy_value = strategy_value
        self.n_shares = n_shares
        self.sma_long_window = sma_long_window
        self.sma_short_window = sma_short_window
        self.stop_loss_long = stop_loss_long
        self.take_profit_long = take_profit_long
        self.stop_loss_short = stop_loss_short
        self.take_profit_short = take_profit_short

        # Agregamos SMA
        short_ma = ta.trend.SMAIndicator(self.df.Close, window=self.sma_short_window)
        long_ma = ta.trend.SMAIndicator(self.df.Close, window=self.sma_long_window)
        self.df['Short_SMA'] = short_ma.sma_indicator()
        self.df['Long_SMA'] = long_ma.sma_indicator()
        self.df = self.df

        self.sma_sell_signal = self.df.iloc[0].Long_SMA > self.df.iloc[0].Short_SMA
        self.sma_buy_signal = self.df.iloc[0].Long_SMA < self.df.iloc[0].Short_SMA

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
                # See if buy signal has changed
                if (row.Long_SMA < row.Short_SMA) and not self.sma_buy_signal:
                    self.sma_buy_signal = True
                    # Buy
                    self.active_operations.append(Operation(operation_type='Long',
                                                             bought_at=row.Close,
                                                             timestamp=row.Timestamp,
                                                             n_shares=self.n_shares,
                                                             stop_loss=(row.Close * self.stop_loss_long),
                                                             take_profit=(row.Close * (1 + self.take_profit_long))))
                    self.cash -= row.Close * self.n_shares * (1 + self.com)
                elif row.Long_SMA > row.Short_SMA:
                    self.sma_buy_signal = False

                # See if sell signal has changed
                if (row.Long_SMA > row.Short_SMA) and not self.sma_sell_signal:
                    self.sma_sell_signal = True
                    # Sell
                    self.active_operations.append(Operation(operation_type='Short',
                                                             bought_at=row.Close,
                                                             timestamp=row.Timestamp,
                                                             n_shares=self.n_shares,
                                                             stop_loss=(row.Close * (1 + self.stop_loss_short)),
                                                             take_profit=(row.Close * self.take_profit_short)))
                    self.cash += row.Close * self.n_shares * (1 - self.com)
                elif row.Long_SMA < row.Short_SMA:
                    self.sma_sell_signal = False

                # Assigning SMA signal to DataFrame
                if not hasattr(self, 'signals_df_buy'):
                    self.signals_df_buy = pd.DataFrame(index=self.df.index, columns=['SMA_buy'])
                if not hasattr(self, 'signals_df_sell'):
                    self.signals_df_sell = pd.DataFrame(index=self.df.index, columns=['SMA_sell'])

                self.signals_df_buy.loc[i, 'SMA_buy'] = int(self.sma_buy_signal)
                self.signals_df_sell.loc[i, 'SMA_sell'] = int(self.sma_sell_signal)
                

            # Cuando no tenemos dinero
            else:
                pass

            # Calculate open positions value
            total_value = len(self.active_operations) * row.Close * self.n_shares
            self.strategy_value.append(self.cash + total_value)

        return self.signals_df_buy, self.signals_df_sell, self.strategy_value