from .utils import Operation
import pandas as pd
import ta

class ADX:
    def __init__(self, df, cash, active_operations, com, strategy_value, n_shares):
        self.df = df
        self.cash = cash
        self.active_operations = active_operations
        self.com = com
        self.strategy_value = strategy_value
        self.n_shares = n_shares

        # Initialize the ADX indicator
        adx = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close'], window=20)
        self.df['ADX'] = adx.adx()

        self.adx_buy_signal = False
        self.adx_sell_signal = False

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
                # Buy Signal if ADX > 10 and there is no active signal
                if row.ADX > 10 and not self.adx_buy_signal:
                    self.adx_buy_signal = True
                    self.adx_sell_signal = False
                    self.active_operations.append(Operation(operation_type='Long',
                                                             bought_at=row.Close,
                                                             timestamp=row.name,
                                                             n_shares=self.n_shares,
                                                             stop_loss=(row.Close * .95),
                                                             take_profit=(row.Close * 1.05)))
                    self.cash -= row.Close * self.n_shares * (1 + self.com)

                # Sell Signal if ADX < 10 and there is no active signal
                elif row.ADX < 10 and not self.adx_sell_signal:
                    self.adx_sell_signal = True
                    self.adx_buy_signal = False
                    self.active_operations.append(Operation(operation_type='Short',
                                                             bought_at=row.Close,
                                                             timestamp=row.name,
                                                             n_shares=self.n_shares,
                                                             stop_loss=(row.Close * 1.05),
                                                             take_profit=(row.Close * .95)))
                    self.cash += row.Close * self.n_shares * (1 - self.com)

                # Update DataFrame with the signal
                if not hasattr(self, 'signals_df'):
                    self.signals_df = pd.DataFrame(index=self.df.index, columns=['ADX_buy_signal', 'ADX_sell_signal'])

                self.signals_df.loc[i, 'ADX_buy_signal'] = int(self.adx_buy_signal)
                self.signals_df.loc[i, 'ADX_sell_signal'] = int(self.adx_sell_signal)

            # Cuando no tenemos dinero
            else:
                pass  # No action is taken when there is no money

            # Calculate open positions value
            total_value = len(self.active_operations) * row.Close * self.n_shares
            self.strategy_value.append(self.cash + total_value)

        return self.signals_df, self.strategy_value
