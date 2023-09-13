from concurrent import futures
import logging

import grpc
import test_pb2
import test_pb2_grpc

logging.basicConfig(filename="server.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
 
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Server(test_pb2_grpc.AlertServicer):
    def SendZone(self, request, context):
        logger.debug("Received red zone from commander")
        logger.debug("Coordinates received: " + str(request.pos.x) + ", " + str(request.pos.y))
        logger.debug("Radius received: " + str(request.radius))
        return test_pb2.SoldierStatus(is_alive=True, pos=test_pb2.Position(x=3, y=0))
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    test_pb2_grpc.add_AlertServicer_to_server(Server(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started listening on port 50051")
    server.wait_for_termination()
    
if __name__ == "__main__":
    logging.basicConfig()
    serve()
