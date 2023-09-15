# File that connects the connector of team to the all the members of the team.
# Could act as a server for the opposing team to send the red zone and return the appropriate response, as well as to teh commamnder as a foot soldier
# Could act as a client for the foot soldiers and potentially secondary commander client to send the strike to get the appropriate response.

from concurrent import futures
import logging
import grpc
import soldier_pb2
import soldier_pb2_grpc
import random

logging.basicConfig(
    filename="server.log", format="%(asctime)s %(message)s", filemode="w"
)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class Server(soldier_pb2_grpc.AlertServicer):
    def __init__(self):
        self.node_number = 1
        self.points = 5
        self.is_commander = False
        self.N = 10
        self.x = random.randint(0, self.N - 1)
        self.y = random.randint(0, self.N - 1)
        self.speed = random.randint(0, 4)
        logger.debug("Soldier speed: " + str(self.speed))
        self.lives = 5
        self.battalion = [i for i in range(1, 6)]

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

        hit_count = 0
        death_count = 0
        added_points = 0

        for i in self.battalion:
            if i != self.node_number:
                with grpc.insecure_channel("localhost:5005" + str(i)) as channel:
                    stub = soldier_pb2_grpc.AlertStub(channel)
                    response = stub.UpdateStatus(
                        soldier_pb2.RedZone(
                            pos=soldier_pb2.Position(x=request.pos.x, y=request.pos.y),
                            radius=request.range,
                        )
                    )

                if response.is_hit:
                    hit_count += 1
                    added_points += 1
                    if response.is_sink:
                        death_count += 1
                        added_points += response.points
                        self.battalion.remove(i)
            else:
                hit = self.move(request.pos.x, request.pos.y, request.radius)
                if hit:
                    hit_count += 1
                    added_points += 1
                    if self.lives == 0:
                        death_count += 1
                        added_points += self.points
        current_commander = self.node_number

        if self.lives == 0:
            self.battalion.remove(self.node_number)
            if len(self.battalion) == 0:
                current_commander = -1
            else:
                current_commander = random.sample(self.battalion, 1)[0]
                with grpc.insecure_channel(
                    "localhost:5005" + str(current_commander)
                ) as channel:
                    stub = soldier_pb2_grpc.AlertStub(channel)
                    soldier_list = soldier_pb2.Battalion()
                    for i in self.battalion:
                        soldier_list.soldier_ids.add(i)
                    response = stub.PromoteSoldier(soldier_list)

        return soldier_pb2.AttackStatus(
            death_count=death_count,
            hit_count=hit_count,
            points=added_points,
            current_commander=current_commander,
        )

    def RegisterHit(self):
        self.lives -= 1
        logger.debug("Soldier hit")
        if self.lives == 0:
            logger.debug("Soldier died")
        return True

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
        return False

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

    def PromoteSoldier(self, request, context):
        logger.debug("Promoting soldier to commander")
        logger.debug("Soldier list: " + str(request.soldier_ids))
        self.is_commander = True
        self.battalion = [i for i in request.soldier_ids]
        return


def serve():
    port = 50051
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    soldier_pb2_grpc.add_AlertServicer_to_server(Server(), server)
    server.add_insecure_port("[::]:" + str(port))
    server.start()
    print("Server started listening on port " + str(port) + ".")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
