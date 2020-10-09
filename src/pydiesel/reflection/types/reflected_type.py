import sys

from ...api.protobuf_pb2 import Message
from ..exceptions import ReflectionException

class ReflectedType(object):
    """
    A ReflectedType models a variable shared with a Java VM through reflection.

    The ReflectedType class is used to keep track of meta-data that would
    otherwise be lost in Python, such as the strong type required by Java.

    A ReflectedType is never instantiated directly, rather #fromArgument and
    #fromNative should be used to cast types provided in API messages or from
    the local system respectively. These methods will return a subclass of
    ReflectedType, which provides suitable methods to allow it to be used as
    a native object.
    """
    

    def __init__(self, reflector=None):
        self._reflector = reflector

    @classmethod
    def fromArgument(cls, argument, reflector):
        """
        Creates a new ReflectedType, given an Argument message as defined in
        the drozer protocol.
        """

        from .reflected_array import ReflectedArray
        from .reflected_binary import ReflectedBinary
        from .reflected_null import ReflectedNull
        from .reflected_object import ReflectedObject
        from .reflected_primitive import ReflectedPrimitive
        from .reflected_string import ReflectedString

        if isinstance(argument, ReflectedType):
            return argument
        elif argument.type == Message.Argument.ARRAY:
            return ReflectedArray.fromArgument(argument, reflector=reflector)
        elif argument.type == Message.Argument.DATA:
            return ReflectedBinary(argument.data, reflector=reflector)
        elif argument.type == Message.Argument.NULL:
            return ReflectedNull(reflector=reflector)
        elif argument.type == Message.Argument.OBJECT:
            return ReflectedObject(argument.object.reference, reflector=reflector)
        elif argument.type == Message.Argument.PRIMITIVE:
            return ReflectedPrimitive.fromArgument(argument, reflector)
        elif argument.type == Message.Argument.STRING:
            return ReflectedString(argument.string, reflector=reflector)
        else:
            return None

    @classmethod
    def fromNative(cls, obj, reflector, obj_type=None):
        """
        Creates a new ReflectedType, given a native variable. An optional type
        can be specified to indicate which Java data type should be used, where
        it cannot be inferred from the Python type.
        """
        from .reflected_array import ReflectedArray
        from .reflected_binary import ReflectedBinary
        from .reflected_null import ReflectedNull
        from .reflected_object import ReflectedObject
        from .reflected_primitive import ReflectedPrimitive
        from .reflected_string import ReflectedString

        if obj_type is None and isinstance(obj, ReflectedType) or obj_type == "object":
            return obj
        elif obj_type is None and isinstance(obj, int) and -sys.maxsize - 1 < obj < sys.maxsize or obj_type == "int":
            return ReflectedPrimitive("int", obj, reflector=reflector)
        elif obj_type is None and isinstance(obj, int) or obj_type == "long":
            return ReflectedPrimitive("long", obj, reflector=reflector)
        elif obj_type == "byte" and isinstance(obj, int):
            return ReflectedPrimitive("byte", obj, reflector=reflector)
        elif obj_type == "char" and isinstance(obj, int):
            return ReflectedPrimitive("char", obj, reflector=reflector)
        elif obj_type == "short":
            return ReflectedPrimitive("short", obj, reflector=reflector)
        elif obj_type is None and isinstance(obj, float) or obj_type == "float":
            return ReflectedPrimitive("float", obj, reflector=reflector)
        elif obj_type is None and isinstance(obj, bool) or obj_type == "boolean":
            return ReflectedPrimitive("boolean", obj, reflector=reflector)
        elif obj_type is None and isinstance(obj, bytes) or obj_type == "data":
            return ReflectedBinary(obj, reflector=reflector)
        elif obj_type is None and isinstance(obj, str) or obj_type == "string":
            return ReflectedString(obj, reflector=reflector)
        elif obj_type == "double":
            return ReflectedPrimitive("double", obj, reflector=reflector)
        elif obj is None:
            return ReflectedNull(reflector=reflector)
        elif hasattr(obj, '__iter__'):
            return ReflectedArray(obj, reflector=reflector)
        else:
            return None
