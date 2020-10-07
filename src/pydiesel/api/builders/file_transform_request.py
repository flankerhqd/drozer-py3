from typing import Optional

from ..protobuf_pb2 import Message


class FileTransformRequestFactory:
    def __init__(self, upload: bool, remote_filename: str, data: Optional[bytes] = None):
        self.builder = Message(type=Message.FILE_TRANSFORM_REQUEST)
        self.builder.file_transform_request.upload = upload
        self.builder.file_transform_request.remote_filename = remote_filename
        if upload:
            self.builder.file_transform_request.data = data

    def build(self):
        """
        Serialize the built Message to a String, using the Protocol Buffer
        format.
        """

        return self.builder.SerializeToString()

    def setSessionId(self, session_id):
        """
        Set session identifier, to route a message correctly on the Agent.
        """

        self.builder.file_transform_request.session_id = session_id

        return self

    def setId(self, message_id):
        """
        Set the identifier of the message.
        """

        self.builder.id = message_id

        return self
