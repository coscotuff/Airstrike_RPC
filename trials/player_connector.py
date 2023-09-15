# File that connects the opposing team to the commander of the team.
# It acts as a server for the opposing team to send the red zone and return the appropriate response.
# It acts as a client for the commander to send the strike and get the appropriate response.

from concurrent import futures
import logging
import grpc
import connector_pb2
import connector_pb2_grpc
import random

logging.basicConfig(
    filename="server.log", format="%(asctime)s %(message)s", filemode="w"
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Server(connector_pb2_grpc.AlertServicer):
    def __init__(self):
        self.intial_set = False
        self.commander = -1
        self.battalion = [i for i in range(1, 6)]

    def SendAlert(self, request, context):
        logger.debug(
            "Received strike from enemy: "
            + str(request.pos.x)
            + ", "
            + str(request.pos.y)
            + "; Type: "
            + str(request.type)
        )
        logger.debug("Executing connector duties...")

        if self.initial_set == False:
            self.intitial_set = True
            self.commander = random.sample(self.battalion, 1)[0]
            
        with grpc.insecure_channel("localhost:5005" + str(self.commander)) as channel:
            stub = connector_pb2_grpc.AlertStub(channel)
            response = stub.SendZone(
                connector_pb2.MissileStrike(
                    pos=connector_pb2.Position(x=request.pos.x, y=request.pos.y),
                    radius=request.type,
                )
            )

        logger.debug("Hits: " + str(response.hit_count))
        logger.debug("Kills: " + str(response.death_count))
        logger.debug("Points added: " + str(response.points))
        logger.debug("Current commander: " + str(response.current_commander))

        self.commander = response.current_commander
        
        if self.commander == -1:
            # Game over
            self.initial_set = False

        return connector_pb2.Hit(
            hits=response.hit_count, kills=response.death_count, points=response.points
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    connector_pb2_grpc.add_AlertServicer_to_server(Server(), server)
    server.add_insecure_port("[::]:50050")
    server.start()
    print("Server started listening on port 50050")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
