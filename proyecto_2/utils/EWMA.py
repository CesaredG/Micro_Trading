from .utils import Operation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ta

class EWMA:
    def __init__(self, df, cash, active_operations, com, strategy_value, n_shares):
        self.df = df
        self.cash = cash
        self.active_operations = active_operations
        self.com = com
        self.strategy_value = strategy_value
        self.n_shares = n_shares

        # Agregamos EWMA
        short_ema = ta.trend.EMAIndicator(self.df.Close, window=7)
        long_ema = ta.trend.EMAIndicator(self.df.Close, window=32)
        self.df['Short_EWMA'] = short_ema.ema_indicator()
        self.df['Long_EWMA'] = long_ema.ema_indicator()
        self.df = self.df.dropna()

        self.ewma_sell_signal = self.df.iloc[0].Long_EWMA > self.df.iloc[0].Short_EWMA
        self.ewma_buy_signal = self.df.iloc[0].Long_EWMA < self.df.iloc[0].Short_EWMA

    def get_buy_signal(self):
        ...
    
    def get_sell_signal(self):
        ...

    def run_strategy(self):
        for i, row in self.df.iterrows():

            # Close Operations
            temp_operations = []
            for op in self.active_operations:

                if op.stop_loss > row.Close:  # Close losing operations
                    self.cash += row.Close * op.n_shares * (1 - self.com)

                elif op.take_profit < row.Close:  # Close profits
                    self.cash += row.Close * op.n_shares * (1 - self.com)
                else:
                    temp_operations.append(op)
            self.active_operations = temp_operations

            # Do we have enough cash?
            if self.cash > row.Close * self.n_shares * (1 + self.com):
                # See if buy signal has changed
                if (row.Long_EWMA < row.Short_EWMA) and not self.ewma_buy_signal:
                    self.ewma_buy_signal = True
                    # Buy
                    self.active_operations.append(Operation(operation_type='Long',
                                                             bought_at=row.Close,
                                                             timestamp=row.Timestamp,
                                                             n_shares=self.n_shares,
                                                             stop_loss=(row.Close * .95),
                                                             take_profit=(row.Close * 1.05)))
                    self.cash -= row.Close * self.n_shares * (1 + self.com)
                elif row.Long_EWMA > row.Short_EWMA:
                    self.ewma_buy_signal = False

                # See if sell signal has changed
                if (row.Long_EWMA > row.Short_EWMA) and not self.ewma_sell_signal:
                    self.ewma_sell_signal = True
                    # Sell
                    self.active_operations.append(Operation(operation_type='Short',
                                                             bought_at=row.Close,
                                                             timestamp=row.Timestamp,
                                                             n_shares=self.n_shares,
                                                             stop_loss=(row.Close * 1.05),
                                                             take_profit=(row.Close * .95)))
                    self.cash += row.Close * self.n_shares * (1 - self.com)
                elif row.Long_EWMA < row.Short_EWMA:
                    self.ewma_sell_signal = False

                # Assigning EWMA signal to DataFrame
                self.df.loc[i, 'EWMA_buy'] = int(self.ewma_buy_signal)
                self.df.loc[i, 'EWMA_sell'] = int(self.ewma_sell_signal)

            # Cuando no tenemos dinero
            else:
                print('No Money No Honey')

            # Calculate open positions value
            total_value = len(self.active_operations) * row.Close * self.n_shares
            self.strategy_value.append(self.cash + total_value)

        return self.df, self.strategy_value
