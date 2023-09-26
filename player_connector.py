# File that connects the opposing team to the commander of the team.
# It acts as a server for the opposing team to send the red zone and return the appropriate response.
# It acts as a client for the commander to send the strike to get the appropriate response, and retrieve the attack from

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


# This is the class defining the connector. It acts as a missile detection system and alerts the commander when the enemy launches a strike.
# As such, it is also a conduit for the enemy object connector to be able to send missile strikes and return the consequences of the same.
# It also acts as the conduit for the commander to launch a missile at the opposing team.


class Server(connector_pb2_grpc.PassAlertServicer):
    def __init__(self, N, M, player):
        # Current commander to send the alert RPC calls to.
        self.commander = -70

        # Initialise the initial number of connected nodes to the connector to be 0.
        # This quantity will later be used to ensure that the correct number of nodes have connected.
        self.num_nodes = 0

        # Initialise the battalion, grid size, and player number of the team.
        self.battalion = [i for i in range(1, M + 1)]
        self.N = N
        self.player = player

        # Initialise the source and destination ports
        self.opposition_port = 60060 - self.player * 10010
        self.port = 50050 + self.player * 10010

        # Flag to check if all enemy nodes have successfully connected with the enemy connector. False means that the
        # enemy has not yet finished connecting and therefore this connector has not yet received an RPC notifying it about the same.
        self.enemy_registered = False

        # Keeping track of personal points and turns left
        self.points = 0
        self.turns = 15

        # Used once all the turns of the team have ended to compare and see who has won. It doubles as a flag. -1 means that the
        # enemy has not yet run out of turns and therefore this connector has not yet received an RPC notifying it about the same.
        self.opponent_points = -1

        # Add self and opponent timmestamps
        self.my_timestamp = -1
        self.opponent_timestamp = -1


    # This is the main function that the enemy connector calls via an RPC as a form of an attack.
    # This function also doubles as the alerting defense system that only the commander has access to.
    # It will send an alert to the commander via an RPC call.

    def SendAlert(self, request, context):
        
        # Request type of -1 indicates that the opposing team is done with all of its moves. It means that, no actual
        # missile has been launched. This is used to call the Attack function via multithreading in response to uphold the turn by turn protocol being followed.
        if request.type == -1:
            threading.Thread(target=self.AttackRPCCall, daemon=True).start()
            return connector_pb2.Hit(hits=0, kills=0, points=0)

        logger.debug(
            "Received strike from enemy: "
            + str(request.pos.x)
            + ", "
            + str(request.pos.y)
            + "; Type: "
            + str(request.type)
        )

        logger.debug("Executing connector duties...")

        # If this is the first time the connector is executing duties, it has yet to select a commander. So it selects an initial commander.
        if self.commander == -70:
            self.commander = random.sample(self.battalion, 1)[0]
            logger.debug("Initial commander: " + str(self.commander))

        # RPC call to the commander node alerting it of the missile. This call returns the damage caused by the missile.
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

        # Keep refreshing current commander after each response in case the commander has changed
        self.commander = response.current_commander
        
        # All the connector's soldiers are dead. The opposing team wins
        if self.commander == -1:
            # Game over
            logger.debug("Game over")
            print("Sorry, you lose!")
            # Initiate exit here (call initiate exit function) using multithreading
            logger.debug("Exiting...")
            threading.Thread(target=self.TerminateProgram, daemon=True).start()
            return connector_pb2.Hit(hits=-1, kills=-1, points=-1)

        # Call an attacking rpc call to the commander in response to the attack (enforcing the turn by turn protocol)
        threading.Thread(target=self.AttackRPCCall, daemon=True).start()

        return connector_pb2.Hit(
            hits=response.hit_count, kills=response.death_count, points=response.points
        )


    # Attacking RPC call asking commander to launch missile.

    def AttackRPCCall(self):
        
        # If you have run of turns and therefore missiles to launch, simply send dummy coordinates to opposing team's connector with type -1.
        if self.turns == 0:
            with grpc.insecure_channel(
                "localhost:" + str(self.opposition_port)
            ) as channel:
                stub = connector_pb2_grpc.PassAlertStub(channel)
                response = stub.SendAlert(
                    connector_pb2.MissileStrike(
                        pos=connector_pb2.Coordinate(x=-1, y=-1), type=-1
                    )
                )
            return

        # Send RPC to commander to Attack
        logger.debug("Sending RPC to commander to Attack")
        with grpc.insecure_channel(
            "localhost:" + str(self.port + self.commander)
        ) as channel:
            stub = soldier_pb2_grpc.AlertStub(channel)
            response = stub.InitiateAttack(soldier_pb2.void())


    # RPC function called by commander to send the missile to the opposing team.

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
                # Returns the appropriate score to the connector (-1 if opponent is not yet done)
                logger.debug("No more turns!")
                logger.debug("Comparing scores...")

                # Checking for enemy points once the connector is done with its turns
                self.opponent_points = self.RegisterEnemyPoints()

                # If the opponent is also done and has sent an RPC with its score, then we can compare scores and decide who is the  winner.
                if self.opponent_points != -1:
                    self.TallyResults()

        self.points += response.points
        return response
    

    # Function tallying scores and deciding who won.

    def TallyResults(self):
        if self.points > self.opponent_points:
            print("Congratulations, you win!")
            logger.debug("Congratulations, you win!")
        elif self.points < self.opponent_points:
            print("Sorry, you lose!")
            logger.debug("Sorry, you lose!")
        else:
            print("It's a tie!")
            logger.debug("It's a tie!")

        # initiate exit here (call initiate exit function)
        logger.debug("Exiting...")
        self.TerminateProgram()


    # Function for sending points to the enemy and getting a response with their points as well.

    def RegisterEnemyPoints(self):
        logger.debug("Sending points to enemy...")
        with grpc.insecure_channel("localhost:" + str(self.opposition_port)) as channel:
            stub = connector_pb2_grpc.PassAlertStub(channel)
            response = stub.GetPoints(connector_pb2.Points(points=self.points))
        logger.debug("Received enemy points: " + str(response.points))
        return response.points
    

    # RPC function for receiving points from the enemy once they are out of turns, and returning own points as well. Returns -1 if the turns are not over.
    # Return the current points if all the turns are over. Also calls Tally Results function to immediately calculate if it won.

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


    # Once all the nodes of the connector have connected, this function is called. It sends to the enemy a message via an RPC call
    # that it is ready to start along with the current timestamp. Timestamp is used for the turn-by-turn protocol being enforced
    # to decide which team will start. If player has already received a timestamp, it means that the opponent was already and therefore we allow it to go first
    # by assigning the connector's timestamp to be one higher than that of the opponent.

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


    # Function called by the RegisterEnemy RPC function if the connector is ready as well.

    def CompareTimestamps(self):
        if self.my_timestamp < self.opponent_timestamp or (
            self.my_timestamp == self.opponent_timestamp and self.player == 0
        ):
            # Attack if timestamp is lesser than opponent's. If equal, then by default player 0 will go first.
            logger.debug("Both teams registered")
            logger.debug("Starting game...")

            # Same logic as in SendAlert()
            if self.commander == -70:
                self.commander = random.sample(self.battalion, 1)[0]
                logger.debug("Initial commander: " + str(self.commander))

            # Send RPC to commander to Attack
            self.AttackRPCCall()


    # RPC function called by each node informing connector that it is ready. If all the required nodes have connected, then the enemy is notified about the same.

    def RegisterNode(self, request, context):
        logger.debug("Registering node: " + str(request.x) + ", " + str(request.y))
        self.num_nodes += 1
        if self.num_nodes == len(self.battalion):
            logger.debug("All nodes registered")
            threading.Thread(target=self.RegisterEnemyRPCCall, daemon=True).start()
        print("Returning void after RegisterNode")
        return soldier_pb2.void()


    # RPC function called by enemy to notify and register its timestamp. If the connector is also ready, then trigger the CompareTimestamps method and start the process.

    def RegisterEnemy(self, request, context):
        logger.debug("Registering enemy: " + str(1 - self.player))
        self.opponent_timestamp = request.timestamp
        
        if self.my_timestamp != -1:
            # Compare the timestamps and intitiate the correct attack
            threading.Thread(target=self.CompareTimestamps, daemon=True).start()
        return soldier_pb2.void()


    # Nuclear launch codes to terminate all the programs initialised by the bash shell script

    def TerminateProgram(self):
        # Nuclear launch codes
        MIN_PID = os.getpid()
        print("KILLING")
        os.system("kill -9 $(pgrep python3 | awk '$1>=" + str(MIN_PID) + "')")
        sys.exit(0)


def serve(N, M, player):
    
    # Initialising the connector server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    connector_pb2_grpc.add_PassAlertServicer_to_server(
        Server(N=N, M=M, player=player), server
    )
    port = 50050 + player * 10010  # 50050 for player 0, 60060 for player 1
    
    # Starting the server
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

    # Intitialising the logger
    logging.basicConfig(
        filename="player_" + str(player) + "_connector.log",
        format="%(asctime)s %(message)s",
        filemode="w",
    )

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    serve(N, M, player)
