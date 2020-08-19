from drozer.modules import common, Module
from pydiesel.reflection import ReflectionException


class DeviceInfo(Module, common.Shell):
    
    name = "Get verbose device information"
    description = "Gets device information"
    examples = ""
    author = "Tyrone (@mwrlabs)"
    date = "2012-11-06"
    license = "BSD (3 clause)"
    path = ["information"]

    def execute(self, arguments):
        self.stdout.write("-----------------------------------------\n")
        self.stdout.write("/proc/version\n")
        self.stdout.write("-----------------------------------------\n")
        try:
            self.stdout.write(self.readFile("/proc/version") + "\n\n")
        except ReflectionException as e:
            self.stdout.write(str(e) + "\n\n")

        self.stdout.write("-----------------------------------------\n")
        self.stdout.write("/system/build.prop\n")
        self.stdout.write("-----------------------------------------\n")
        try:
            self.stdout.write(self.readFile("/system/build.prop") + "\n\n")
        except ReflectionException as e:
            self.stdout.write(str(e) + "\n\n")

        self.stdout.write("-----------------------------------------\n")
        self.stdout.write("getprop\n")
        self.stdout.write("-----------------------------------------\n\n")
        try:
            self.stdout.write(self.shellExec("getprop") + "\n")
        except ReflectionException as e:
            self.stdout.write(str(e) + "\n\n")
