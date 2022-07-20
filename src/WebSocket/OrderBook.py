import datetime
import mango

def getOrderBookWebSocket():
    """
    Input:
    1. Currency Pair

    Streams OrderBook via WebSocket Connection
    """

    with mango.ContextBuilder.build(cluster_name="devnet") as context:

        market = mango.market(context, "SOL-PERP")
        subscription = market.on_orderbook_change(context, lambda ob: print("\n", datetime.datetime.now(), "\n", ob))
        subscription.dispose()

    return 0

def getOrderBookSnapShot():
    """
    Input:
    1. Currency Pair

    Returns OrderBook via API Connection
    """

    with mango.ContextBuilder.build(cluster_name="devnet") as context:
        market = mango.market(context, "SOL-PERP")
        print(market.fetch_orderbook(context))

    return 0 