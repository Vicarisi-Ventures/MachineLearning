from numba import jit 

@jit(nopython = True) 
def getOrderBookPressure():
    """
    Input:
    1. The Currency Pair

    Computes the OrderBook Pressure Given the Current OrderBook
    """



    return 0