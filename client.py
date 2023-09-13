# python3 -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. test.proto

from __future__ import print_function

import logging
import grpc
import test_pb2
import test_pb2_grpc

logging.basicConfig(filename="client.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
 
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def run():
    logger.debug("ALERT, received red zone from detector. Executing commander duties...")
    logger.debug("Red zone coordinates: [0,0]; Radius: 2")
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = test_pb2_grpc.AlertStub(channel)
        response = stub.SendZone(test_pb2.RedZone(pos=test_pb2.Position(x=0, y=0), radius=2))
    logger.debug("Soldier status: " + str(response.is_alive))
    logger.debug("Soldier position: " + str(response.pos.x) + ", " + str(response.pos.y))


if __name__ == "__main__":
    logging.basicConfig()
    run()