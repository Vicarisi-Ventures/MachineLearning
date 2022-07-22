import numpy as np
from numba import jit 

# @jit(nopython = True) 
def getWeightedMidpoint(bid_price, bid_size, ask_price, ask_size):
    """
    Input:
    1. The Currency Pair

    Computes the Weighted Midpoint Given the Current OrderBook
    """

    l = len(bid_price)
    imbalance = np.zeros(l)
    w_midpoints = np.zeros(l)

    bid_kappa = 0
    ask_kappa = 0

    for i in range(l):

        bid_kappa += bid_price[i] * bid_size[i] 
        ask_kappa += ask_price[i] * ask_size[i]
        imbalance[i] = bid_kappa / (bid_kappa + ask_kappa)
        w_midpoints[i] = (imbalance[i] * ask_price[i]) + ((1 - imbalance[i]) * bid_price[i])

    return imbalance, w_midpoints