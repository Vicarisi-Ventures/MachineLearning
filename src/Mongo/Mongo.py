import numpy as np

from pymongo import MongoClient 
from Features.OrderBookPressure import getOrderBookPressure
from Features.WeightedMidpoint import getWeightedMidpoint
from Models.StochasticGradientDescent import getStochasticGradientDescent
from Models.RandomForestClassifier import getRandomForest
from Models.SupportVectorMachine import getSupportVectorMachine
import matplotlib.pyplot as plt 

def getConnection(pair_name, clear_data):
    """
        Attempts to Connect to MongoDB
    """

    try: 

        # Connect 
        password = "APuXI7kPYRKNhaYA"
        client = MongoClient("mongodb+srv://vicarisiventures:" + password + "@optioncluster.ing0x.mongodb.net/?retryWrites=true&w=majority")
        print("Connected to MongoDB")

        if clear_data: 

            # Clear Previous Data
            print("Clearing Previous Data")
            db = client["MarketMaking"]
            coll = db[pair_name]
            coll.delete_many({})

    except:

        print("Error Connecting to MongoDB")
        return 0


    return client 

def appendMongo(obj, mongo_client, pair_name): 
    """
    Inserts Documents to MongoDB
    """

    db = mongo_client["MarketMaking"]
    coll = db[pair_name]

    N = 10
    bid_price = np.zeros(N)
    bid_size = np.zeros(N)
    ask_price = np.zeros(N)
    ask_size = np.zeros(N)

    for i in range(N):
        bid_price[i] = float(obj.bids[i].price)
        bid_size[i] = float(obj.bids[i].quantity)
        ask_price[i] = float(obj.asks[i].price)
        ask_size[i] = float(obj.asks[i].quantity)

    imbalance, weighted_midpoint = getWeightedMidpoint(bid_price, bid_size, ask_price, ask_size)
    pressure = getOrderBookPressure(bid_size, ask_size)

    midpoint = (float(obj.top_ask.price) + float(obj.top_bid.price)) / 2.0

    dict = { 

        "midpoint": midpoint,

        "top_ask": ask_price.tolist()[0],
        "top_ask_size": ask_size.tolist()[0],
        "top_bid": bid_price.tolist()[0],
        "top_bid_size": bid_size.tolist()[0],

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

def fetchMongo(mongo_client, pair_name): 
    """
    Fetches Data from MongoDB and Returns Machine Learning Models
    """

    db = mongo_client["MarketMaking"]
    coll = db[pair_name]

    data = coll.find({})

    midpoint = []
    weighted_midpoint = []

    imbalance = []
    orderbook_pressure = []

    for d in data: 

        midpoint.append(d["midpoint"])
        weighted_midpoint.append(d["weighted_midpoint"])

        imbalance.append(d["imbalance"][0])
        orderbook_pressure.append(d["orderbook_pressure"][0])

    l = len(midpoint)
    vector = np.zeros(l)

    for i in range(l - 1):

        if imbalance[i] > 0.50 and midpoint[i + 1] > midpoint[i]:
            vector[i] = 1

        if imbalance[i] < 0.50 and midpoint[i + 1] < midpoint[i]:
            vector[i] = 1 

    # Support Vector Machine
    svm = getSupportVectorMachine(imbalance, vector)

    # Random Forest Classifier
    rf = getRandomForest(imbalance, vector)

    # Stochastic Gradient Descent
    sgd = getStochasticGradientDescent(imbalance, vector)

    return svm, rf, sgd