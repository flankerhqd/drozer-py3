import base64

from ...api.protobuf_pb2 import Message
from ..exceptions import ReflectionException
from .reflected_string import ReflectedString
from .reflected_type import ReflectedType

class ReflectedBinary(ReflectedString):
    
    def __init__(self, native: bytes, *args, **kwargs):
        ReflectedType.__init__(self, *args, **kwargs)
        
        self._native = native
    
    def base64_encode(self):
        """
        Get a Base64-encoded representation of the underlying Binary data.
        """
    
        return base64.b64encode(self._native)
    
    def _pb(self):
        """
        Get the Argument representation of the String, as defined in the drozer
        protocol.
        """

        return Message.Argument(type=Message.Argument.DATA, data=self._native)