import mango

def getMarket(pair_name):
    """
    
    """

    context =  mango.ContextBuilder.build(cluster_name="devnet")
    market = mango.market(context, "spot:" + pair_name)
    print("spot_market", market)

    return 0