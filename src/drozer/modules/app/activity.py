import xml.etree.ElementTree as ET

from drozer import android
from drozer.modules import common, Module
from drozer.manifest_parser import Activity, Manifest


class ForIntent(common.PackageManager, common.ClassLoader, Module):

    name = "Find activities that can handle the given intent"
    description = "Find activities that can handle the formulated intent"
    examples = """Find activities that can handle web addresses:

    dz> run app.activity.forintent
                --action android.intent.action.VIEW
                --data http://www.google.com

    Package name: com.android.browser
    Target activity: com.android.browser.BrowserActivity"""
    author = "MWR InfoSecurity (@mwrlabs)"
    date = "2012-11-06"
    license = "BSD (3 clause)"
    path = ["app", "activity"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        android.Intent.addArgumentsTo(parser)

    def execute(self, arguments):
        intent = android.Intent.fromParser(arguments)

        if intent.isValid():
            for activity in self.packageManager().queryIntentActivities(intent, common.PackageManager.MATCH_DEFAULT_ONLY | common.PackageManager.GET_ACTIVITIES | common.PackageManager.GET_INTENT_FILTERS | common.PackageManager.GET_RESOLVED_FILTER):
                activity_info = activity.activityInfo

                self.stdout.write("Package: %s\n" % activity_info.packageName)
                self.stdout.write("  %s\n\n" % activity_info.name)
        else:
            self.stderr.write("invalid intent: one of action or component must be set\n")
    
    def get_completion_suggestions(self, action, text, **kwargs):
        if action.dest in ["action", "category", "component", "data_uri",
                           "extras", "flags", "mimetype"]:
            return android.Intent.get_completion_suggestions(action, text, **kwargs)


class Info(common.IntentFilter, common.PackageManager, common.Assets, common.ClassLoader, Module):
    
    name = "Gets information about exported activities."
    description = "Gets information about exported activities."
    examples = """List activities exported by the Browser:

    dz> run app.activity.info --package com.android.browser
    Package: com.android.browser
      com.android.browser.BrowserActivity
      com.android.browser.ShortcutActivity
      com.android.browser.BrowserPreferencesPage
      com.android.browser.BookmarkSearch
      com.android.browser.AddBookmarkPage
      com.android.browser.widget.BookmarkWidgetConfigure"""
    author = "MWR InfoSecurity (@mwrlabs)"
    date = "2012-11-06"
    license = "BSD (3 clause)"
    path = ["app", "activity"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        parser.add_argument("-a", "--package", default=None, help="specify the package to inspect")
        parser.add_argument("-f", "--filter", default=None, help="specify a filter term for the activity name")
        parser.add_argument("-i", "--show-intent-filters", action="store_true", default=False, help="specify whether to include intent filters")
        parser.add_argument("-u", "--unexported", action="store_true", default=False, help="include activities that are not exported")
        parser.add_argument("-v", "--verbose", action="store_true", default=False, help="be verbose")

    def execute(self, arguments):
        if arguments.package is None:
            for j_package in self.packageManager().getPackages():
                package = str(j_package.packageName)
                try:
                    m = Manifest(self.getAndroidManifest(package), False, has_activity=True)
                    self.__get_activities(arguments, m)
                except ET.ParseError as e:
                    self.stderr.write("%s cannot parse manifest. %s" % (package, e))
        else:
            package = arguments.package
            try:
                m = Manifest(self.getAndroidManifest(package), False, has_activity=True)
                self.__get_activities(arguments, m)
            except ET.ParseError as e:
                self.stderr.write("%s cannot parse manifest. %s" % (package, e))

    def __get_activities(self, arguments, manifest: Manifest):
        activities = manifest.application.activities

        exported_activities = []
        hidden_activities = []
        for e in activities:
            if e.is_exported():
                exported_activities.append(e)
            else:
                hidden_activities.append(e)

        self.stdout.write("Package: %s\n" % manifest.package)

        if len(activities) == 0:
            self.stdout.write("  No matching activities.\n\n")
        else:
            if not arguments.unexported:
                for activity in exported_activities:
                    self.__print_activity(None, activity, "  ", arguments.show_intent_filters)
            else:
                self.stdout.write("  Exported Activities:\n")
                for activity in exported_activities:
                    self.__print_activity(None, activity, "    ", arguments.show_intent_filters)
                self.stdout.write("  Hidden Activities:\n")
                for activity in hidden_activities:
                    self.__print_activity(None, activity, "    ", arguments.show_intent_filters)
            self.stdout.write("\n")

    def __print_activity(self, package, activity: Activity, prefix, include_intent_filters):
        self.stdout.write("%s%s\n" % (prefix, activity.name))

        if activity.parentActivityName is not None:
            self.stdout.write("%s  Parent Activity: %s\n" % (prefix, activity.parentActivityName))

        permissionInfo = self.singlePermissionInfo(str(activity.permission))
        if permissionInfo is None:
            self.stdout.write("%s  Permission: %s [Non-existent]\n" % (prefix, activity.permission))
        else:
            self.stdout.write("%s    %s\n" % (prefix, permissionInfo))

        if activity.targetActivity is not None:
            self.stdout.write("%s  Target Activity: %s\n" % (prefix, activity.targetActivity))
        if include_intent_filters:
            for intent_filter in activity.intent_filters:
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
                
class Start(Module):

    name = "Start an Activity"
    description = "Starts an Activity using the formulated intent."
    examples = """Start the Browser with an explicit intent:

    dz> run app.activity.start
                --component com.android.browser
                            com.android.browser.BrowserActivity
                --flags ACTIVITY_NEW_TASK
                
If no flags are specified, drozer will add the ACTIVITY_NEW_TASK flag. To launch an activity with no flags:

    dz> run app.activity.start
                --component com.android.browser
                            com.android.browser.BrowserActivity
                --flags 0x0

Starting the Browser with an implicit intent:

    dz> run app.activity.start
                --action android.intent.action.VIEW
                --data-uri http://www.google.com
                --flags ACTIVITY_NEW_TASK

For more information on how to formulate an Intent, type 'help intents'."""
    author = "MWR InfoSecurity (@mwrlabs)"
    date = "2012-11-06"
    license = "BSD (3 clause)"
    path = ["app", "activity"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        android.Intent.addArgumentsTo(parser)

    def execute(self, arguments):
        intent = android.Intent.fromParser(arguments)

        if len(intent.flags) == 0:
            intent.flags.append('ACTIVITY_NEW_TASK')
        
        if intent.isValid():
            self.getContext().startActivity(intent.buildIn(self))
        else:
            self.stderr.write("invalid intent: one of action or component must be set\n")
    
    def get_completion_suggestions(self, action, text, **kwargs):
        if action.dest in ["action", "category", "component", "data_uri",
                           "extras", "flags", "mimetype"]:
            return android.Intent.get_completion_suggestions(action, text, **kwargs)
