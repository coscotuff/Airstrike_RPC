# File that connects the connector of team to the all the members of the team.
# It as a server for the connector to receive the red zone and return the appropriate response, as well as for the commander to the foot soldier
# It acts as a client for the foot soldiers and get the appropriate response from them

import logging
import os
import random
import socket
import sys
import threading
import time
import tkinter as tk
from concurrent import futures
from tkinter import Canvas, messagebox

import grpc

import connector_pb2
import connector_pb2_grpc
import soldier_pb2
import soldier_pb2_grpc


def get_self_ip():
    try:
        # Create a socket object and connect to a remote host (e.g., Google's DNS server)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        # Get the local IP address
        self_ip = s.getsockname()[0]
        return self_ip
    except socket.error as e:
        print(f"Error: {e}")
        return None
    finally:
        s.close()

# Class for each soldier object that is initialised


class Server(soldier_pb2_grpc.AlertServicer):
    def __init__(self, node_number, lives, player, N, M, canvas, connector_ip):
        # Flag checking if the soldier is the commander
        self.is_commander = False
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

        self.connector_ip = connector_ip
        # Port number for the connector, 50050 for player 0, 60060 for player 1
        self.connector_port = 50050 + self.player * 10010

        # Get my ip address
        self.ip_address = get_self_ip()
        self.port_number = self.connector_port + self.node_number

        logger.debug("Soldier speed: " + str(self.speed))
        logger.debug("Soldier position: " + str(self.x) + ", " + str(self.y))
        logger.debug("Connector port: " + str(self.connector_port))

        # Initialise the battalion with all the soldiers
        self.battalion = []

        # Mutli-threaded call to register the newly initialised node with the connector
        threading.Thread(target=self.RegisterNodeRPCCall).start()

        self.canvas = canvas  # Store the canvas for GUI interaction

        # Create a soldier representation on the canvas
        self.soldier_shape = self.canvas.create_rectangle(
            self.x * GRID_CELL_SIZE,
            self.y * GRID_CELL_SIZE,
            (self.x + 1) * GRID_CELL_SIZE,
            (self.y + 1) * GRID_CELL_SIZE,
            fill=self.get_player_color(self.player),
        )

    # Making an RPC call to the connector to register the node

    def RegisterNodeRPCCall(self):
        with grpc.insecure_channel(self.connector_ip + ":" + str(self.connector_port)) as channel:
            stub = connector_pb2_grpc.PassAlertStub(channel)
            stub.RegisterNode(soldier_pb2.SoldierData(
                id=self.node_number, ip_address=self.ip_address, port=self.port_number))
            logging.debug("Registered self to connector")

    # RPC access point the connector uses to send the red zone to the commander and get a status update

    def SendZone(self, request, context):
        # Set the commander flag to true if it is not already set
        if self.is_commander == False:
            self.is_commander = True

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
            if i.id != self.node_number:
                with grpc.insecure_channel(
                    i.ip_address + ":" + str(i.port)
                ) as channel:
                    stub = soldier_pb2_grpc.AlertStub(channel)
                    response = stub.UpdateStatus(
                        soldier_pb2.RedZone(
                            pos=soldier_pb2.Position(
                                x=request.pos.x, y=request.pos.y),
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

        current_commander = [
            i for i in self.battalion if i.id == self.node_number][0]

        # If the commander is killed, remove them from the battalion and promote a random soldier to commander
        # Update the current commander to be returned to the connector. This new commander will directly be connected to by the connector
        if self.lives == 0:
            self.battalion.remove(
                [i for i in self.battalion if i.id == self.node_number][0])
            if len(self.battalion) == 0:
                # If the battalion is empty, then there is no commander, return -1 (this will end the game)
                current_commander = soldier_pb2.SoldierData(
                    id=-1, ip_address="", port=-1)
            else:
                current_commander = random.sample(self.battalion, 1)[0]

                # The new commander needs to be promoted to commander using RPC calls and be given the current remaining battalion
                with grpc.insecure_channel(
                    current_commander.ip_address +
                        ":" + str(current_commander.port)
                ) as channel:
                    stub = soldier_pb2_grpc.AlertStub(channel)
                    soldier_list = soldier_pb2.Battalion()
                    soldier_list.soldiers.extend(self.battalion)
                    response = stub.PromoteSoldier(soldier_list)

        return soldier_pb2.AttackStatus(
            death_count=death_count,
            hit_count=hit_count,
            points=added_points,
            current_commander=current_commander.id,
        )

    # Function to terminate soldier. It is called when the soldier dies.

    def terminate(self):
        time.sleep(5)
        os._exit(0)

    # Function used to update the soldier parameters when they are hit by a missile

    def RegisterHit(self):
        self.lives -= 1
        logger.debug("Soldier hit")
        if self.lives == 0:
            logger.debug("Soldier died")
            self.update_info()
            self.erase_soldier()
            threading.Thread(target=self.terminate).start()

        logger.debug("Soldier lives: " + str(self.lives))
        logger.debug("Soldier position: " + str(self.x) + ", " + str(self.y))
        return True

    # Move the box of the soldier to the new position

    def move_soldier(self, new_x, new_y):
        # Update the soldier's position on the canvas
        self.canvas.coords(
            self.soldier_shape,
            new_x * GRID_CELL_SIZE,
            new_y * GRID_CELL_SIZE,
            (new_x + 1) * GRID_CELL_SIZE,
            (new_y + 1) * GRID_CELL_SIZE,
        )

        if self.is_commander:
            canvas.itemconfig(self.soldier_shape, outline="gold", width=5)

    # Function to erase the soldier from the canvas

    def erase_soldier(self):
        # Remove the soldier from the canvas
        self.canvas.delete(self.soldier_shape)
        self.clear_grid()
        info_label.config(text="Soldier " + str(self.node_number) + " is dead")

    # Function to get the color of the soldier based on the player

    def get_player_color(self, player):
        # Define colors for different players
        return "blue" if player == 0 else "purple"

    # Function to update life and position information

    def update_info(self):
        info_label.config(
            text=f"Current Coordinates: ({self.x}, {self.y}) | Lives Left: {self.lives}"
        )

    # Function to change the color of a cell

    def change_color(self, x, y, color):
        canvas.itemconfig(grid[y][x], fill=color)

    # Function to display a red region on the grid based on center and radius

    def display_red_region(self, center_x, center_y, radius):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if abs(x - center_x) < radius and abs(y - center_y) < radius:
                    self.change_color(x, y, "red")

    # Function to clear the grid

    def clear_grid(self):
        for y in range(self.N):
            for x in range(self.N):
                self.change_color(x, y, DEFAULT_COLOR)

    # Function to handle attacks launched by the commander on the click of the button

    def button_click(self, x, y, attacking_phase_window):
        # Destroy the attacking phase window
        attacking_phase_window.destroy()

        # Send the chosen attack coordinates to the connector
        with grpc.insecure_channel(self.connector_ip + ":" + str(self.connector_port)) as channel:
            stub = connector_pb2_grpc.PassAlertStub(channel)
            response = stub.Attack(
                connector_pb2.MissileStrike(
                    pos=connector_pb2.Coordinate(
                        x=x, y=y
                    ),
                    type=random.randint(1, 5),
                )
            )

    # Timeout function to close the attacking phase window for the commander to select the coordinates to attack with random coordinates

    def close_attacking_phase_window(self, attacking_phase_window):
        # Destroy the attacking phase window
        attacking_phase_window.destroy()

        # Send the randomised attack coordinates to the connector
        with grpc.insecure_channel(self.connector_ip + ":" + str(self.connector_port)) as channel:
            stub = connector_pb2_grpc.PassAlertStub(channel)
            response = stub.Attack(
                connector_pb2.MissileStrike(
                    pos=connector_pb2.Coordinate(
                        x=random.randint(0, self.N - 1), y=random.randint(0, self.N - 1)
                    ),
                    type=random.randint(1, 5),
                )
            )

    # Function to open the attacking phase window for the commander to select the coordinates to attack

    def open_attacking_phase(self, window):
        # Create a new window for the attacking phase
        attacking_phase_window = tk.Toplevel(window)
        attacking_phase_window.title("Attacking Phase")

        # Create a canvas to draw the grid in the attacking phase window
        attacking_phase_canvas = tk.Canvas(
            attacking_phase_window, width=N * GRID_CELL_SIZE, height=N * GRID_CELL_SIZE)
        attacking_phase_canvas.pack()

        # Create a 2D list to store the grid buttons
        attacking_phase_buttons = []

        # Initialize the grid buttons in the attacking phase window
        for y in range(GRID_SIZE):
            row = []
            for x in range(GRID_SIZE):
                button = tk.Button(
                    attacking_phase_canvas,
                    text=f"({x}, {y})",
                    # Pass coordinates to button_click function
                    command=lambda x=x, y=y: self.button_click(
                        x, y, attacking_phase_window)
                )
                button.grid(row=y, column=x)
                row.append(button)
            attacking_phase_buttons.append(row)

        # Set a timeout timer for the commander to select the coordinates to attack
        attacking_phase_window.after(
            10000, lambda: self.close_attacking_phase_window(attacking_phase_window))

    # Default algorithm for the soldier to move out of the red zone if possible, else register a hit

    def move(self, hit_x, hit_y, radius):
        self.clear_grid()
        self.display_red_region(hit_x, hit_y, radius)
        canvas.update()
        self.move_soldier(self.x, self.y)
        self.update_info()

        # Check if the soldier is in the red zone using manhattan distance
        if abs(hit_x - self.x) < radius and abs(hit_y - self.y) < radius:
            # If the soldier is in the red zone, try to move out of it
            if abs(min(self.x + self.speed, self.N - 1) - hit_x) >= radius:
                self.x = min(self.x + self.speed, self.N - 1)
            elif abs(max(self.x - self.speed, 0) - hit_x) >= radius:
                self.x = max(self.x - self.speed, 0)
            else:
                self.move_soldier(self.x, self.y)
                self.update_info()
                return self.RegisterHit()

            if abs(min(self.y + self.speed, self.N - 1) - hit_y) >= radius:
                self.y = min(self.y + self.speed, self.N - 1)
            elif abs(max(self.y - self.speed, 0) - hit_y) >= radius:
                self.y = max(self.y - self.speed, 0)
            else:
                self.move_soldier(self.x, self.y)
                self.update_info()
                return self.RegisterHit()
        logger.debug("Soldier lives: " + str(self.lives))
        logger.debug("Soldier position: " + str(self.x) + ", " + str(self.y))
        self.move_soldier(self.x, self.y)
        self.update_info()
        return False

    # RPC access point for the commander to send the red zone to the soldier and get a status update

    def UpdateStatus(self, request, context):
        logger.debug("Received red zone from commander")
        logger.debug(
            "Coordinates received: " +
            str(request.pos.x) + ", " + str(request.pos.y)
        )
        logger.debug("Radius received: " + str(request.radius))
        hit = self.move(request.pos.x, request.pos.y, request.radius)
        return soldier_pb2.SoldierStatus(
            is_sink=(self.lives == 0), is_hit=hit, points=self.points
        )

    # RPC access point for the commander to promote a soldier to a new commander with a new battalion

    def PromoteSoldier(self, request, context):
        logger.debug("Promoting soldier to commander")
        self.is_commander = True
        self.battalion = request.soldiers
        return soldier_pb2.void()

    # RPC access point for the commander to initiate an attack on the opposing team by passing the attack to the connector.
    # One change made here is to introduce a type 5 missile. This is so that super soldiers with 4 speed wont always be able to escape.
    # This is introduce the possibility of a game over where all the soldiers die.

    def InitiateAttack(self, request, context):
        logger.debug("Initiating attack")

        # Opens an attacking window for the commander to select the coordinates to attack, will automatically close after some time
        # and select a random coordinates if the commander does not select any
        self.open_attacking_phase(window)

        return soldier_pb2.void()


def serve(node_number, lives, player, N, M, canvas, server_ip):
    # Initialise the appropriate port for the soldier, depending on the player and node number 5005s for player 0, 6006s for player 1
    port = 50050 + player * 10010 + node_number

    # Initialise the server part of the soldiers
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    soldier_pb2_grpc.add_AlertServicer_to_server(
        Server(node_number=node_number, lives=lives, player=player,
               N=N, M=M, canvas=canvas, connector_ip=server_ip), server
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
    server_ip = "localhost"

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

        if len(sys.argv) > 5:
            server_ip = sys.argv[5]

    # Initialise the logger
    logging.basicConfig(
        filename="player_" + str(player) + "_soldier_" +
        str(node_number) + ".log",
        format="%(asctime)s %(message)s",
        filemode="w",
    )

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Create a tkinter window and canvas for GUI
    window = tk.Tk()
    window.title("Soldier Grid")

    # Initialize game variables
    GRID_SIZE = N
    GRID_CELL_SIZE = 40  # Adjust this for cell size
    DEFAULT_COLOR = "white"
    MAX_LIVES = 5
    MAX_TURNS = 10

    current_x, current_y = 0, 0
    lives_left = MAX_LIVES
    turns_left = MAX_TURNS

    canvas = Canvas(
        window, width=GRID_SIZE * GRID_CELL_SIZE, height=GRID_SIZE * GRID_CELL_SIZE
    )
    canvas.pack()

    grid = []

    for y in range(GRID_SIZE):
        row = []
        for x in range(GRID_SIZE):
            cell = canvas.create_rectangle(
                x * GRID_CELL_SIZE,
                y * GRID_CELL_SIZE,
                (x + 1) * GRID_CELL_SIZE,
                (y + 1) * GRID_CELL_SIZE,
                fill=DEFAULT_COLOR,
                outline="black",
            )
            row.append(cell)
        grid.append(row)

    # Create a label for displaying information
    info_label = tk.Label(window, text="")
    info_label.pack()

    threading.Thread(target=serve, args=(node_number, lives,
                     player, N, M, canvas, server_ip)).start()
    window.mainloop()
