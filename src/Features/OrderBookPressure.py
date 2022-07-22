import numpy as np
from numba import jit 

@jit(nopython = True) 
def getOrderBookPressure(bid_size, ask_size):
    """
    Input:
    1. The Currency Pair

    Computes the OrderBook Pressure Given the Current OrderBook

    PsuedoCode:
    1. If Best Ask Size > Best Bid Size --> Midpoint Decreases
    2. If Best Ask Size < Best Bid Size --> Midpoint Increases
    3. If Best Ask Size == Best Bid Size --> Midpoint Unchanged 

    Output:
    1. If Signal > 0 --> Bullish
    2. If Signal < 0 --> Bearish
    """

    l = len(bid_size)
    pressure = np.zeros(l)

    bid_sum_size = 0
    ask_sum_size = 0

    for i in range(l):

        bid_sum_size += bid_size[i]
        ask_sum_size += ask_size[i]
        pressure[i] = bid_sum_size / ask_sum_size

    return pressure