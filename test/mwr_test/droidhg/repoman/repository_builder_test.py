import configparser
import os
import shutil
import unittest

from mwr.common import fs

from drozer.configuration import Configuration
from drozer.repoman.installer import ModuleInstaller
from drozer.repoman.repositories import Repository
from drozer.repoman.repository_builder import RepositoryBuilder

class RepositoryBuilderTestCase(unittest.TestCase):
    
    def setUp(self):
        Configuration._Configuration__config = configparser.SafeConfigParser()
        
        shutil.rmtree("./tmp", True)
        shutil.rmtree("./repo", True)
        
        Repository.create("./tmp")
        fs.write("./tmp/a.local.module", "This is a local, raw module.")
        ModuleInstaller("./tmp").install(["./tmp/a.local.module"])
    
    def tearDown(self):
        shutil.rmtree("./tmp", True)
        shutil.rmtree("./repo", True)
    
    def testItShouldBuildAModuleRepository(self):
        RepositoryBuilder("./tmp", "./repo").build()
        
        assert os.path.exists("./repo")
        assert os.path.exists("./repo/INDEX.xml")
        assert os.path.exists("./repo/a.local.module")
        
        assert b"a.local.module" in fs.read("./repo/INDEX.xml")
    
    def testItShouldBuildAModuleRepositoryWithPackage(self):
        fs.touch("./tmp/a/local/.drozer_package")
        
        RepositoryBuilder("./tmp", "./repo").build()
        
        assert os.path.exists("./repo")
        assert os.path.exists("./repo/INDEX.xml")
        assert os.path.exists("./repo/a.local")
        
        assert b"a.local" in fs.read("./repo/INDEX.xml")
        assert fs.read("./repo/a.local")[0:4] == b"\x50\x4b\x03\x04"

    
def RepositoryBuilderTestSuite():
    suite = unittest.TestSuite()

    suite.addTest(RepositoryBuilderTestCase("testItShouldBuildAModuleRepository"))
    suite.addTest(RepositoryBuilderTestCase("testItShouldBuildAModuleRepositoryWithPackage"))

    return suite
  
if __name__ == "__main__":
    unittest.TextTestRunner().run(RepositoryBuilderTestSuite())
    