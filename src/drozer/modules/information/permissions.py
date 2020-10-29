from drozer.modules import common, Module


class Permissions(common.PackageManager, Module):
    name = "Get a list of all permissions used by packages on the device"
    description = "Get a list of all permissions used by packages on the device as well as their descriptions and protection levels"
    examples = '''
    dz> run information.permissions --permission android.permission.INSTALL_PACKAGES
    Allows the app to install new or updated Android packages. Malicious apps may use this to add new apps with arbitrarily powerful permissions.
    18 - signature|system
    '''
    author = "LeadroyaL"
    date = "2020-10-29"
    license = "BSD (3 clause)"
    path = ["information"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    __protectionLevels = {
        'normal': 0x00,
        'dangerous': 0x01,
        'signature': 0x02,
        'system': 0x10,
        'development': 0x20,
    }

    def add_arguments(self, parser):
        parser.add_argument("--permission", help="filter by specific permission")
        parser.add_argument("--level", help="filter by protection level")

    def execute(self, arguments):
        if arguments.permission:
            perm = self.singlePermissionInfo(arguments.permission)
            if perm is not None:
                self.stdout.write(str(perm) + "\n")
            else:
                self.stdout.write("No such permission defined\n")
        else:
            if arguments.level is not None:
                if arguments.level not in self.__protectionLevels.keys():
                    self.stderr.write("protection level not in list\n")
                    self.stderr.write(f"{','.join(self.__protectionLevels.keys())}")
                    return
                level = self.__protectionLevels[arguments.level]
            else:
                level = None
            permissionList = self.getAllPermissions()
            for permission in permissionList:
                if level is None:
                    show = True
                elif level == 0 and permission.protectionLevel == 0:
                    show = True
                elif level & permission.protectionLevel != 0:
                    show = True
                else:
                    show = False
                if show:
                    self.stdout.write(str(permission) + "\n")
