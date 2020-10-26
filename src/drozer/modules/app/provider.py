import os
import xml.etree.ElementTree as ET

from drozer import android
from drozer.modules import common, Module
from drozer.manifest_parser import Provider, Manifest

class Columns(common.Provider, common.TableFormatter, Module):
    name = "List columns in content provider"
    description = "List the columns in the specified content provider URI."
    examples = """List the columns of content://settings/secure

    dz> run app.provider.columns content://settings/secure
    | _id | name | value |"""
    author = "MWR InfoSecurity (@mwrlabs)"
    date = "2012-11-06"
    license = "BSD (3 clause)"
    path = ["app", "provider"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        parser.add_argument("uri", help="the content provider uri to query")

    def execute(self, arguments):
        c = self.contentResolver().query(arguments.uri)

        if c.__ne__(None):
            columns = c.getColumnNames()
            c.close()

            self.print_table([columns])
        else:
            self.stderr.write("Unable to get columns from %s\n"%arguments.uri)

class Delete(common.Provider, Module):
    name = "Delete from a content provider"
    description = "Delete from the specified content provider URI."
    examples = """Delete from content://settings/secure, with name condition:

    dz> run app.provider.delete content://settings/secure
                --selection "name=?"
                --selection-args my_setting"""
    author = "MWR InfoSecurity (@mwrlabs)"
    date = "2012-11-06"
    license = "BSD (3 clause)"
    path = ["app", "provider"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        parser.add_argument("uri", help="the content provider uri to query")
        parser.add_argument("--selection", default=None, metavar="conditions", help="the conditions to apply to the query, as in \"WHERE <conditions>\"")
        parser.add_argument("--selection-args", default=None, metavar="arg", nargs="*", help="any parameters to replace '?' in --selection")
    
    def execute(self, arguments):
        self.contentResolver().delete(arguments.uri, arguments.selection, arguments.selection_args)

        self.stdout.write("Done.\n\n")


class Download(common.Provider, Module):
    name = "Download a file from a content provider that supports files"
    description = "Read from the specified content uri using openInputStream, and download to the local file system"
    examples = """Download, using directory traversal on a content provider:

    dz> run app.provider.download content://vulnerable.provider/../../../system/etc/hosts /tmp/hostsfile
    Written 25 bytes"""
    author = "MWR InfoSecurity (@mwrlabs)"
    date = "2012-11-06"
    license = "BSD (3 clause)"
    path = ["app", "provider"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        parser.add_argument("uri", help="the content provider URI to read a file through")
        parser.add_argument("destination", help="path to save the downloaded file to")

    def execute(self, arguments):
        data = self.contentResolver().read(arguments.uri)
        
        if os.path.isdir(arguments.destination):
            arguments.destination = os.path.sep.join([arguments.destination, arguments.uri.split("/")[-1]])
        
        output = open(arguments.destination, 'w')
        output.write(str(data))
        output.close()

        self.stdout.write("Written %d bytes\n\n" % len(data))

    def get_completion_suggestions(self, action, text, **kwargs):
        if action.dest == "destination":
            return common.path_completion.on_console(text)


class FindUri(common.FileSystem, common.PackageManager, common.Provider, common.Strings, common.ZipFile, Module):
    name = "Find referenced content URIs in a package"
    description = """Finds Content URIs within a package.
    
This module uses a number of strategies to identify a content URI, including inspecting the authorities, path permissions and searching for strings inside the package."""
    examples = """Find content provider URIs in the Browser:

    dz> run app.provider.finduri com.android.browser
    Scanning com.android.browser...
    content://com.android.browser.home/res/raw/
    content://browser/search_suggest_query
    content://browser/
    content://com.android.browser.snapshots/
    content://com.android.browser/bookmarks/search_suggest_query
    content://com.android.browser/
    content://com.google.settings/partner
    content://com.android.browser.snapshots
    content://com.google.android.partnersetup.rlzappprovider/
    content://com.android.browser.home/
    content://browser/bookmarks/search_suggest_query"""
    author = "MWR InfoSecurity (@mwrlabs)"
    date = "2012-13-18"
    license = "BSD (3 clause)"
    path = ["app", "provider"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        parser.add_argument("package", help="the package to search for content provider uris")

    def execute(self, arguments):
        uris = self.findAllContentUris(arguments.package)
        
        if len(uris) > 0:
            for uri in uris:
                self.stdout.write("%s\n" % uri[uri.upper().find("CONTENT"):])
        else:
            self.stdout.write("No Content URIs found.\n")


class Info(common.Assets, common.PackageManager, Module):
    name = "Get information about exported content providers"
    description = "List information about exported content providers, with optional filters."
    examples = """Find content provider with the keyword "settings" in them:

    dz> run app.provider.info -f settings

    Package name: com.google.android.gsf
    Authority: com.google.settings
    Required Permission - Read: null
    Required Permission - Write: com.google.android.providers.settings.permission.WRITE_GSETTINGS
    Grant Uri Permissions: false
    Multiprocess allowed: false

    Package name: com.android.providers.settings
    Authority: settings
    Required Permission - Read: null
    Required Permission - Write: android.permission.WRITE_SETTINGS
    Grant Uri Permissions: false
    Multiprocess allowed: false

Finding content providers that do not require permissions to read/write:

    dz> run app.provider.info -p null

    Package name: com.google.android.gsf
    Authority: com.google.settings
    Required Permission - Read: null
    Required Permission - Write: com.google.android.providers.settings.permission.WRITE_GSETTINGS
    Grant Uri Permissions: false
    Multiprocess allowed: false

    ..."""
    author = "MWR InfoSecurity (@mwrlabs)"
    date = "2012-11-06"
    license = "BSD (3 clause)"
    path = ["app", "provider"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    PatternMatcherTypes = { 0: "PATTERN_LITERAL", 1: "PATTERN_PREFIX", 2: "PATTERN_SIMPLE_GLOB" }

    def add_arguments(self, parser):
        parser.add_argument("-a", "--package", default=None, help="specify the package to inspect")
        parser.add_argument("-f", "--filter", default=None, help="specify filter conditions")
        parser.add_argument("-p", "--permission", default=None, help="specify permission conditions")
        parser.add_argument("-u", "--unexported", action="store_true", default=False, help="include providers that are not exported")
        parser.add_argument("-v", "--verbose", action="store_true", default=False, help="be verbose")

    def execute(self, arguments):
        if arguments.package is None:
            for j_package in self.packageManager().getPackages():
                package = str(j_package.packageName)
                try:
                    m = Manifest(self.getAndroidManifest(package), False, has_provider=True)
                    self.__get_providers(arguments, m)
                except ET.ParseError as e:
                    self.stderr.write("%s cannot parse manifest. %s" % (package, e))
        else:
            package = arguments.package
            try:
                m = Manifest(self.getAndroidManifest(package), False, has_provider=True)
                self.__get_providers(arguments, m)
            except ET.ParseError as e:
                self.stderr.write("%s cannot parse manifest. %s" % (package, e))

    def get_completion_suggestions(self, action, text, **kwargs):
        if action.dest == "permission":
            return ["null"] + android.permissions

    def __get_providers(self, arguments, manifest: Manifest):
        providers = manifest.application.providers
        if arguments.filter:
            providers = filter(lambda _r:
                               arguments.filter.lower() in _r.authority.lower(),
                               providers)

        if arguments.permission:
            providers = filter(lambda _r:
                               _r.readPermission is not None and arguments.permission.lower() in _r.readPermission.lower()
                               or _r.writePermission is not None and arguments.permission.lower() in _r.writePermission.lower(),
                               providers)

        exported_providers = []
        hidden_providers = []
        for e in providers:
            if e.is_exported():
                exported_providers.append(e)
            else:
                hidden_providers.append(e)

        self.stdout.write("Package: %s\n" % manifest.package)
        if len(exported_providers) > 0 or arguments.unexported and len(hidden_providers) > 0:
            if not arguments.unexported:
                for provider in exported_providers:
                    if provider.authorities is None or provider.authorities == "":
                        self.stdout.write("provider.authorities NULL\n")
                        continue
                    for authority in provider.authorities.split(";"):
                        self.__print_provider(provider, authority, "  ")
            else:
                self.stdout.write("  Exported Providers:\n")
                for provider in exported_providers:
                    if provider.authorities is None or provider.authorities == "":
                        self.stdout.write("provider.authorities NULL\n")
                        continue
                    for authority in provider.authorities.split(";"):
                        self.__print_provider(provider, authority, "  ")
                self.stdout.write("  Hidden Providers:\n")
                for provider in hidden_providers:
                    if provider.authorities is None or provider.authorities == "":
                        self.stdout.write("provider.authorities NULL\n")
                        continue
                    for authority in provider.authorities.split(";"):
                        self.__print_provider(provider, authority, "  ")
            self.stdout.write("\n")
        else:
            self.stdout.write("  No matching providers.\n\n")

    def __print_provider(self, provider: Provider, authority: str, prefix):
        self.stdout.write("%sAuthority: %s\n" % (prefix, authority))
        permissionInfo = self.singlePermissionInfo(str(provider.readPermission))
        if permissionInfo is None:
            self.stdout.write("%s  Read Permission: %s [Non-existent]\n" % (prefix, permissionInfo))
        else:
            self.stdout.write("%s  Read Permission: %s\n" % (prefix, permissionInfo))
        permissionInfo = self.singlePermissionInfo(str(provider.writePermission))
        if permissionInfo is None:
            self.stdout.write("%s  Write Permission: %s [Non-existent]\n" % (prefix, permissionInfo))
        else:
            self.stdout.write("%s  Write Permission: %s\n" % (prefix, permissionInfo))
        self.stdout.write("%s  Content Provider: %s\n" % (prefix, provider.name))
        self.stdout.write("%s  Multiprocess Allowed: %s\n" % (prefix, provider.multiprocess))
        self.stdout.write("%s  Grant Uri Permissions: %s\n" % (prefix, provider.grantUriPermissions))
        if len(provider.grant_uri_permissions) > 0:
            self.stdout.write("%s  Uri Permission Patterns:\n" % prefix)
            for grant_uri_permission in provider.grant_uri_permissions:
                if grant_uri_permission.path is not None:
                    self.stdout.write("%s    Path: %s\n" % (prefix, grant_uri_permission.path))
                    self.stdout.write("%s      Type: %s\n" % (prefix, Info.PatternMatcherTypes[0]))
                elif grant_uri_permission.pathPrefix is not None:
                    self.stdout.write("%s    Path: %s\n" % (prefix, grant_uri_permission.pathPrefix))
                    self.stdout.write("%s      Type: %s\n" % (prefix, Info.PatternMatcherTypes[0]))
                elif grant_uri_permission.pathPattern is not None:
                    self.stdout.write("%s    Path: %s\n" % (prefix, grant_uri_permission.pathPattern))
                    self.stdout.write("%s      Type: %s\n" % (prefix, Info.PatternMatcherTypes[0]))
        if len(provider.path_permissions) > 0:
            self.stdout.write("%s  Path Permissions:\n" % prefix)
            for pathPermission in provider.path_permissions:
                if pathPermission.path is not None:
                    self.stdout.write("%s    Path: %s\n" % (prefix, pathPermission.path))
                    self.stdout.write("%s      Type: %s\n" % (prefix, Info.PatternMatcherTypes[0]))
                elif pathPermission.pathPrefix is not None:
                    self.stdout.write("%s    Path: %s\n" % (prefix, pathPermission.pathPrefix))
                    self.stdout.write("%s      Type: %s\n" % (prefix, Info.PatternMatcherTypes[0]))
                elif pathPermission.pathPattern is not None:
                    self.stdout.write("%s    Path: %s\n" % (prefix, pathPermission.pathPattern))
                    self.stdout.write("%s      Type: %s\n" % (prefix, Info.PatternMatcherTypes[0]))
                self.stdout.write("%s      Read Permission: %s\n" % (prefix, pathPermission.readPermission))
                self.stdout.write("%s      Write Permission: %s\n" % (prefix, pathPermission.writePermission))


class Insert(common.Provider, Module):

    name = "Insert into a Content Provider"
    description = "Insert into a content provider."
    examples = """Insert into a vulnerable content provider:

    dz> run app.provider.insert content://com.vulnerable.im/messages
                --string date 1331763850325
                --string type 0
                --integer _id 7"""
    author = "MWR InfoSecurity (@mwrlabs)"
    date = "2012-11-06"
    license = "BSD (3 clause)"
    path = ["app", "provider"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        parser.add_argument("uri", help="the content provider uri to insert into")
        parser.add_argument('--boolean', action="append", nargs=2, metavar=('column', 'data'))
        parser.add_argument('--double', action="append", nargs=2, metavar=('column', 'data'))
        parser.add_argument('--float', action="append", nargs=2, metavar=('column', 'data'))
        parser.add_argument('--integer', action="append", nargs=2, metavar=('column', 'data'))
        parser.add_argument('--long', action="append", nargs=2, metavar=('column', 'data'))
        parser.add_argument('--short', action="append", nargs=2, metavar=('column', 'data'))
        parser.add_argument('--string', action="append", nargs=2, metavar=('column', 'data'))
    
    def execute(self, arguments):
        values = self.new("android.content.ContentValues")

        if arguments.boolean is not None:
            for b in arguments.boolean:
                values.put(b[0], self.arg(b[1].upper().startswith("T"), obj_type="boolean"))
        if arguments.double is not None:
            for d in arguments.double:
                values.put(d[0], self.arg(d[1], obj_type="double"))
        if arguments.float is not None:
            for f in arguments.float:
                values.put(f[0], self.arg(f[1], obj_type="float"))
        if arguments.integer is not None:
            for i in arguments.integer:
                values.put(i[0], self.arg(int(i[1]), obj_type="int"))
        if arguments.long is not None:
            for l in arguments.long:
                values.put(l[0], self.arg(l[1], obj_type="long"))
        if arguments.short is not None:
            for s in arguments.short:
                values.put(s[0], self.arg(s[1], obj_type="short"))
        if arguments.string is not None:
            for s in arguments.string:
                values.put(s[0], self.arg(s[1], obj_type="string"))

        self.contentResolver().insert(arguments.uri, values);

        self.stdout.write("Done.\n\n")
        
class Query(common.Provider, common.TableFormatter, Module):

    name = "Query a content provider"
    description = "Query a content provider"
    examples = """Querying the settings content provider:

    dz> run app.provider.query content://settings/secure

    | _id | name                                    | value   |
    | 5   | assisted_gps_enabled                    | 1       |
    | 9   | wifi_networks_available_notification_on | 1       |
    | 10  | sys_storage_full_threshold_bytes        | 2097152 |
    | ... | ...                                     | ...     |

Querying, with a WHERE clause in the SELECT statement:

    dz> run app.provider.query content://settings/secure
                --selection "_id=?"
                --selection-args 10
    
    | _id | name                                    | value   |
    | 10  | sys_storage_full_threshold_bytes        | 2097152 |"""
    author = "MWR InfoSecurity (@mwrlabs)"
    date = "2012-11-06"
    license = "BSD (3 clause)"
    path = ["app", "provider"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        parser.add_argument("uri", help="the content provider uri to query")
        parser.add_argument("--projection", default=None, metavar="columns", nargs="*", help="the columns to SELECT from the database, as in \"SELECT <projection> FROM ...\"")
        parser.add_argument("--selection", default=None, metavar="conditions", help="the conditions to apply to the query, as in \"WHERE <conditions>\"")
        parser.add_argument("--selection-args", default=None, metavar="arg", nargs="*", help="any parameters to replace '?' in --selection")
        parser.add_argument("--order", default=None, metavar="by_column", help="the column to order results by")
        parser.add_argument("--vertical", action="store_true", default=False)

    def execute(self, arguments):
        c = self.contentResolver().query(arguments.uri, arguments.projection, arguments.selection, arguments.selection_args, arguments.order)

        if c.__ne__(None):
            rows = self.getResultSet(c)

            self.print_table(rows, show_headers=True, vertical=arguments.vertical)
        else:
            self.stdout.write("Unknown Error.\n\n")

class Read(common.Provider, Module):

    name = "Read from a content provider that supports files"
    description = "Read from the specified content uri using openInputStream"
    examples = """Attempt directory traversal on a content provider:

    dz> run app.provider.read content://settings/secure/../../../system/etc/hosts
    java.io.FileNotFoundException: No files supported by provider at content://settings/secure/../../../system/etc/hosts"""
    author = "MWR InfoSecurity (@mwrlabs)"
    date = "2012-11-06"
    license = "BSD (3 clause)"
    path = ["app", "provider"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        parser.add_argument("uri", help="the content provider URI to read a file through")

    def execute(self, arguments):
        self.stdout.write(self.contentResolver().read(arguments.uri) + "\n")
        
class Update(common.Provider, Module):

    name = "Update a record in a content provider"
    description = "Update the specified content provider URI"
    examples = """Updating, the assisted_gps_enabled setting:

    dz> run app.provider.update content://settings/secure
                --selection "name=?"
                --selection-args assisted_gps_enabled
                --integer value 0
    Done."""
    author = "MWR InfoSecurity (@mwrlabs)"
    date = "2012-11-06"
    license = "BSD (3 clause)"
    path = ["app", "provider"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        parser.add_argument("uri", help="the content provider uri to update in")
        parser.add_argument("--selection", default=None, metavar="conditions", help="the conditions to apply to the query, as in \"WHERE <conditions>\"")
        parser.add_argument("--selection-args", default=None, metavar="arg", nargs="*", help="any parameters to replace '?' in --selection")
        parser.add_argument('--boolean', action="append", nargs=2, metavar=('column', 'data'))
        parser.add_argument('--double', action="append", nargs=2, metavar=('column', 'data'))
        parser.add_argument('--float', action="append", nargs=2, metavar=('column', 'data'))
        parser.add_argument('--integer', action="append", nargs=2, metavar=('column', 'data'))
        parser.add_argument('--long', action="append", nargs=2, metavar=('column', 'data'))
        parser.add_argument('--short', action="append", nargs=2, metavar=('column', 'data'))
        parser.add_argument('--string', action="append", nargs=2, metavar=('column', 'data'))
    
    def execute(self, arguments):
        values = self.new("android.content.ContentValues")

        if arguments.boolean is not None:
            for b in arguments.boolean:
                values.put(b[0], self.arg(b[1].upper().startswith("T"), obj_type="boolean"))
        if arguments.double is not None:
            for d in arguments.double:
                values.put(d[0], self.arg(d[1], obj_type="double"))
        if arguments.float is not None:
            for f in arguments.float:
                values.put(f[0], self.arg(f[1], obj_type="float"))
        if arguments.integer is not None:
            for i in arguments.integer:
                values.put(i[0], self.arg(i[1], obj_type="integer"))
        if arguments.long is not None:
            for l in arguments.long:
                values.put(l[0], self.arg(l[1], obj_type="long"))
        if arguments.short is not None:
            for s in arguments.short:
                values.put(s[0], self.arg(s[1], obj_type="short"))
        if arguments.string is not None:
            for s in arguments.string:
                values.put(s[0], self.arg(s[1], obj_type="string"))

        self.contentResolver().update(arguments.uri, values, arguments.selection, arguments.selection_args)

        self.stdout.write("Done.\n\n")
