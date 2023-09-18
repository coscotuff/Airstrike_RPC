import grpc
from concurrent import futures
import time
import threading
import sys
import logging

import timestamp_pb2
import timestamp_pb2_grpc


class Service(timestamp_pb2_grpc.ExchangeServicer):
    def __init__(self, tsA):
        self.A = tsA
        self.B = 0
    
    def order(self, request, context):
        # Set timestamp variable B using the timestamp from the other server:
        self.B = request.micros
        logger.debug("Timestamp received from client " + str(request.micros))
        logger.debug("Server Timestamp " + str(self.A))
        logger.debug("Client Timestamp: " + str(self.B))
        
        if self.A < self.B:
            logger.debug("Server is the leader")

            # Call the initiate function:
            self.initiate()
        else:
            logger.debug("Client is the leader")

        # Return a response to the client immediately
        return timestamp_pb2.Empty()

    def initiate(self):
        # Simulate some work in the initiate function
        logger.debug("Initiate function called by leader")

# TO-DO: Add timestamp calculation, figure out logic to call the other server on a periodic basis and return their timestamp,
# add timestamp of that server a variable (change self.A to self.A.timestamp), and then compare the timestamps to determine
# which server is the leader. Also need to add try except blocks to handle the case where the other server is down and 
# there should be a constant sleep() to check the other server's timestamp every 5 seconds or so.


def serve(port, timestamp):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    timestamp_pb2_grpc.add_ExchangeServicer_to_server(Service(tsA = timestamp), server)
    server.add_insecure_port("[::]:" + str(port))
    server.start()
    print("Server started")

    if port == 50050:
        port = 60060
    else:
        port = 50050
    
    while True:
        try:
            channel = grpc.insecure_channel("localhost:" + str(port))
            stub = timestamp_pb2_grpc.ExchangeStub(channel)
            response = stub.order(timestamp_pb2.Timestamp(micros=timestamp))
            break
        except Exception as e:
            print("Server is down: " + str(e))
            time.sleep(2)

    logger.debug("Timestamp sent to server: " + str(timestamp))
    server.wait_for_termination()


if __name__ == "__main__":
    port = 50050
    timestamp = time.time() % 1000
    if len(sys.argv) > 1:
        player = int(sys.argv[1])  # Either A or B
        if player != 0 and player != 1:
            print("Invalid player number. Please enter 0 or 1.")
            sys.exit()
        else:
            print("Player: " + str(player))
            if player == 1:
                port = 60060

    logging.basicConfig(
        filename="player_" + str(player) + ".log",
        format="%(asctime)s %(message)s",
        filemode="w",
    )
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    serve(port, timestamp)
