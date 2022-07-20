from numba import jit 

@jit(nopython = True) 
def getWeightedMidpoint():
    """
    Input:
    1. The Currency Pair

    Computes the Weighted Midpoint Given the Current OrderBook
    """

    return 0