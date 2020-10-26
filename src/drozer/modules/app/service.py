import xml.etree.ElementTree as ET

from drozer import android
from drozer.modules import common, Module
from drozer.manifest_parser import Service, Manifest


class Info(common.Filters, common.IntentFilter, common.PackageManager, Module):
    name = "Get information about exported services"
    description = "Gets information about exported services."
    examples = """List services exported by the Browser:

    dz> run app.service.info --package com.android.browser
    Package: com.android.browser
      No exported services.

List exported services with no permissions required to interact with it:

    dz> run app.service.info -p null
    Package: com.android.email
      com.android.email.service.EmailBroadcastProcessorService
        Permission: null
      com.android.email.Controller$ControllerService
        Permission: null
      com.android.email.service.PopImapAuthenticatorService
        Permission: null
      com.android.email.service.PopImapSyncAdapterService
        Permission: null
      com.android.email.service.EasAuthenticatorService
        Permission: null"""
    author = "MWR InfoSecurity (@mwrlabs)"
    date = "2012-11-06"
    license = "BSD (3 clause)"
    path = ["app", "service"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        parser.add_argument("-a", "--package", default=None, help="specify the package to inspect")
        parser.add_argument("-f", "--filter", metavar='<filter>')
        parser.add_argument("-i", "--show-intent-filters", action="store_true", default=False, help="specify whether to include intent filters")
        parser.add_argument("-p", "--permission", metavar='<filter>')
        parser.add_argument("-u", "--unexported", action="store_true", default=False, help="include receivers that are not exported")
        parser.add_argument("-v", action="store_true", dest="verbose", default=False)

    def execute(self, arguments):
        if arguments.package is None:
            for j_package in self.packageManager().getPackages():
                package = str(j_package.packageName)
                try:
                    m = Manifest(self.getAndroidManifest(package), False, has_service=True)
                    self.__get_services(arguments, m)
                except ET.ParseError as e:
                    self.stderr.write("%s cannot parse manifest. %s" % (package, e))
        else:
            package = arguments.package
            try:
                m = Manifest(self.getAndroidManifest(package), False, has_service=True)
                self.__get_services(arguments, m)
            except ET.ParseError as e:
                self.stderr.write("%s cannot parse manifest. %s" % (package, e))

    def get_completion_suggestions(self, action, text, **kwargs):
        if action.dest == "permission":
            return ["null"] + android.permissions

    def __get_services(self, arguments, manifest: Manifest):
        services = manifest.application.services
        if arguments.filter:
            services = filter(lambda _r:
                              arguments.filter.lower() in _r.name.lower(),
                              services)
        if arguments.permission:
            services = filter(lambda _r:
                              _r.permission is not None
                              and arguments.permission.lower() in _r.permission.lower(),
                              services)
        exported_services = []
        hidden_services = []
        for e in services:
            if e.is_exported():
                exported_services.append(e)
            else:
                hidden_services.append(e)

        self.stdout.write("Package: %s\n" % manifest.package)
        if len(exported_services) > 0 or arguments.unexported and len(services) > 0:
            if not arguments.unexported:
                for service in exported_services:
                    self.__print_service(None, service, "  ", arguments.show_intent_filters)
            else:
                self.stdout.write("  Exported Services:\n")
                for service in exported_services:
                    self.__print_service(None, service, "    ", arguments.show_intent_filters)
                self.stdout.write("  Hidden Services:\n")
                for service in hidden_services:
                    self.__print_service(None, service, "    ", arguments.show_intent_filters)
            self.stdout.write("\n")
        else:
            self.stdout.write("  No exported services.\n\n")

    def __print_service(self, package, service: Service, prefix, include_intent_filters=False):
        self.stdout.write("%s%s\n" % (prefix, service.name))

        if include_intent_filters:
            for intent_filter in service.intent_filters:
                self.stdout.write("%s  Intent Filter:\n" % (prefix))
                if len(intent_filter.actions) > 0:
                    self.stdout.write("%s    Actions:\n" % (prefix))
                    for action in intent_filter.actions:
                        self.stdout.write("%s      - %s\n" % (prefix, action))
                if len(intent_filter.categories) > 0:
                    self.stdout.write("%s    Categories:\n" % (prefix))
                    for category in intent_filter.categories:
                        self.stdout.write("%s      - %s\n" % (prefix, category))
                if len(intent_filter.datas) > 0:
                    self.stdout.write("%s    Data:\n" % (prefix))
                    for data in intent_filter.datas:
                        self.stdout.write("%s      - %s\n" % (prefix, data))
        permissionInfo = self.singlePermissionInfo(str(service.permission))
        if permissionInfo is None:
            self.stdout.write("%s  Permission: %s [Non-existent]\n" % (prefix, service.permission))
        else:
            self.stdout.write("%s    %s\n" % (prefix, permissionInfo))


class Send(common.ServiceBinding, Module):
    name = "Send a Message to a service, and display the reply"
    description = """Binds to an exported service, and sends a Message to it. If the service sends a reply, display the message received and any data it contains.

NB: by default, this module will wait 20 seconds for a reply."""
    examples = """Deliver a Message to a dummy application, that simply returns the message:
    
    dz> run app.service.send com.example.srv com.example.srv.Service --msg 1 2 3 --extra float value 0.1324 --extra string test value
    Got a reply from com.example.srv/com.example.srv.Service:
      what: 1
      arg1: 2
      arg2: 3
    Data: 
      value (float) : 0.1324
      test (string) : value
    """
    author = "MWR InfoSecurity (@mwrlabs)"
    date = "2013-05-20"
    license = "BSD (3 clause)"
    path = ["app", "service"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]
    
    def add_arguments(self, parser):
        parser.add_argument("package", help="the package containing the target service")
        parser.add_argument("component", help="the fully-qualified service name to bind to")
        parser.add_argument("--msg", nargs=3, metavar=("what", "arg1", "arg2"), help="specify the what, arg1 and arg2 values to use when obtaining the message")
        parser.add_argument("--extra", action="append", nargs=3, metavar=("type","key","value"), help="add an extra to the message's data bundle")
        parser.add_argument("--no-response", action="store_true", default=False, help="do not wait for a response from the service")
        parser.add_argument("--timeout", default="20000", help="specify a timeout in milliseconds (default is 20000)")
        parser.add_argument("--bundle-as-obj", action="store_true", default=False, help="this is useful when the 'obj' parameter on the target is being cast back to a Bundle instead of using Message.getData()")

    def execute(self, arguments):
        if arguments.msg is None:
            self.stderr.write("please specify --msg as \"what arg1 arg2\"\n")
            
            return
        
        binder = self.getBinding(arguments.package, arguments.component)
    
        if arguments.extra is not None:
            for extra in arguments.extra:
                binder.add_extra(extra)

            if arguments.bundle_as_obj:
                binder.setObjFormat("bundleAsObj")
                
        if arguments.no_response:
            binder.send_message(arguments.msg, -1)
            
            self.stdout.write("Sent message, did not wait for a reply from %s/%s.\n" % (arguments.package, arguments.component))
        else:
            result = binder.send_message(arguments.msg, arguments.timeout)
            
            if result:
                response_message = binder.getMessage();
                response_bundle = binder.getData();

                self.stdout.write("Got a reply from %s/%s:\n" % (arguments.package, arguments.component))
                self.stdout.write("  what: %d\n" % int(response_message.what))
                self.stdout.write("  arg1: %d\n" % int(response_message.arg1))
                self.stdout.write("  arg2: %d\n" % int(response_message.arg2))

                for n in response_bundle.split('\n'):
                    self.stdout.write("  %s\n"%n)
            else:
                self.stdout.write("Did not receive a reply from %s/%s.\n" % (arguments.package, arguments.component))


class Start(Module):
    name = "Start Service"
    description = """Formulate an Intent to start a service, and deliver it to another application.

For more information on how to formulate an Intent, type 'help intents'."""
    examples = ""
    author = "MWR InfoSecurity (@mwrlabs)"
    date = "2012-11-06"
    license = "BSD (3 clause)"
    path = ["app", "service"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        android.Intent.addArgumentsTo(parser)

    def execute(self, arguments):
        intent = android.Intent.fromParser(arguments)
        
        if intent.isValid():        
            self.getContext().startService(intent.buildIn(self))
        else:
            self.stderr.write("invalid intent: one of action or component must be set\n")
    
    def get_completion_suggestions(self, action, text, **kwargs):
        if action.dest in ["action", "category", "component", "data_uri",
                           "extras", "flags", "mimetype"]:
            return android.Intent.get_completion_suggestions(action, text, **kwargs)

class Stop(Module):

    name = "Stop Service"
    description = "Formulate an Intent to stop a service, and deliver it to another application."
    examples = ""
    author = "MWR InfoSecurity (@mwrlabs)"
    date = "2012-11-06"
    license = "BSD (3 clause)"
    path = ["app", "service"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        android.Intent.addArgumentsTo(parser)

    def execute(self, arguments):
        intent = android.Intent.fromParser(arguments)
        
        if intent.isValid():        
            self.getContext().stopService(intent.buildIn(self))
        else:
            self.stderr.write("invalid intent: one of action or component must be set\n")
    
    def get_completion_suggestions(self, action, text, **kwargs):
        if action.dest in ["action", "category", "component", "data_uri",
                           "extras", "flags", "mimetype"]:
            return android.Intent.get_completion_suggestions(action, text, **kwargs)
