from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

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

class AttackStatus(_message.Message):
    __slots__ = ["death_count", "hit_count", "points", "current_commander"]
    DEATH_COUNT_FIELD_NUMBER: _ClassVar[int]
    HIT_COUNT_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    CURRENT_COMMANDER_FIELD_NUMBER: _ClassVar[int]
    death_count: int
    hit_count: int
    points: int
    current_commander: int
    def __init__(self, death_count: _Optional[int] = ..., hit_count: _Optional[int] = ..., points: _Optional[int] = ..., current_commander: _Optional[int] = ...) -> None: ...

class SoldierStatus(_message.Message):
    __slots__ = ["is_hit", "is_sink", "points"]
    IS_HIT_FIELD_NUMBER: _ClassVar[int]
    IS_SINK_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    is_hit: bool
    is_sink: bool
    points: int
    def __init__(self, is_hit: bool = ..., is_sink: bool = ..., points: _Optional[int] = ...) -> None: ...

class Battalion(_message.Message):
    __slots__ = ["soldier_ids"]
    SOLDIER_IDS_FIELD_NUMBER: _ClassVar[int]
    soldier_ids: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, soldier_ids: _Optional[_Iterable[int]] = ...) -> None: ...

class void(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
