from pydoc import doc
import pika
import time
import numpy as np
import matplotlib.pyplot as plt
from Mongo.Mongo import getConnection, fetchMongo
from WebSocket.OrderBook import getOrderBookSnapShot, getOrderBookWebSocket

def receive(channel):
    """
    Receives Data via RabbitMQ Api
    """

    # Receving 
    channel.queue_declare(queue='hello')

    data = 0
    def callback(ch, method, properties, body):
        data = body 

    channel.basic_consume(
        queue = 'hello',
        auto_ack = True,
        on_message_callback = callback
        )

    print('[*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

    return data 

def send(channel, connection):
    """
    Sends Data via RabbitMQ Api 
    """ 

    # Sending
    channel.queue_declare(queue = 'hello')

    channel.basic_publish(
        exchange = '',
        routing_key = 'hello',
        body = 'Hello World!'
        )
    
    print(" [x] Sent 'Hello World!'")
    connection.close()

    return 0

def plot_data(mongo_client, pair_name):

    db = mongo_client["MarketMaking"]
    coll = db[pair_name]
    doc_count = coll.count_documents({})

    temp_midpoint = list(coll.find({}, {"midpoint":1, "_id":0}))
    temp_imbalance = list(coll.find({}, {"imbalance":1, "_id":0}))
    temp_w_midpoint = list(coll.find({}, {"weighted_midpoint":1, "_id":0}))
    temp_orderbook_pressure = list(coll.find({}, {"orderbook_pressure":1, "_id":0}))

    N = 10
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

    # Sort Winners From Losers
    imbalance_win = []
    orderbook_pressure_win = []
    imbalance_loss = []
    orderbook_pressure_loss = []
    for i in range(doc_count - 1):
        
        # Prediction Worked
        if imbalance[N-1][i] > 0.50 and midpoint[i+1] >= midpoint[i]:
            imbalance_win.append(imbalance[N-1][i]) 
            orderbook_pressure_win.append(orderbook_pressure[N-1][i])

        if imbalance[N-1][i] < 0.50 and midpoint[i+1] <= midpoint[i]:
            imbalance_win.append(imbalance[N-1][i]) 
            orderbook_pressure_win.append(orderbook_pressure[N-1][i])

        # Prediction Failed
        if imbalance[N-1][i] > 0.50 and midpoint[i+1] < midpoint[i]:
            imbalance_loss.append(imbalance[N-1][i])
            orderbook_pressure_loss.append(orderbook_pressure[N-1][i])

        if imbalance[N-1][i] < 0.50 and midpoint[i+1] < midpoint[i]:
            imbalance_loss.append(imbalance[N-1][i])
            orderbook_pressure_loss.append(orderbook_pressure[N-1][i])

    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.suptitle("Market Making Machine Learning")

    # Plot 
    ax1.scatter(imbalance[N-1], orderbook_pressure[N-1])
    ax1.set_title("Imbalance vs. OrderBook Pressure")

    ax2.plot(midpoint)
    ax2.plot(weighted_midpoint[N-1])
    ax2.set_title("Price Time Series")

    fig2, (ax1, ax2) = plt.subplots(2, 1)
    fig2.suptitle("Market Making Machine Learning")
    
    ax1.scatter(imbalance_win, orderbook_pressure_win, label = "Win")
    ax1.scatter(imbalance_loss, orderbook_pressure_loss, label = "Loss")
    ax1.set_title("Winners and Losers")
    ax1.legend(loc = 'best')

    plt.show()

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

if __name__ == "__main__":

    def main():

        # Rabbit MQ 
        # print("Initializing RabbitMQ")
        # connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        # channel = connection.channel()

        # Begin Receiving 
        # receive(channel)
        
        # Market
        pair_name = "SOL-PERP"
        n_minutes = 15.00

        # MongoDB
        start = time.time()
        delete_data = False 
        mongo_client = getConnection(pair_name, delete_data)

        # Plot Data
        isPlot = True
        if isPlot:
            plot_data(mongo_client, pair_name)
            exit()

        # Fetch WebSocket Data
        getOrderBookWebSocket(pair_name, mongo_client, n_minutes)

        N = 10
        svm, rf, sgd = fetchMongo(mongo_client, pair_name)
        imbalance, w_mid, pressure, mid = getOrderBookSnapShot(pair_name)

        # Generate Prediction
        arr = np.array([imbalance[N-1], pressure[N-1]])
        svm_prediction = svm.predict(arr.reshape(1, -1))
        rf_prediction = rf.predict(arr.reshape(1, -1))
        sgd_prediction = sgd.predict(arr.reshape(1, -1))

        print("")
        print("Predictions:")
        print("Feature Vector: ", arr)
        print("SVM Prediction: ", svm_prediction)
        print("Random Forest Prediction: ", rf_prediction)
        print("Stochastic Gradient Descent Prediction: ", sgd_prediction)
        print("")

        end = time.time()
        print("Time Elapsed: ", end - start)

        # Begin Sending
        # send(channel, connection)

        return 0

    

    main()