# File that connects the opposing team to the commander of the team.
# It acts as a server for the opposing team to send the red zone and return the appropriate response.
# It acts as a client for the commander to send the strike and get the appropriate response.

import logging
import os
import random
from concurrent import futures
import threading

import connector_pb2
import connector_pb2_grpc
import grpc
import soldier_pb2
import soldier_pb2_grpc
import sys


class Server(connector_pb2_grpc.PassAlertServicer):
    def __init__(self, N, M, player):
        self.commander = -70
        self.num_nodes = 0
        self.battalion = [i for i in range(1, M + 1)]
        self.N = N
        self.player = player
        self.opposition_port = 50050 + (1 - self.player) * 10010
        self.port = 50050 + self.player * 10010
        self.enemy_registered = False

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
        
        x = threading.Thread(target=self.AttackRPCCall, daemon=True)
        x.start()
        return connector_pb2.Hit(
            hits=response.hit_count, kills=response.death_count, points=response.points
        )
            
    def AttackRPCCall(self):
        # Send RPC to commander to Attack
        logger.debug("Sending RPC to commander to Attack")
        with grpc.insecure_channel("localhost:" + str(self.port + self.commander)) as channel:
            stub = soldier_pb2_grpc.AlertStub(channel)
            response = stub.InitiateAttack(soldier_pb2.void())

    def Attack(self, request, context):
        port = 50050
        if self.player == 1:
            port = 60060
        with grpc.insecure_channel("localhost:" + str(self.opposition_port)) as channel:
            stub = connector_pb2_grpc.PassAlertStub(channel)
            response = stub.SendAlert(request)
        return response

    def RegisterEnemyRPCCall(self):
        logger.debug("Register to enemy...")
        with grpc.insecure_channel("localhost:" + str(self.opposition_port)) as channel:
            stub = connector_pb2_grpc.PassAlertStub(channel)
            response = stub.RegisterEnemy(soldier_pb2.void())
        logger.debug("Registered to enemy")

    def RegisterNode(self, request, context):
        logger.debug("Registering node: " + str(request.x) + ", " + str(request.y))
        self.num_nodes += 1
        if self.num_nodes == len(self.battalion):
            logger.debug("All nodes registered")
            x = threading.Thread(target=self.RegisterEnemyRPCCall, daemon=True)
            x.start()
        print("Returning void after RegisterNode")
        return soldier_pb2.void()
    
    def RegisterEnemy(self, request, context):
        logger.debug("Registering enemy: " + str(1 - self.player))
        if self.num_nodes == len(self.battalion) and self.player == 0:
            logger.debug("Both teams registered")
            logger.debug("Starting game...")

            if self.commander == -70:
                self.commander = random.sample(self.battalion, 1)[0]
                logger.debug("Initial commander: " + str(self.commander))
            # Send RPC to commander to Attack
            self.AttackRPCCall()
        return soldier_pb2.void()

def serve(N, M, player):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    connector_pb2_grpc.add_PassAlertServicer_to_server(Server(N = N, M = M, player = player), server)
    port = 50050
    if player == 1:
        port = 60060
    server.add_insecure_port("[::]:" + str(port))
    server.start()
    print("Server started listening on port " + str(port) + "...")
    logger.debug("Server started listening on port " + str(port) + "...")
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
