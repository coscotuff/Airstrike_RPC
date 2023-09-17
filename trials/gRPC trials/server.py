import logging
import random
from concurrent import futures

import grpc

import test_pb2
import test_pb2_grpc

logging.basicConfig(filename="server.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
 
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class Server(test_pb2_grpc.AlertServicer):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.speed = random.randint(0, 4)
        logger.debug("Soldier speed: " + str(self.speed))
        self.lives = 3
        self.N = 10
    
    def RegisterHit(self):
        self.lives -= 1
        logger.debug("Soldier hit")
        if self.lives == 0:
            logger.debug("Soldier died")
        return True
    def move(self, hit_x, hit_y, radius):
        # Check if the soldier is in the red zone using manhattan distance
        if abs(hit_x - self.x) + abs(hit_y - self.y) <= radius:
            # If the soldier is in the red zone, try to move out of it
            if abs(min(self.x + self.speed, self.N -1) - hit_x) > radius:
                self.x = min(self.x + self.speed, self.N -1)
            elif abs(max(self.x - self.speed, 0) - hit_x) > radius:
                self.x = max(self.x - self.speed, 0)
            else:
                return self.RegisterHit()
            
            if abs(min(self.y + self.speed, self.N -1) - hit_y) > radius:
                self.y = min(self.y + self.speed, self.N -1)
            elif abs(max(self.y - self.speed, 0) - hit_y) > radius:
                self.y = max(self.y - self.speed, 0)
            else:
                return self.RegisterHit()
        return False
    
    def SendZone(self, request, context):
        logger.debug("Received red zone from commander")
        logger.debug("Coordinates received: " + str(request.pos.x) + ", " + str(request.pos.y))
        logger.debug("Radius received: " + str(request.radius))
        hit = self.move(request.pos.x, request.pos.y, request.radius)
        return test_pb2.SoldierStatus(is_alive=(self.lives>0), is_hit=hit)
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    test_pb2_grpc.add_AlertServicer_to_server(Server(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started listening on port 50051")
    server.wait_for_termination()
    
if __name__ == "__main__":
    serve()
