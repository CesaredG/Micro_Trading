from .utils import Operation
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ta

class CombinedStrategy:
    def __init__(self, df, cash, active_operations, com, strategy_value, n_shares,
                 sma_long_window, sma_short_window, stop_loss_long_sma, take_profit_long_sma,
                 stop_loss_short_sma, take_profit_short_sma,
                 sto_window, stoch_upper_threshold, stoch_lower_threshold,
                 stop_loss_long_sto, take_profit_long_sto, stop_loss_short_sto, take_profit_short_sto):
        
        self.df = df
        self.cash = cash
        self.active_operations = active_operations
        self.com = com
        self.strategy_value = strategy_value
        self.n_shares = n_shares
        
        # SMA Parameters
        self.sma_long_window = sma_long_window
        self.sma_short_window = sma_short_window
        self.stop_loss_long_sma = stop_loss_long_sma
        self.take_profit_long_sma = take_profit_long_sma
        self.stop_loss_short_sma = stop_loss_short_sma
        self.take_profit_short_sma = take_profit_short_sma
        
        # Stochastic Oscillator Parameters
        self.sto_window = sto_window
        self.stoch_upper_threshold = stoch_upper_threshold
        self.stoch_lower_threshold = stoch_lower_threshold
        self.stop_loss_long_sto = stop_loss_long_sto
        self.take_profit_long_sto = take_profit_long_sto
        self.stop_loss_short_sto = stop_loss_short_sto
        self.take_profit_short_sto = take_profit_short_sto

        # Add SMA
        short_ma = ta.trend.SMAIndicator(self.df.Close, window=self.sma_short_window)
        long_ma = ta.trend.SMAIndicator(self.df.Close, window=self.sma_long_window)
        self.df['Short_SMA'] = short_ma.sma_indicator()
        self.df['Long_SMA'] = long_ma.sma_indicator()

        self.sma_sell_signal = self.df.iloc[0].Long_SMA > self.df.iloc[0].Short_SMA
        self.sma_buy_signal = self.df.iloc[0].Long_SMA < self.df.iloc[0].Short_SMA

        # Add Stochastic Oscillator
        stochastic_data = ta.momentum.StochasticOscillator(high=self.df.High, low=self.df.Low, close=self.df.Close, window=self.sto_window)
        self.df['%K'] = stochastic_data.stoch()
        self.df['%D'] = stochastic_data.stoch_signal()

        # Initialize signals
        self.stoch_sell_signal = self.df.iloc[0]['%K'] > self.df.iloc[0]['%D']
        self.stoch_buy_signal = self.df.iloc[0]['%K'] < self.df.iloc[0]['%D']

        # Create DataFrames for signals
        self.signals_df_buy = pd.DataFrame(index=self.df.index, columns=['SMA_buy', 'STOCH_buy'])
        self.signals_df_sell = pd.DataFrame(index=self.df.index, columns=['SMA_sell', 'STOCH_sell'])

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
                # SMA strategy
                if (row.Long_SMA < row.Short_SMA) and not self.sma_buy_signal:
                    self.sma_buy_signal = True
                    # Buy
                    self.active_operations.append(Operation(operation_type='Long',
                                                             bought_at=row.Close,
                                                             timestamp=row.Timestamp,
                                                             n_shares=self.n_shares,
                                                             stop_loss=(row.Close * self.stop_loss_long_sma),
                                                             take_profit=(row.Close * (1 + self.take_profit_long_sma))))
                    self.cash -= row.Close * self.n_shares * (1 + self.com)
                elif row.Long_SMA > row.Short_SMA:
                    self.sma_buy_signal = False

                if (row.Long_SMA > row.Short_SMA) and not self.sma_sell_signal:
                    self.sma_sell_signal = True
                    # Sell
                    self.active_operations.append(Operation(operation_type='Short',
                                                             bought_at=row.Close,
                                                             timestamp=row.Timestamp,
                                                             n_shares=self.n_shares,
                                                             stop_loss=(row.Close * (1 + self.stop_loss_short_sma)),
                                                             take_profit=(row.Close * self.take_profit_short_sma)))
                    self.cash += row.Close * self.n_shares * (1 - self.com)
                elif row.Long_SMA < row.Short_SMA:
                    self.sma_sell_signal = False

                # Stochastic Oscillator strategy
                if (row['%K'] < self.stoch_lower_threshold) and not self.stoch_buy_signal:
                    self.stoch_buy_signal = True
                    # Buy
                    self.active_operations.append(Operation(operation_type='Long',
                                                             bought_at=row.Close,
                                                             timestamp=row.Timestamp,
                                                             n_shares=self.n_shares,
                                                             stop_loss=(row.Close * self.stop_loss_long_sto),
                                                             take_profit=(row.Close * (1 + self.take_profit_long_sto))))
                    self.cash -= row.Close * self.n_shares * (1 + self.com)
                elif row['%K'] >= self.stoch_lower_threshold:
                    self.stoch_buy_signal = False

                if (row['%K'] > self.stoch_upper_threshold) and not self.stoch_sell_signal:
                    self.stoch_sell_signal = True
                    # Sell
                    self.active_operations.append(Operation(operation_type='Short',
                                                             bought_at=row.Close,
                                                             timestamp=row.Timestamp,
                                                             n_shares=self.n_shares,
                                                             stop_loss=(row.Close * (1 + self.stop_loss_short_sto)),
                                                             take_profit=(row.Close * self.take_profit_short_sto)))
                    self.cash += row.Close * self.n_shares * (1 - self.com)
                elif row['%K'] <= self.stoch_upper_threshold:
                    self.stoch_sell_signal = False

                # Assigning signals to DataFrames
                self.signals_df_buy.loc[i, ['SMA_buy', 'STOCH_buy']] = int(self.sma_buy_signal), int(self.st
                else:
                    pass

                        # Calculate open positions value
                        total_value = len(self.active_operations) * row.Close * self.n_shares
                        self.strategy_value.append(self.cash + total_value)

     return self.signals_df_buy, self.signals_df_sell, self.strategy_value, self.active_operations