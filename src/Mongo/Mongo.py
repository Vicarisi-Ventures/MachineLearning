import numpy as np
from numba import jit 
from multiprocessing.pool import ThreadPool

from pymongo import MongoClient 
from WebSocket.OrderBookObj import OrderBook
from Features.OrderBookPressure import getOrderBookPressure
from Features.WeightedMidpoint import getWeightedMidpoint
from Models.StochasticGradientDescent import getStochasticGradientDescent
from Models.RandomForestClassifier import getRandomForest
from Models.SupportVectorMachine import getSupportVectorMachine

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
    doc_count = coll.count_documents({})

    N = 10
    temp_midpoint = list(coll.find({}, {"midpoint":1, "_id":0}))
    temp_imbalance = list(coll.find({}, {"imbalance":1, "_id":0}))
    temp_w_midpoint = list(coll.find({}, {"weighted_midpoint":1, "_id":0}))
    temp_orderbook_pressure = list(coll.find({}, {"orderbook_pressure":1, "_id":0}))

    midpoint = np.zeros(doc_count)
    imbalance = np.zeros((N, doc_count))
    weighted_midpoint = np.zeros((N, doc_count))
    orderbook_pressure = np.zeros((N, doc_count))

    iterate_data(
        temp_midpoint, 
        temp_imbalance, 
        temp_w_midpoint, 
        temp_orderbook_pressure, 
        doc_count, 
        midpoint, 
        weighted_midpoint, 
        imbalance, 
        orderbook_pressure
        )

    imbalance_vector = np.zeros(doc_count * 10)
    get_imbalance_vector(doc_count, imbalance, midpoint, imbalance_vector)

    orderbook_pressure_vector = np.zeros(doc_count * 10)
    get_pressure_vector(doc_count, orderbook_pressure, midpoint, orderbook_pressure_vector)

    # Run Models in Parallel
    print("Initializing Threads")
    pool = ThreadPool(processes = 6)
    t1 = pool.apply_async(getSupportVectorMachine, (imbalance, imbalance_vector))
    t2 = pool.apply_async(getRandomForest, (imbalance, imbalance_vector))
    t3 = pool.apply_async(getStochasticGradientDescent, (imbalance, imbalance_vector))
    t4 = pool.apply_async(getSupportVectorMachine, (orderbook_pressure, orderbook_pressure_vector))
    t5 = pool.apply_async(getRandomForest, (orderbook_pressure, orderbook_pressure_vector))
    t6 = pool.apply_async(getStochasticGradientDescent, (orderbook_pressure, orderbook_pressure_vector))
    pool.close()

    try: 
        pool.join()
        imbalance_svm = t1.get()
        imbalance_rf = t2.get()
        imbalance_sgd = t3.get()
        pressure_svm = t4.get()
        pressure_rf = t5.get()
        pressure_sgd = t6.get()

    except: 
        print("Threads Failed")

    return imbalance_svm, imbalance_rf, imbalance_sgd, pressure_svm, pressure_rf, pressure_sgd

# @jit(nopython = True, parallel = True)
def iterate_data(temp_midpoint, temp_imbalance, temp_w_midpoint, temp_orderbook_pressure, doc_count, midpoint, weighted_midpoint, imbalance, orderbook_pressure):
    """
    Parses Data Quickly with Numba 
    """

    N = 10

    for i in range(doc_count):
        midpoint[i] = temp_midpoint[i]["midpoint"]

        for j in range(N):
            imbalance[j][i] = temp_imbalance[i]["imbalance"][j]
            weighted_midpoint[j][i] = temp_w_midpoint[i]["weighted_midpoint"][j]
            orderbook_pressure[j][i] = temp_orderbook_pressure[i]["orderbook_pressure"][j]

    return 0

# @jit(nopython = True, parallel = True)
def get_imbalance_vector(doc_count, imbalance, midpoint, vector):
    """
    Parses Data Quickly with Numba
    """

    N = 10

    for i in range(doc_count - 1):

        for j in range(N):
            if imbalance[j][i] > 0.50 and midpoint[i + 1] > midpoint[i]:
                vector[i] = 1

            if imbalance[j][i] < 0.50 and midpoint[i + 1] < midpoint[i]:
                vector[i] = 1 

    return 0

def get_pressure_vector(doc_count, orderbook_pressure, midpoint, vector):

    N = 10

    for i in range(doc_count - 1):

        for j in range(N):
            if orderbook_pressure[j][i] > 0.50 and midpoint[i + 1] > midpoint[i]:
                vector[i] = 1

            if orderbook_pressure[j][i] < 0.50 and midpoint[i + 1] < midpoint[i]:
                vector[i] = 1 

    return 0