# File that connects the opposing team to the commander of the team.
# It acts as a server for the opposing team to send the red zone and return the appropriate response.
# It acts as a client for the commander to send the strike and get the appropriate response.

import logging
import random
from concurrent import futures

import connector_pb2
import connector_pb2_grpc
import grpc
import soldier_pb2
import soldier_pb2_grpc
import sys


class Server(connector_pb2_grpc.PassAlertServicer):
    def __init__(self, N, M, player):
        self.commander = -70
        self.battalion = [i for i in range(1, M + 1)]
        self.N = N
        self.player = player

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

        port_base = 5005

        if self.player == 1:
            port_base = 6006

        if self.commander == -70:
            self.commander = random.sample(self.battalion, 1)[0]
            logger.debug("Initial commander: " + str(self.commander))

        with grpc.insecure_channel("localhost:5005" + str(self.commander)) as channel:
            stub = soldier_pb2_grpc.AlertStub(channel)
            response = stub.SendZone(
                soldier_pb2.RedZone(
                    pos=soldier_pb2.Position(x=request.pos.x, y=request.pos.y),
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
            logger.debug("Game over")
            print("Sorry, you lose!")
            return connector_pb2.Hit(hits=-1, kills=-1, points=-1)
            exit(0)

        return connector_pb2.Hit(
            hits=response.hit_count, kills=response.death_count, points=response.points
        )

    def Attack(self, request, context):
        port = 50050
        if self.player == 1:
            port = 60060
        with grpc.insecure_channel("localhost:60060") as channel:
            stub = connector_pb2_grpc.PassAlertStub(channel)
            response = stub.SendAlert(
                connector_pb2.MissileStrike(
                    pos=connector_pb2.Coordinate(
                        x=random.randn(0, self.N - 1), y=random.randn(0, self.N - 1)
                    ),
                    type=random.randn(1, 4),
                )
            )
        return response


def serve(N, M, player):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    connector_pb2_grpc.add_PassAlertServicer_to_server(Server(N = N, M = M, player = player), server)
    port = 50050
    if player == 1:
        port = 60060
    server.add_insecure_port("[::]:" + str(port))
    server.start()
    print("Server started listening on port " + str(port) + "...")
    
    server.wait_for_termination()


if __name__ == "__main__":
    # Take size of field and number of soldiers as command line argument, default to 10 and 5 , pass it to serve()
    N = 10
    M = 5
    player = 0

    if len(sys.argv) > 1:
        N = int(sys.argv[1])
        M = int(sys.argv[2])
        player = int(sys.argv[3])

    logging.basicConfig(
        filename="player_" + str(player) + "_connector.log",
        format="%(asctime)s %(message)s",
        filemode="w",
    )

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    serve(N, M, player)
