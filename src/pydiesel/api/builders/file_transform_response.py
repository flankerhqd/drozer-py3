from ..protobuf_pb2 import Message


class FileTransformResponseFactory:
    def __init__(self):
        self.builder = Message(type=Message.FILE_TRANSFORM_RESPONSE)
