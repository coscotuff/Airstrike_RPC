from __future__ import print_function

import logging

import grpc

import connector_pb2
import connector_pb2_grpc

logging.basicConfig(filename="client.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
 
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def run():
    logger.debug("ALERT, received red zone from detector. Executing commander duties...")
    logger.debug("Red zone coordinates: [0,0]; Radius: 2")
    with grpc.insecure_channel("localhost:50050") as channel:
        stub = connector_pb2_grpc.PassAlertStub(channel)
        response = stub.SendAlert(connector_pb2.MissileStrike(pos=connector_pb2.Position(x=0, y=0), type=2))
    logger.debug("Soldier is alive: " + str(response.is_alive))
    logger.debug("Soldier hit: " + str(response.is_hit))


if __name__ == "__main__":
    while True:
        run()