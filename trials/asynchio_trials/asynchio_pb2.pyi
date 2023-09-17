from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Status(_message.Message):
    __slots__ = ["isAlive"]
    ISALIVE_FIELD_NUMBER: _ClassVar[int]
    isAlive: bool
    def __init__(self, isAlive: bool = ...) -> None: ...

class Confirmation(_message.Message):
    __slots__ = ["status_code"]
    STATUS_CODE_FIELD_NUMBER: _ClassVar[int]
    status_code: int
    def __init__(self, status_code: _Optional[int] = ...) -> None: ...

class void(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
