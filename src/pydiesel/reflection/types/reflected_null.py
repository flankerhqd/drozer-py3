from ...api.protobuf_pb2 import Message
from ..exceptions import ReflectionException
from .reflected_type import ReflectedType

class ReflectedNull(ReflectedType):
    """
    A ReflectedType that represents Java null.
    """

    def _pb(self):
        """
        Get an Argument representation of the null, as defined in the drozer
        protocol.
        """
        return Message.Argument(type=Message.Argument.NULL)

    def __eq__(self, other):
        if other is None:
            return True
        else:
            return ReflectedType.__eq__(self, other)

    def __ne__(self, other):
        if other is None:
            return False
        else:
            return ReflectedType.__ne__(self, other)

    def __str__(self):
        return "null"

    def __format__(self, format_spec):
        return "null"
