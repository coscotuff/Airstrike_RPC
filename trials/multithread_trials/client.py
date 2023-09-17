import grpc
import multi_pb2
import multi_pb2_grpc


def run():
    channel = grpc.insecure_channel("localhost:50050")
    stub = multi_pb2_grpc.GameServiceStub(channel)
    response = stub.endTurn(multi_pb2.EndTurnRequest())
    print("Response from server:", response.result)


if __name__ == "__main__":
    run()
