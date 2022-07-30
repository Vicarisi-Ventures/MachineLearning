import numpy as np
from numba import float64 
from numba.experimental import jitclass

spec = [

    ('top_bid', float64),
    ('top_bid_size', float64),
    ('top_ask', float64),
    ('top_ask_size', float64),

    ('bid_price', float64[:]),
    ('bid_size', float64[:]),
    ('ask_price', float64[:]),
    ('ask_size', float64[:]),

    ('bid_sum_size', float64),
    ('ask_sum_size', float64),
    ('imbalance', float64[:]),
    ('orderbook_pressure', float64[:]),
    ('weighted_midpoint', float64[:]),
]

@jitclass(spec)
class OrderBook:
    """
    Contains OrderBook Variables
    """

    def __init__(self, data, length, n_features):

        self.top_bid = 0
        self.top_bid_size = 0
        self.top_ask = 0
        self.top_ask_size = 0

        self.bid_price = np.zeros(length)
        self.bid_size = np.zeros(length)
        self.ask_price = np.zeros(length)
        self.ask_size = np.zeros(length)

        self.bid_sum_size = 0
        self.ask_sum_size = 0
        self.imbalance = np.zeros((n_features, length))
        self.orderbook_pressure = np.zeros((n_features, length))
        self.weighted_midpoint = np.zeros((n_features, length))
