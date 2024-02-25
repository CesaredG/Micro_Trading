from .utils import Operation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ta

class STO:
    def __init__(self, df, cash, active_operations, com, strategy_value, n_shares, sto_window, stoch_upper_trheshold, stoch_lower_trheshold,stop_loss_long, take_profit_long, stop_loss_short, take_profit_short):
        self.df = df
        self.cash = cash
        self.active_operations = active_operations
        self.com = com
        self.strategy_value = strategy_value
        self.n_shares = n_shares
        self.sto_window = sto_window
        self.stoch_upper_trheshold = stoch_upper_trheshold
        self.stoch_lower_trheshold = stoch_lower_trheshold
        self.stop_loss_long = stop_loss_long
        self.take_profit_long = take_profit_long
        self.stop_loss_short = stop_loss_short
        self.take_profit_short = take_profit_short

        # Add Stochastic Oscillator
        stochastic_data = ta.momentum.StochasticOscillator(high=self.df.High, low=self.df.Low, close=self.df.Close, window=self.sto_window)
        self.df['%K'] = stochastic_data.stoch()
        self.df['%D'] = stochastic_data.stoch_signal()

        # Initialize signals
        self.stoch_sell_signal = self.df.iloc[0]['%K'] > self.df.iloc[0]['%D']
        self.stoch_buy_signal = self.df.iloc[0]['%K'] < self.df.iloc[0]['%D']

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
                if (row['%K'] < self.stoch_lower_trheshold) and not self.stoch_buy_signal:
                    self.stoch_buy_signal = True
                    # Buy
                    self.active_operations.append(Operation(operation_type='Long',
                                                             bought_at=row.Close,
                                                             timestamp=row.Timestamp,
                                                             n_shares=self.n_shares,
                                                             stop_loss=(row.Close * self.stop_loss_long),
                                                             take_profit=(row.Close * (1 + self.take_profit_long))))
                    self.cash -= row.Close * self.n_shares * (1 + self.com)
                elif row['%K'] >= self.stoch_lower_trheshold:
                    self.stoch_buy_signal = False

                # See if sell signal has changed
                if (row['%K'] > self.stoch_upper_trheshold) and not self.stoch_sell_signal:
                    self.stoch_sell_signal = True
                    # Sell
                    self.active_operations.append(Operation(operation_type='Short',
                                                             bought_at=row.Close,
                                                             timestamp=row.Timestamp,
                                                             n_shares=self.n_shares,
                                                             stop_loss=(row.Close * (1 + self.stop_loss_short)),
                                                             take_profit=(row.Close * self.take_profit_short)))
                    self.cash += row.Close * self.n_shares * (1 - self.com)
                elif row['%K'] <= self.stoch_upper_trheshold:
                    self.stoch_sell_signal = False

                # Assigning Stochastic Oscillator signal to DataFrame
                # Create a new DataFrame for signals if it doesn't exist
                if not hasattr(self, 'signals_df_buy'):
                    self.signals_df_buy = pd.DataFrame(index=self.df.index, columns=['STOCH_buy'])
                if not hasattr(self, 'signals_df_sell'):
                    self.signals_df_sell = pd.DataFrame(index=self.df.index, columns=['STOCH_sell'])

                self.signals_df_buy.loc[i, 'STOCH_buy'] = int(self.stoch_buy_signal)
                self.signals_df_sell.loc[i, 'STOCH_sell'] = int(self.stoch_sell_signal)

            # Cuando no tenemos dinero
            else:
                pass

            # Calculate open positions value
            total_value = len(self.active_operations) * row.Close * self.n_shares
            self.strategy_value.append(self.cash + total_value)

        return self.signals_df_buy, self.signals_df_sell, self.strategy_value