import unittest

from pydiesel import reflection
from pydiesel.api.protobuf_pb2 import Message

from mwr_test.mocks.reflection import MockReflector

class ReflectedNullTestCase(unittest.TestCase):

    def setUp(self):
        pass

def ReflectedNullTestSuite():
    suite = unittest.TestSuite()

    #suite.addTest(ReflectedNullTestCase("testItShouldGetAPropertyValue"))
    
    return suite
  
if __name__ == "__main__":
    unittest.TextTestRunner().run(ReflectedNullTestSuite())
    