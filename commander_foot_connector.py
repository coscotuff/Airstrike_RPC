# File that connects the connector of team to the all the members of the team.
# It as a server for the connector to receive the red zone and return the appropriate response, as well as for the commander to the foot soldier
# It acts as a client for the foot soldiers and get the appropriate response from them

import logging
import random
from concurrent import futures
import sys
import threading
import time

import grpc
import soldier_pb2
import soldier_pb2_grpc
import connector_pb2
import connector_pb2_grpc


# Class for each soldier object that is initialised
class Server(soldier_pb2_grpc.AlertServicer):
    def __init__(self, node_number, lives, player, N, M):
        # Node number associated with each soldier
        self.node_number = node_number

        # Number of lives each soldier has
        self.lives = lives

        # Points each soldier is associated with
        self.points = lives

        # Team number that the soldier belongs to
        self.player = player

        # Size of the grid
        self.N = N

        # Initiliase soldier position and speed
        self.x = random.randint(0, self.N - 1)
        self.y = random.randint(0, self.N - 1)
        self.speed = random.randint(0, 4)

        # Port number for the connector, 50050 for player 0, 60060 for player 1
        self.connector_port = 50050 + self.player * 10010

        logger.debug("Soldier speed: " + str(self.speed))
        logger.debug("Soldier position: " + str(self.x) + ", " + str(self.y))
        logger.debug("Connector port: " + str(self.connector_port))

        # Initialise the battalion with all the soldiers
        self.battalion = [i for i in range(1, M + 1)]

        # Mutli-threaded call to register the newly initialised node with the connector
        threading.Thread(target=self.RegisterNodeRPCCall).start()

    # Making an RPC call to the connector to register the node

    def RegisterNodeRPCCall(self):
        with grpc.insecure_channel("localhost:" + str(self.connector_port)) as channel:
            stub = connector_pb2_grpc.PassAlertStub(channel)
            stub.RegisterNode(connector_pb2.Coordinate(x=self.x, y=self.y))
            logging.debug("Registered self to connector")

    # RPC access point the connector uses to send the red zone to the commander and get a status update

    def SendZone(self, request, context):
        logger.debug(
            "Received alert: "
            + str(request.pos.x)
            + ", "
            + str(request.pos.y)
            + "; Radius: "
            + str(request.radius)
        )
        logger.debug("Executing commander duties...")

        # Temp variables to keep track of important values
        hit_count = 0
        death_count = 0
        added_points = 0

        # port_base initialisation, 5005 for player 0, 6006 for player 1
        # node number will be appended to the end of this to generate the appropriate port number
        port_base = 5005 + 1001 * self.player

        # Iterate through all the soldiers in the battalion and alert them using RPC calls, then return their updated status
        for i in self.battalion:
            if i != self.node_number:
                with grpc.insecure_channel(
                    "localhost:" + str(port_base) + str(i)
                ) as channel:
                    stub = soldier_pb2_grpc.AlertStub(channel)
                    response = stub.UpdateStatus(
                        soldier_pb2.RedZone(
                            pos=soldier_pb2.Position(x=request.pos.x, y=request.pos.y),
                            radius=request.radius,
                        )
                    )

                # Calculate the hit count, death count, points, and remove the soldier from the battalion if they are killed
                if response.is_hit:
                    hit_count += 1
                    added_points += 1
                    if response.is_sink:
                        death_count += 1
                        added_points += response.points
                        self.battalion.remove(i)

            # Same thing needs to be done for the commander separately without using RPC calls
            else:
                hit = self.move(request.pos.x, request.pos.y, request.radius)
                if hit:
                    hit_count += 1
                    added_points += 1
                    if self.lives == 0:
                        death_count += 1
                        added_points += self.points

        current_commander = self.node_number

        # If the commander is killed, remove them from the battalion and promote a random soldier to commander
        # Update the current commander to be returned to the connector. This new commander will directly be connected to by the connector
        if self.lives == 0:
            self.battalion.remove(self.node_number)
            if len(self.battalion) == 0:
                # If the battalion is empty, then there is no commander, return -1 (this will end the game)
                current_commander = -1
            else:
                current_commander = random.sample(self.battalion, 1)[0]

                # The new commander needs to be promoted to commander using RPC calls and be given the current remaining battalion
                with grpc.insecure_channel(
                    "localhost:" + str(port_base) + str(current_commander)
                ) as channel:
                    stub = soldier_pb2_grpc.AlertStub(channel)
                    soldier_list = soldier_pb2.Battalion()
                    soldier_list.soldier_ids.extend(self.battalion)
                    response = stub.PromoteSoldier(soldier_list)

        return soldier_pb2.AttackStatus(
            death_count=death_count,
            hit_count=hit_count,
            points=added_points,
            current_commander=current_commander,
        )

    # Function used to update the soldier parameters when they are hit by a missile

    def RegisterHit(self):
        self.lives -= 1
        logger.debug("Soldier hit")
        if self.lives == 0:
            logger.debug("Soldier died")
        logger.debug("Soldier lives: " + str(self.lives))
        logger.debug("Soldier position: " + str(self.x) + ", " + str(self.y))
        return True

    # Default algorithm for the soldier to move out of the red zone if possible, else register a hit

    def move(self, hit_x, hit_y, radius):
        # Check if the soldier is in the red zone using manhattan distance
        if abs(hit_x - self.x) < radius and abs(hit_y - self.y) < radius:
            # If the soldier is in the red zone, try to move out of it
            if abs(min(self.x + self.speed, self.N - 1) - hit_x) >= radius:
                self.x = min(self.x + self.speed, self.N - 1)
            elif abs(max(self.x - self.speed, 0) - hit_x) >= radius:
                self.x = max(self.x - self.speed, 0)
            else:
                return self.RegisterHit()

            if abs(min(self.y + self.speed, self.N - 1) - hit_y) >= radius:
                self.y = min(self.y + self.speed, self.N - 1)
            elif abs(max(self.y - self.speed, 0) - hit_y) >= radius:
                self.y = max(self.y - self.speed, 0)
            else:
                return self.RegisterHit()
        logger.debug("Soldier lives: " + str(self.lives))
        logger.debug("Soldier position: " + str(self.x) + ", " + str(self.y))
        return False

    # RPC access point for the commander to send the red zone to the soldier and get a status update

    def UpdateStatus(self, request, context):
        logger.debug("Received red zone from commander")
        logger.debug(
            "Coordinates received: " + str(request.pos.x) + ", " + str(request.pos.y)
        )
        logger.debug("Radius received: " + str(request.radius))
        hit = self.move(request.pos.x, request.pos.y, request.radius)
        return soldier_pb2.SoldierStatus(
            is_sink=(self.lives == 0), is_hit=hit, points=self.points
        )

    # RPC access point for the commander to promote a soldier to a new commander with a new battalion

    def PromoteSoldier(self, request, context):
        logger.debug("Promoting soldier to commander")
        logger.debug("Soldier list: " + str(request.soldier_ids))
        self.battalion = [i for i in request.soldier_ids]
        return soldier_pb2.void()

    # RPC access point for the commander to initiate an attack on the opposing team by passing the attack to the connector.
    # One change made here is to introduce a type 5 missile. This is so that super soldiers with 4 speed wont always be able to escape.
    # This is introduce the possibility of a game over where all the soldiers die.

    def InitiateAttack(self, request, context):
        logger.debug("Initiating attack")
        with grpc.insecure_channel("localhost:" + str(self.connector_port)) as channel:
            stub = connector_pb2_grpc.PassAlertStub(channel)
            response = stub.Attack(
                connector_pb2.MissileStrike(
                    pos=connector_pb2.Coordinate(
                        x=random.randint(0, self.N - 1), y=random.randint(0, self.N - 1)
                    ),
                    type=random.randint(1, 5),
                )
            )
        return soldier_pb2.void()


