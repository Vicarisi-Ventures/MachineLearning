from WebSocket.OrderBook import getOrderBookWebSocket


if __name__ == "__main__":

    def main():

        print("Connecting to WebSocket")
        getOrderBookWebSocket()

        return 0

    main()