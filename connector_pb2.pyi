import soldier_pb2 as _soldier_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Coordinate(_message.Message):
    __slots__ = ["x", "y"]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: int
    y: int
    def __init__(self, x: _Optional[int] = ..., y: _Optional[int] = ...) -> None: ...

class MissileStrike(_message.Message):
    __slots__ = ["pos", "type"]
    POS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    pos: Coordinate
    type: int
    def __init__(self, pos: _Optional[_Union[Coordinate, _Mapping]] = ..., type: _Optional[int] = ...) -> None: ...

class Hit(_message.Message):
    __slots__ = ["hits", "kills", "points"]
    HITS_FIELD_NUMBER: _ClassVar[int]
    KILLS_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    hits: int
    kills: int
    points: int
    def __init__(self, hits: _Optional[int] = ..., kills: _Optional[int] = ..., points: _Optional[int] = ...) -> None: ...

class Points(_message.Message):
    __slots__ = ["points"]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    points: int
    def __init__(self, points: _Optional[int] = ...) -> None: ...

class Timestamp(_message.Message):
    __slots__ = ["timestamp"]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    timestamp: float
    def __init__(self, timestamp: _Optional[float] = ...) -> None: ...
