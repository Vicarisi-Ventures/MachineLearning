import mango
import time
import numpy as np

from Mongo.Mongo import appendMongo
from WebSocket.OrderBookObj import OrderBook
from Features.OrderBookPressure import getOrderBookPressure
from Features.WeightedMidpoint import getWeightedMidpoint

def getOrderBookWebSocket(pair_name, mongo_client, n_minutes):
    """
    Input:
    1. Currency Pair

    Streams OrderBook via WebSocket Connection
    """

    context = mango.ContextBuilder.build(cluster_name="mainnet")
    market = mango.market(context, pair_name)
    subscription = market.on_orderbook_change(context, lambda ob: appendMongo(ob, mongo_client, pair_name))

    time.sleep(60 * n_minutes)
    subscription.dispose()

    return 0

def getOrderBookSnapShot(pair_name):
    """
    Input:
    1. Currency Pair

    Returns OrderBook via API Connection
    """

    context = mango.ContextBuilder.build(cluster_name="mainnet")
    market = mango.market(context, pair_name)
    orderbook = market.fetch_orderbook(context)
    bids = orderbook.bids
    asks = orderbook.asks

    # Return This
    N = 10
    bid_price = np.zeros(N)
    bid_size = np.zeros(N)
    ask_price = np.zeros(N)
    ask_size = np.zeros(N)

    for i in range(N):
        bid_price[i] = float(bids[i].price)
        bid_size[i] = float(bids[i].quantity)
        ask_price[i] = float(asks[i].price)
        ask_size[i] = float(asks[i].quantity)

    imbalance, weighted_midpoint = getWeightedMidpoint(bid_price, bid_size, ask_price, ask_size)
    pressure = getOrderBookPressure(bid_size, ask_size)
    midpoint = (bid_price[0] + ask_price[0]) / 2.0

    return imbalance, weighted_midpoint, pressure, midpoint

