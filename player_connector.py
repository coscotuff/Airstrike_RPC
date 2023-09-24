# File that connects the opposing team to the commander of the team.
# It acts as a server for the opposing team to send the red zone and return the appropriate response.
# It acts as a client for the commander to send the strike and get the appropriate response.

import logging
import os
import random
from concurrent import futures
import threading
import time
import sys

import connector_pb2
import connector_pb2_grpc
import grpc
import soldier_pb2
import soldier_pb2_grpc



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
        self.points = 0
        self.opponent_points = -1
        self.turns = 15

        # Add self and opponent timmestamps
        self.my_timestamp = -1
        self.opponent_timestamp = -1

    def SendAlert(self, request, context):
        logger.debug(
            "Received strike from enemy: "
            + str(request.pos.x)
            + ", "
            + str(request.pos.y)
            + "; Type: "
            + str(request.type)
        )

        if(request.type == -1):
            threading.Thread(target=self.AttackRPCCall, daemon=True).start()
            return connector_pb2.Hit(
                hits=0, kills=0, points=0
            )

        # Send RPC to commander to Attack
        logger.debug("Executing connector duties...")

        if self.commander == -70:
            self.commander = random.sample(self.battalion, 1)[0]
            logger.debug("Initial commander: " + str(self.commander))

        with grpc.insecure_channel(
            "localhost:" + str(self.port + self.commander)
        ) as channel:
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
            # Initiate exit here (call initiate exit function) using multithreading
            logger.debug("Exiting...")
            threading.Thread(target=self.TerminateProgram, daemon=True).start()
            return connector_pb2.Hit(hits=-1, kills=-1, points=-1)

        
        threading.Thread(target=self.AttackRPCCall, daemon=True).start()

        return connector_pb2.Hit(
            hits=response.hit_count, kills=response.death_count, points=response.points
        )

    def AttackRPCCall(self):
        # Send RPC to commander to Attack
        if(self.turns == 0):
            with grpc.insecure_channel("localhost:" + str(self.opposition_port)) as channel:
                stub = connector_pb2_grpc.PassAlertStub(channel)
                response = stub.SendAlert(connector_pb2.MissileStrike(pos=connector_pb2.Coordinate(x=-1, y=-1), type=-1))
            return
        
        logger.debug("Sending RPC to commander to Attack")
        with grpc.insecure_channel(
            "localhost:" + str(self.port + self.commander)
        ) as channel:
            stub = soldier_pb2_grpc.AlertStub(channel)
            response = stub.InitiateAttack(soldier_pb2.void())

    def Attack(self, request, context):
        with grpc.insecure_channel("localhost:" + str(self.opposition_port)) as channel:
            stub = connector_pb2_grpc.PassAlertStub(channel)
            response = stub.SendAlert(request)
        logger.debug("Received response from enemy")

        # Decrementing turns
        self.turns = max(0, self.turns - 1)

        # If hit count is non-zero, increment the number of turns
        if response.hits > 0:
            self.turns += 1

            # If kill count is non-zero, increment the number of turns equivalent to the number of kills
            if response.kills > 0:
                self.turns += response.kills

        # If turns is zero, game over, check which player won by comparing points. This can be done using rpc call to opposition
        if self.turns == 0 or response.points == -1:
            if response.points == -1:
                print("Congratulations, you win!")
                # Initiate exit here (call initiate exit function) using multithreading
                logger.debug("Exiting...")
                threading.Thread(target=self.TerminateProgram, daemon=True).start()

            else:
                # To compare scores, send score to opponent. If opponent is not yet done, then wait for opponent to send score
                # Return the appropriate score to the connector (-1 if opponent is not yet done)
                logger.debug("No more turns!")
                logger.debug("Comparing scores...")
                self.opponent_points = self.RegisterEnemyPoints()

                if self.opponent_points != -1:
                    self.TallyResults()

        self.points += response.points
        return response

    def TallyResults(self):
        if self.points > self.opponent_points:
            print("Congratulations, you win!")
        elif self.points < self.opponent_points:
            print("Sorry, you lose!")
        else:
            print("It's a tie!")
        
        # initiate exit here (call initiate exit function)
        logger.debug("Exiting...")
        self.TerminateProgram()

    def RegisterEnemyPoints(self):
        logger.debug("Sending points to enemy...")
        with grpc.insecure_channel("localhost:" + str(self.opposition_port)) as channel:
            stub = connector_pb2_grpc.PassAlertStub(channel)
            response = stub.GetPoints(connector_pb2.Points(points=self.points))
        logger.debug("Received enemy points: " + str(response.points))
        return response.points

    def GetPoints(self, request, context):
        logger.debug("Received points from enemy: " + str(request.points))
        self.opponent_points = request.points
    
        if self.turns == 0:
            # Apply multithreading to call TallyResults() function and return the points
            logger.debug("Sending back current points to enemy: " + str(self.points))
            threading.Thread(target=self.TallyResults, daemon=True).start()
            return connector_pb2.Points(points=self.points)
        else:
            logger.debug("Sending back current points to enemy: -1")
            return connector_pb2.Points(points=-1)

    def RegisterEnemyRPCCall(self):
        logger.debug("Register to enemy...")
        self.my_timestamp = time.time() % 10000

        if self.opponent_timestamp != -1:
            self.my_timestamp = 1 + self.opponent_timestamp
        with grpc.insecure_channel("localhost:" + str(self.opposition_port)) as channel:
            stub = connector_pb2_grpc.PassAlertStub(channel)
            response = stub.RegisterEnemy(
                connector_pb2.Timestamp(timestamp=self.my_timestamp)
            )
        logger.debug("Registered to enemy")

    def CompareTimestamps(self):
        if self.my_timestamp < self.opponent_timestamp or (
            self.my_timestamp == self.opponent_timestamp and self.player == 0
        ):
            # Attack
            logger.debug("Both teams registered")
            logger.debug("Starting game...")

            if self.commander == -70:
                self.commander = random.sample(self.battalion, 1)[0]
                logger.debug("Initial commander: " + str(self.commander))
            # Send RPC to commander to Attack
            self.AttackRPCCall()

    def RegisterNode(self, request, context):
        logger.debug("Registering node: " + str(request.x) + ", " + str(request.y))
        self.num_nodes += 1
        if self.num_nodes == len(self.battalion):
            logger.debug("All nodes registered")
            threading.Thread(target=self.RegisterEnemyRPCCall, daemon=True).start()
        print("Returning void after RegisterNode")
        return soldier_pb2.void()

    def RegisterEnemy(self, request, context):
        logger.debug("Registering enemy: " + str(1 - self.player))
        self.opponent_timestamp = request.timestamp
        if self.my_timestamp != -1:
            # Compare the timestamps and intitiate the correct attack
            threading.Thread(target=self.CompareTimestamps, daemon=True).start()
        return soldier_pb2.void()
    
    def TerminateProgram(self):
        # Nuclear launch codes
        MIN_PID = os.getpid()
        print("KILLING")
        os.system("kill -9 $(pgrep python3 | awk '$1>=" + str(MIN_PID)  + "')")
        sys.exit(0)


def serve(N, M, player):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    connector_pb2_grpc.add_PassAlertServicer_to_server(
        Server(N=N, M=M, player=player), server
    )
    port = 50050 + player * 10010  # 50050 for player 0, 60060 for player 1
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

    # Set random seed
    random.seed(time.time() % 100)

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
