import mango
import time

from Mongo.Mongo import appendMongo
from WebSocket.OrderBookObj import OrderBook

def getOrderBookWebSocket(pair_name, mongo_client):
    """
    Input:
    1. Currency Pair

    Streams OrderBook via WebSocket Connection
    """

    context = mango.ContextBuilder.build(cluster_name="devnet")
    market = mango.market(context, pair_name)
    subscription = market.on_orderbook_change(context, lambda ob: appendMongo(ob, mongo_client, pair_name))

    time.sleep(5)
    subscription.dispose()

    return 0

def getOrderBookSnapShot(pair_name):
    """
    Input:
    1. Currency Pair

    Returns OrderBook via API Connection
    """

    context = mango.ContextBuilder.build(cluster_name="devnet")
    market = mango.market(context, pair_name)
    orderbook = market.fetch_orderbook(context)
    bids = orderbook.bids

    # Return This
    OB = OrderBook(4)

    for bid in bids:
        print("Bid Price: ", bid.price)
        print("Bid Size: ", bid.quantity)

    asks = orderbook.asks

    for ask in asks:
        print("Ask Price: ", ask.price)
        print("Ask Size: ", ask.quantity)

    return OB

