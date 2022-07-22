import numpy as np

from pymongo import MongoClient 
from Features.OrderBookPressure import getOrderBookPressure
from Features.WeightedMidpoint import getWeightedMidpoint

def getConnection():
    """
        Attempts to Connect to MongoDB
    """

    try: 

        password = "APuXI7kPYRKNhaYA"
        client = MongoClient("mongodb+srv://vicarisiventures:" + password + "@optioncluster.ing0x.mongodb.net/?retryWrites=true&w=majority")

    except:

        print("Error Connecting to MongoDB")
        return 0

    print("Connected to MongoDB")

    return client 

def appendMongo(obj, mongo_client, pair_name): 

    db = mongo_client["MarketMaking"]
    coll = db[pair_name]

    bid_price = np.zeros(4)
    bid_size = np.zeros(4)
    ask_price = np.zeros(4)
    ask_size = np.zeros(4)

    for i in range(4):
        bid_price[i] = float(obj.bids[i].price)
        bid_size[i] = float(obj.bids[i].quantity)
        ask_price[i] = float(obj.asks[i].price)
        ask_size[i] = float(obj.asks[i].quantity)

    imbalance, weighted_midpoint = getWeightedMidpoint(bid_price, bid_size, ask_price, ask_size)
    pressure = getOrderBookPressure(bid_size, ask_size)

    dict = { 

        "top_ask": float(obj.top_ask.price), 
        "top_ask_size": float(obj.top_ask.quantity),
        "top_bid": float(obj.top_bid.price),
        "top_bid_size": float(obj.top_ask.quantity),

        "bid_price": bid_price.tolist(),
        "bid_size": bid_size.tolist(), 
        "ask_price": ask_price.tolist(),
        "ask_size": ask_size.tolist(),

        "imbalance": imbalance.tolist(),
        "orderbook_pressure": pressure.tolist(),
        "weighted_midpoint": weighted_midpoint.tolist(),

        }

    resp = coll.insert_one(dict)
    print("Mongo Append: ", resp)

    return 0