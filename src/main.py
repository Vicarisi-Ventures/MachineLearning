from Mongo.Mongo import getConnection
from WebSocket.Market import getMarket
from WebSocket.OrderBook import getOrderBookSnapShot, getOrderBookWebSocket


if __name__ == "__main__":

    def main():

        # MongoDB
        mongo_client = getConnection()

        # Market
        pair_name = "SOL-PERP"

        # getMarket(pair_name)
        # getOrderBookSnapShot(pair_name)
        getOrderBookWebSocket(pair_name, mongo_client)

        return 0

    main()