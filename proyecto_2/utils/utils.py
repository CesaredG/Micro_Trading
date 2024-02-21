class Operation:
    def __init__(self, operation_type, bought_at, timestamp, n_shares,
                 stop_loss,take_profit):
        self.operation_type = operation_type
        self.bought_at = bought_at
        self.timestamp = timestamp
        self.n_shares = n_shares
        self.sold_at = None
        self.stop_loss = stop_loss
        self.take_profit = take_profit




