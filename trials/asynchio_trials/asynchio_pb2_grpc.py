# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import asynchio_pb2 as asynchio__pb2


class AlertStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.endTurn = channel.unary_unary(
                '/asynchio.Alert/endTurn',
                request_serializer=asynchio__pb2.Status.SerializeToString,
                response_deserializer=asynchio__pb2.Confirmation.FromString,
                )


class AlertServicer(object):
    """Missing associated documentation comment in .proto file."""

    def endTurn(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_AlertServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'endTurn': grpc.unary_unary_rpc_method_handler(
                    servicer.endTurn,
                    request_deserializer=asynchio__pb2.Status.FromString,
                    response_serializer=asynchio__pb2.Confirmation.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'asynchio.Alert', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Alert(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def endTurn(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/asynchio.Alert/endTurn',
            asynchio__pb2.Status.SerializeToString,
            asynchio__pb2.Confirmation.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