def serve(node_number, lives, player, N, M):
    # Initialise the appropriate port for the soldier, depending on the player and node number 5005s for player 0, 6006s for player 1
    port = 50050 + player * 10010 + node_number

    # Initialise the server part of the soldiers
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    soldier_pb2_grpc.add_AlertServicer_to_server(
        Server(node_number=node_number, lives=lives, player=player, N=N, M=M), server
    )

    # Start the server
    server.add_insecure_port("[::]:" + str(port))
    server.start()
    print("Server started listening on port " + str(port) + ".")
    logger.debug("Soldier started listening on port " + str(port) + ".")
    server.wait_for_termination()


if __name__ == "__main__":
    # Accept grid size, soldier count, player number and node number in the command line argument if provided, else use default values
    node_number = 1
    lives = 3
    player = 0
    port = 50050

    # Random seed for the soldier
    random.seed(time.time() % 100)

    if len(sys.argv) > 1:
        player = int(sys.argv[3])  # Either A or B
        if player != 0 and player != 1:
            print("Invalid player number. Please enter 0 for A or 1 for B.")
            sys.exit()
        else:
            print("Player: " + str(player))
            if player == 1:
                port = 60060
        N = int(sys.argv[1])
        M = int(sys.argv[2])
        node_number = int(sys.argv[4])

        if node_number < 1 or node_number > M:
            print("Invalid node number. Please enter a value from 1 to " + str(M) + ".")
            sys.exit()
        else:
            print("Node number: " + str(node_number))
            port += node_number

    # Initialise the logger
    logging.basicConfig(
        filename="player_" + str(player) + "_soldier_" + str(node_number) + ".log",
        format="%(asctime)s %(message)s",
        filemode="w",
    )

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    serve(node_number, lives, player, N, M)
