import pika
from Mongo.Mongo import getConnection, fetchMongo
from WebSocket.OrderBook import getOrderBookSnapShot, getOrderBookWebSocket


if __name__ == "__main__":

    def main():
        
        # Market
        pair_name = "SOL-PERP"
        n_minutes = 5.00

        # MongoDB
        # mongo_client = getConnection(pair_name, False)

        # Fetch WebSocket Data
        # getOrderBookWebSocket(pair_name, mongo_client, n_minutes)

        # svm, rf, sgd = fetchMongo(mongo_client, pair_name)
        imbalance, w_mid, pressure, mid = getOrderBookSnapShot(pair_name)

        # Rabbit MQ 
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        channel.basic_publish(
                exchange = '',
                routing_key = 'hello',
                body = 'Hello World!'
                )

        return 0

    main()