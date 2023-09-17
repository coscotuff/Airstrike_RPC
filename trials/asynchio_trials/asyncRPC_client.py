from __future__ import print_function
from concurrent import futures
import asyncio
import asynchio_pb2
import asynchio_pb2_grpc
import grpc
import grpc.aio


class Server(asynchio_pb2_grpc.AlertServicer):
    async def f1(self):
        for i in range(10):
            print("f1 is running")
            await asyncio.sleep(1)  # Simulate some asynchronous work

    async def endTurn(self, request, context):
        print("f2 is running")
        await asyncio.sleep(1)  # Simulate some asynchronous work
        print("f2 is done")

        # Call f1 inside f2 and let it run concurrently
        asyncio.create_task(self.f1())

        return asynchio_pb2.Confirmation(status_code=200)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    asynchio_pb2_grpc.add_AlertServicer_to_server(Server(), server)
    server.add_insecure_port("[::]:50050")
    server.start()
    print("Server started listening on port 50050")
    server.wait_for_termination()


def main():
    # Perform an RPC to f2() in the server
    with grpc.insecure_channel("localhost:50050") as channel:
        stub = asynchio_pb2_grpc.AlertStub(channel)
        response = stub.endTurn(asynchio_pb2.Status(isAlive=True))

    # Continue with other tasks or code after f2 has finished
    print("Status of endTurn():" + str(response.status_code))


if __name__ == "__main__":
    main()
