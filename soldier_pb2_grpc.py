# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import soldier_pb2 as soldier__pb2


class AlertStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendZone = channel.unary_unary(
                '/soldier.Alert/SendZone',
                request_serializer=soldier__pb2.RedZone.SerializeToString,
                response_deserializer=soldier__pb2.AttackStatus.FromString,
                )
        self.UpdateStatus = channel.unary_unary(
                '/soldier.Alert/UpdateStatus',
                request_serializer=soldier__pb2.RedZone.SerializeToString,
                response_deserializer=soldier__pb2.SoldierStatus.FromString,
                )
        self.PromoteSoldier = channel.unary_unary(
                '/soldier.Alert/PromoteSoldier',
                request_serializer=soldier__pb2.Battalion.SerializeToString,
                response_deserializer=soldier__pb2.void.FromString,
                )


class AlertServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendZone(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateStatus(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def PromoteSoldier(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_AlertServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendZone': grpc.unary_unary_rpc_method_handler(
                    servicer.SendZone,
                    request_deserializer=soldier__pb2.RedZone.FromString,
                    response_serializer=soldier__pb2.AttackStatus.SerializeToString,
            ),
            'UpdateStatus': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateStatus,
                    request_deserializer=soldier__pb2.RedZone.FromString,
                    response_serializer=soldier__pb2.SoldierStatus.SerializeToString,
            ),
            'PromoteSoldier': grpc.unary_unary_rpc_method_handler(
                    servicer.PromoteSoldier,
                    request_deserializer=soldier__pb2.Battalion.FromString,
                    response_serializer=soldier__pb2.void.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'soldier.Alert', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Alert(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendZone(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/soldier.Alert/SendZone',
            soldier__pb2.RedZone.SerializeToString,
            soldier__pb2.AttackStatus.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateStatus(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/soldier.Alert/UpdateStatus',
            soldier__pb2.RedZone.SerializeToString,
            soldier__pb2.SoldierStatus.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def PromoteSoldier(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/soldier.Alert/PromoteSoldier',
            soldier__pb2.Battalion.SerializeToString,
            soldier__pb2.void.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)