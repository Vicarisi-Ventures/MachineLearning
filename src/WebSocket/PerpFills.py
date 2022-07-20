import mango

def getPerpFillsWebSocket():
    """
    Input:
    1. Currency Pair

    Streams Order Fills via WebSocket Connection
    """

    with mango.ContextBuilder.build(cluster_name="devnet") as context:

        market = mango.market(context, "SOL-PERP")
        event_queue = mango.PerpEventQueue.load(context, market.event_queue_address, market.lot_size_converter)
        print(event_queue.fills)

    return 0

