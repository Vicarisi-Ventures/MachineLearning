import pika
from Mongo.Mongo import getConnection, fetchMongo
from WebSocket.OrderBook import getOrderBookSnapShot, getOrderBookWebSocket


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
        n_minutes = 5.00

        # MongoDB
        mongo_client = getConnection(pair_name, False)

        # Fetch WebSocket Data
        # getOrderBookWebSocket(pair_name, mongo_client, n_minutes)

        imbalance_svm, imbalance_rf, imbalance_sgd, pressure_svm, pressure_rf, pressure_sgd = fetchMongo(mongo_client, pair_name)
        imbalance, w_mid, pressure, mid = getOrderBookSnapShot(pair_name)

        # Generate Prediction
        imbalance_svm_prediction = imbalance_svm.predict(imbalance.reshape(-1, 1))
        imbalance_rf_prediction = imbalance_rf.predict(imbalance.reshape(-1, 1))
        imbalance_sgd_prediction = imbalance_sgd.predict(imbalance.reshape(-1, 1))

        print("Imbalance:")
        print("Imbalance Prediction: ", imbalance_svm_prediction)
        print("Random Forest Prediction: ", imbalance_rf_prediction)
        print("Stochastic Gradient Descent Prediction: ", imbalance_sgd_prediction)
        print("")

        pressure_svm_prediction = pressure_svm.predict(pressure.reshape(-1, 1))
        pressure_rf_prediction = pressure_rf.predict(pressure.reshape(-1, 1))
        pressure_sgd_prediction = pressure_sgd.predict(pressure.reshape(-1, 1))

        print("OrderBook Pressure:")
        print("Support Vector Machine Prediction: ", pressure_svm_prediction)
        print("Random Forest Prediction: ", pressure_rf_prediction)
        print("Stochastic Gradient Descent Prediction: ", pressure_sgd_prediction)
        print("")

        # Begin Sending
        # send(channel, connection)

        return 0

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

    main()