from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Position(_message.Message):
    __slots__ = ["x", "y"]
    X_FIELD_NUMBER: _ClassVar[int]
    Y_FIELD_NUMBER: _ClassVar[int]
    x: int
    y: int
    def __init__(self, x: _Optional[int] = ..., y: _Optional[int] = ...) -> None: ...

class RedZone(_message.Message):
    __slots__ = ["pos", "radius"]
    POS_FIELD_NUMBER: _ClassVar[int]
    RADIUS_FIELD_NUMBER: _ClassVar[int]
    pos: Position
    radius: int
    def __init__(self, pos: _Optional[_Union[Position, _Mapping]] = ..., radius: _Optional[int] = ...) -> None: ...

class SoldierStatus(_message.Message):
    __slots__ = ["is_alive", "pos"]
    IS_ALIVE_FIELD_NUMBER: _ClassVar[int]
    POS_FIELD_NUMBER: _ClassVar[int]
    is_alive: bool
    pos: Position
    def __init__(self, is_alive: bool = ..., pos: _Optional[_Union[Position, _Mapping]] = ...) -> None: ...
