# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: asynchio.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0e\x61synchio.proto\x12\x08\x61synchio\"*\n\x06Status\x12\x14\n\x07isAlive\x18\x01 \x01(\x08H\x00\x88\x01\x01\x42\n\n\x08_isAlive\"8\n\x0c\x43onfirmation\x12\x18\n\x0bstatus_code\x18\x01 \x01(\x05H\x00\x88\x01\x01\x42\x0e\n\x0c_status_code\"\x06\n\x04void2>\n\x05\x41lert\x12\x35\n\x07\x65ndTurn\x12\x10.asynchio.Status\x1a\x16.asynchio.Confirmation\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'asynchio_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_STATUS']._serialized_start=28
  _globals['_STATUS']._serialized_end=70
  _globals['_CONFIRMATION']._serialized_start=72
  _globals['_CONFIRMATION']._serialized_end=128
  _globals['_VOID']._serialized_start=130
  _globals['_VOID']._serialized_end=136
  _globals['_ALERT']._serialized_start=138
  _globals['_ALERT']._serialized_end=200
# @@protoc_insertion_point(module_scope)
