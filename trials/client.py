from __future__ import print_function

import logging
import random

import connector_pb2
import connector_pb2_grpc
import grpc

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
        response = stub.SendAlert(connector_pb2.MissileStrike(pos=connector_pb2.Coordinate(x=6, y=9), type=3))



if __name__ == "__main__":
    run()