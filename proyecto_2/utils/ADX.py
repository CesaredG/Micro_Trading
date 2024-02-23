from ta.trend import ADXIndicator
from .utils import Operation

class ADXStrategy:
    def __init__(self, df, cash, active_operations, com, strategy_value, n_shares):
        self.df = df
        self.cash = cash
        self.active_operations = active_operations
        self.com = com
        self.strategy_value = strategy_value
        self.n_shares = n_shares

        # Inicializar el indicador ADX
        adx = ADXIndicator(df['High'], df['Low'], df['Close'], window=14)
        self.df['ADX'] = adx.adx()

        # Inicializar señales de compra y venta
        self.adx_buy_signal = (self.df.iloc[0]['ADX'] > 25)
        self.adx_sell_signal = (self.df.iloc[0]['ADX'] < 25)

    def run_strategy(self):
        for i, row in self.df.iterrows():

            # Cerrar operaciones
            temp_operations = []
            for op in self.active_operations:
                if op.stop_loss > row['Close']:  # Cerrar operaciones perdedoras
                    self.cash += row['Close'] * op.n_shares * (1 - self.com)
                elif op.take_profit < row['Close']:  # Cerrar operaciones rentables
                    self.cash += row['Close'] * op.n_shares * (1 - self.com)
                else:
                    temp_operations.append(op)
            self.active_operations = temp_operations

            # Comprar si hay señal de compra de ADX
            if (self.cash > row['Close'] * self.n_shares * (1 + self.com)) and self.adx_buy_signal:
                self.active_operations.append(Operation(operation_type='Long',
                                                         bought_at=row['Close'],
                                                         timestamp=row.name,
                                                         n_shares=self.n_shares,
                                                         stop_loss=(row['Close'] * .95),
                                                         take_profit=(row['Close'] * 1.05)))
                self.cash -= row['Close'] * self.n_shares * (1 + self.com)

            # Vender si hay señal de venta de ADX
            elif self.adx_sell_signal:
                self.active_operations.append(Operation(operation_type='Short',
                                                         bought_at=row['Close'],
                                                         timestamp=row.name,
                                                         n_shares=self.n_shares,
                                                         stop_loss=(row['Close'] * 1.05),
                                                         take_profit=(row['Close'] * .95)))
                self.cash += row['Close'] * self.n_shares * (1 - self.com)

            # Calcular el valor total de las operaciones abiertas
            total_value = sum(op.n_shares * row['Close'] for op in self.active_operations)
            self.strategy_value.append(self.cash + total_value)

        return self.df, self.strategy_value