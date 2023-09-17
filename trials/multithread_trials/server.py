import grpc
from concurrent import futures
import time
import threading

import multi_pb2
import multi_pb2_grpc

class GameService(multi_pb2_grpc.GameServiceServicer):

    def endTurn(self, request, context):
        # Start a new thread to run the initiate function
        threading.Thread(target=self.initiate).start()
        
        # Return a response to the client immediately
        return multi_pb2.EndTurnResponse(result="SUCCESS")

    def initiate(self):
        # Simulate some work in the initiate function
        time.sleep(5)
        print("initiate function completed")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    multi_pb2_grpc.add_GameServiceServicer_to_server(GameService(), server)
    server.add_insecure_port('[::]:50050')
    server.start()
    print("Server started")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()