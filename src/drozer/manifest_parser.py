from typing import Union, List
import xml.etree.ElementTree as ET

ANDROID_PREFIX = '{http://schemas.android.com/apk/res/android}'


class XmlCompact:
    def __init__(self, xml: Union[str, ET.Element]):
        if isinstance(xml, str):
            xml = ET.fromstring(xml)
        self.xmlET: ET.Element = xml

    def __getattr__(self, item: str):
        if item in ['xmlET'] or item.startswith("__") and item.endswith("__"):
            return None
        try:
            return self.xmlET.attrib[ANDROID_PREFIX + item]
        except KeyError:
            try:
                return self.xmlET.attrib[item]
            except KeyError:
                return None

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}>"


class Manifest(XmlCompact):
    # https://github.com/aosp-mirror/platform_frameworks_base/blob/master/core/res/res/values/attrs_manifest.xml
    # TODO: It's not very complete, some attributes are missing here
    # FIXME: apk-analyzer escape double quote, which causes xml parse error
    def __init__(self, xml: Union[str, ET.Element], all_node=True, *,
                 has_activity=False, has_service=False, has_receiver=False, has_provider=False, has_permission=False):
        super().__init__(xml)

        self.package: str = super().__getattr__("package")
        self.versionCode: str = super().__getattr__("versionCode")
        self.versionCodeMajor: str = super().__getattr__("versionCodeMajor")
        self.versionName: str = super().__getattr__("versionName")
        self.revisionCode: str = super().__getattr__("revisionCode")
        self.sharedUserId: str = super().__getattr__("sharedUserId")
        self.sharedUserLabel: str = super().__getattr__("sharedUserLabel")
        self.installLocation: str = super().__getattr__("installLocation")
        self.isolatedSplits: str = super().__getattr__("isolatedSplits")
        self.isFeatureSplit: str = super().__getattr__("isFeatureSplit")
        self.targetSandboxVersion: str = super().__getattr__("targetSandboxVersion")
        self.compileSdkVersion: str = super().__getattr__("compileSdkVersion")
        self.compileSdkVersionCodename: str = super().__getattr__("compileSdkVersionCodename")
        self.isSplitRequired: str = super().__getattr__("isSplitRequired")

        self.application: Application = Application(self.xmlET.find("application"),
                                                    all_node=all_node,
                                                    has_activity=has_activity,
                                                    has_service=has_service,
                                                    has_receiver=has_receiver,
                                                    has_provider=has_provider,
                                                    has_permission=has_permission)

    def __repr__(self) -> str:
        return f"<Manifest {self.package}>"


class Application(XmlCompact):

    def __init__(self, xml: Union[str, ET.Element], all_node=True, *,
                 has_activity=False, has_service=False, has_receiver=False, has_provider=False, has_permission=False):
        super().__init__(xml)

        self.activities: List[Activity] = []
        self.services: List[Service] = []
        self.receivers: List[Receiver] = []
        self.providers: List[Provider] = []
        self.permissions: List[Permission] = []

        if xml is None:
            # some manifest doesn't contain Application
            return

        self.name: str = super().__getattr__("name")
        self.theme: str = super().__getattr__("theme")
        self.label: str = super().__getattr__("label")
        self.icon: str = super().__getattr__("icon")
        self.roundIcon: str = super().__getattr__("roundIcon")
        self.banner: str = super().__getattr__("banner")
        self.logo: str = super().__getattr__("logo")
        self.description: str = super().__getattr__("description")
        self.permission: str = super().__getattr__("permission")
        self.process: str = super().__getattr__("process")
        self.taskAffinity: str = super().__getattr__("taskAffinity")
        self.allowTaskReparenting: str = super().__getattr__("allowTaskReparenting")
        self.hasCode: str = super().__getattr__("hasCode")
        self.persistent: str = super().__getattr__("persistent")
        self.persistentWhenFeatureAvailable: str = super().__getattr__("persistentWhenFeatureAvailable")
        self.requiredForAllUsers: str = super().__getattr__("requiredForAllUsers")
        self.enabled: str = super().__getattr__("enabled")
        self.debuggable: str = super().__getattr__("debuggable")
        self.vmSafeMode: str = super().__getattr__("vmSafeMode")
        self.hardwareAccelerated: str = super().__getattr__("hardwareAccelerated")
        self.manageSpaceActivity: str = super().__getattr__("manageSpaceActivity")
        self.allowClearUserData: str = super().__getattr__("allowClearUserData")
        self.testOnly: str = super().__getattr__("testOnly")
        self.backupAgent: str = super().__getattr__("backupAgent")
        self.allowBackup: str = super().__getattr__("allowBackup")
        self.fullBackupOnly: str = super().__getattr__("fullBackupOnly")
        self.fullBackupContent: str = super().__getattr__("fullBackupContent")
        self.killAfterRestore: str = super().__getattr__("killAfterRestore")
        self.restoreNeedsApplication: str = super().__getattr__("restoreNeedsApplication")
        self.restoreAnyVersion: str = super().__getattr__("restoreAnyVersion")
        self.backupInForeground: str = super().__getattr__("backupInForeground")
        self.largeHeap: str = super().__getattr__("largeHeap")
        self.cantSaveState: str = super().__getattr__("cantSaveState")
        self.uiOptions: str = super().__getattr__("uiOptions")
        self.supportsRtl: str = super().__getattr__("supportsRtl")
        self.restrictedAccountType: str = super().__getattr__("restrictedAccountType")
        self.requiredAccountType: str = super().__getattr__("requiredAccountType")
        self.isGame: str = super().__getattr__("isGame")
        self.usesCleartextTraffic: str = super().__getattr__("usesCleartextTraffic")
        self.multiArch: str = super().__getattr__("multiArch")
        self.useEmbeddedDex: str = super().__getattr__("useEmbeddedDex")
        self.extractNativeLibs: str = super().__getattr__("extractNativeLibs")
        self.defaultToDeviceProtectedStorage: str = super().__getattr__("defaultToDeviceProtectedStorage")
        self.directBootAware: str = super().__getattr__("directBootAware")
        self.resizeableActivity: str = super().__getattr__("resizeableActivity")
        self.maxAspectRatio: str = super().__getattr__("maxAspectRatio")
        self.minAspectRatio: str = super().__getattr__("minAspectRatio")
        self.networkSecurityConfig: str = super().__getattr__("networkSecurityConfig")
        self.appCategory: str = super().__getattr__("appCategory")
        self.classLoader: str = super().__getattr__("classLoader")
        self.appComponentFactory: str = super().__getattr__("appComponentFactory")
        self.usesNonSdkApi: str = super().__getattr__("usesNonSdkApi")
        self.hasFragileUserData: str = super().__getattr__("hasFragileUserData")
        self.zygotePreloadName: str = super().__getattr__("zygotePreloadName")
        self.allowClearUserDataOnFailedRestore: str = super().__getattr__("allowClearUserDataOnFailedRestore")
        self.allowAudioPlaybackCapture: str = super().__getattr__("allowAudioPlaybackCapture")
        self.requestLegacyExternalStorage: str = super().__getattr__("requestLegacyExternalStorage")
        self.preserveLegacyExternalStorage: str = super().__getattr__("preserveLegacyExternalStorage")
        self.forceQueryable: str = super().__getattr__("forceQueryable")
        self.crossProfile: str = super().__getattr__("crossProfile")
        self.allowNativeHeapPointerTagging: str = super().__getattr__("allowNativeHeapPointerTagging")
        self.gwpAsanMode: str = super().__getattr__("gwpAsanMode")
        self.allowAutoRevokePermissionsExemption: str = super().__getattr__("allowAutoRevokePermissionsExemption")
        self.autoRevokePermissions: str = super().__getattr__("autoRevokePermissions")

        if all_node or has_activity:
            for activityET in self.xmlET.findall("activity"):
                self.activities.append(Activity(activityET))
        if all_node or has_service:
            for serviceET in self.xmlET.findall("service"):
                self.services.append(Service(serviceET))
        if all_node or has_receiver:
            for receiverET in self.xmlET.findall("receiver"):
                self.receivers.append(Receiver(receiverET))
        if all_node or has_provider:
            for providerET in self.xmlET.findall("provider"):
                self.providers.append(Provider(providerET))
        if all_node or has_permission:
            for permissionET in self.xmlET.findall("permission"):
                self.permissions.append(Permission(permissionET))


class Activity(XmlCompact):
    def __init__(self, xml: Union[str, ET.Element]):
        super().__init__(xml)

        self.intent_filters: List[IntentFilter] = []

        self.name: str = super().__getattr__("name")
        self.theme: str = super().__getattr__("theme")
        self.label: str = super().__getattr__("label")
        self.description: str = super().__getattr__("description")
        self.icon: str = super().__getattr__("icon")
        self.roundIcon: str = super().__getattr__("roundIcon")
        self.banner: str = super().__getattr__("banner")
        self.logo: str = super().__getattr__("logo")
        self.launchMode: str = super().__getattr__("launchMode")
        self.screenOrientation: str = super().__getattr__("screenOrientation")
        self.configChanges: str = super().__getattr__("configChanges")
        self.recreateOnConfigChanges: str = super().__getattr__("recreateOnConfigChanges")
        self.permission: str = super().__getattr__("permission")
        self.multiprocess: str = super().__getattr__("multiprocess")
        self.process: str = super().__getattr__("process")
        self.taskAffinity: str = super().__getattr__("taskAffinity")
        self.allowTaskReparenting: str = super().__getattr__("allowTaskReparenting")
        self.finishOnTaskLaunch: str = super().__getattr__("finishOnTaskLaunch")
        self.finishOnCloseSystemDialogs: str = super().__getattr__("finishOnCloseSystemDialogs")
        self.clearTaskOnLaunch: str = super().__getattr__("clearTaskOnLaunch")
        self.noHistory: str = super().__getattr__("noHistory")
        self.alwaysRetainTaskState: str = super().__getattr__("alwaysRetainTaskState")
        self.stateNotNeeded: str = super().__getattr__("stateNotNeeded")
        self.excludeFromRecents: str = super().__getattr__("excludeFromRecents")
        self.showOnLockScreen: str = super().__getattr__("showOnLockScreen")
        self.enabled: str = super().__getattr__("enabled")
        self.exported: str = super().__getattr__("exported")
        self.windowSoftInputMode: str = super().__getattr__("windowSoftInputMode")
        self.immersive: str = super().__getattr__("immersive")
        self.hardwareAccelerated: str = super().__getattr__("hardwareAccelerated")
        self.uiOptions: str = super().__getattr__("uiOptions")
        self.parentActivityName: str = super().__getattr__("parentActivityName")
        self.singleUser: str = super().__getattr__("singleUser")
        self.systemUserOnly: str = super().__getattr__("systemUserOnly")
        self.persistableMode: str = super().__getattr__("persistableMode")
        self.allowEmbedded: str = super().__getattr__("allowEmbedded")
        self.documentLaunchMode: str = super().__getattr__("documentLaunchMode")
        self.maxRecents: str = super().__getattr__("maxRecents")
        self.autoRemoveFromRecents: str = super().__getattr__("autoRemoveFromRecents")
        self.relinquishTaskIdentity: str = super().__getattr__("relinquishTaskIdentity")
        self.resumeWhilePausing: str = super().__getattr__("resumeWhilePausing")
        self.resizeableActivity: str = super().__getattr__("resizeableActivity")
        self.supportsPictureInPicture: str = super().__getattr__("supportsPictureInPicture")
        self.maxAspectRatio: str = super().__getattr__("maxAspectRatio")
        self.minAspectRatio: str = super().__getattr__("minAspectRatio")
        self.lockTaskMode: str = super().__getattr__("lockTaskMode")
        self.showForAllUsers: str = super().__getattr__("showForAllUsers")
        self.showWhenLocked: str = super().__getattr__("showWhenLocked")
        self.inheritShowWhenLocked: str = super().__getattr__("inheritShowWhenLocked")
        self.turnScreenOn: str = super().__getattr__("turnScreenOn")
        self.directBootAware: str = super().__getattr__("directBootAware")
        self.alwaysFocusable: str = super().__getattr__("alwaysFocusable")
        self.enableVrMode: str = super().__getattr__("enableVrMode")
        self.rotationAnimation: str = super().__getattr__("rotationAnimation")
        self.visibleToInstantApps: str = super().__getattr__("visibleToInstantApps")
        self.splitName: str = super().__getattr__("splitName")
        self.colorMode: str = super().__getattr__("colorMode")
        self.forceQueryable: str = super().__getattr__("forceQueryable")
        self.preferMinimalPostProcessing: str = super().__getattr__("preferMinimalPostProcessing")

        self.targetActivity: str = super().__getattr__("targetActivity")
        self.parentActivityName: str = super().__getattr__("parentActivityName")

        for _ in self.xmlET.findall("intent-filter"):
            self.intent_filters.append(IntentFilter(_))

    def is_exported(self):
        if str(self.exported).lower() == 'false':
            return False
        if len(self.intent_filters) > 0:
            return True
        return False


class Service(XmlCompact):
    def __init__(self, xml: Union[str, ET.Element]):
        super().__init__(xml)

        self.intent_filters: List[IntentFilter] = []

        self.name: str = super().__getattr__("name")
        self.label: str = super().__getattr__("label")
        self.description: str = super().__getattr__("description")
        self.icon: str = super().__getattr__("icon")
        self.roundIcon: str = super().__getattr__("roundIcon")
        self.banner: str = super().__getattr__("banner")
        self.logo: str = super().__getattr__("logo")
        self.permission: str = super().__getattr__("permission")
        self.process: str = super().__getattr__("process")
        self.enabled: str = super().__getattr__("enabled")
        self.exported: str = super().__getattr__("exported")
        self.stopWithTask: str = super().__getattr__("stopWithTask")
        self.isolatedProcess: str = super().__getattr__("isolatedProcess")
        self.singleUser: str = super().__getattr__("singleUser")
        self.directBootAware: str = super().__getattr__("directBootAware")
        self.externalService: str = super().__getattr__("externalService")
        self.visibleToInstantApps: str = super().__getattr__("visibleToInstantApps")
        self.splitName: str = super().__getattr__("splitName")
        self.useAppZygote: str = super().__getattr__("useAppZygote")
        self.foregroundServiceType: str = super().__getattr__("foregroundServiceType")

        for _ in self.xmlET.findall("intent-filter"):
            self.intent_filters.append(IntentFilter(_))


class Provider(XmlCompact):
    def __init__(self, xml: Union[str, ET.Element]):
        super().__init__(xml)

        self.grant_uri_permissions: List[GrantUriPermission] = []
        self.path_permissions: List[PathPermission] = []

        self.name: str = super().__getattr__("name")
        self.label: str = super().__getattr__("label")
        self.description: str = super().__getattr__("description")
        self.icon: str = super().__getattr__("icon")
        self.roundIcon: str = super().__getattr__("roundIcon")
        self.banner: str = super().__getattr__("banner")
        self.logo: str = super().__getattr__("logo")
        self.process: str = super().__getattr__("process")
        self.authorities: str = super().__getattr__("authorities")
        self.syncable: str = super().__getattr__("syncable")
        self.readPermission: str = super().__getattr__("readPermission")
        self.writePermission: str = super().__getattr__("writePermission")
        self.grantUriPermissions: str = super().__getattr__("grantUriPermissions")
        self.forceUriPermissions: str = super().__getattr__("forceUriPermissions")
        self.permission: str = super().__getattr__("permission")
        self.multiprocess: str = super().__getattr__("multiprocess")
        self.initOrder: str = super().__getattr__("initOrder")
        self.enabled: str = super().__getattr__("enabled")
        self.exported: str = super().__getattr__("exported")
        self.singleUser: str = super().__getattr__("singleUser")
        self.directBootAware: str = super().__getattr__("directBootAware")
        self.visibleToInstantApps: str = super().__getattr__("visibleToInstantApps")
        self.splitName: str = super().__getattr__("splitName")

        self.authorities: str = super().__getattr__("authorities")

        for _ in self.xmlET.findall("grant-uri-permission"):
            self.grant_uri_permissions.append(GrantUriPermission(_))
        for _ in self.xmlET.findall("path-permission"):
            self.path_permissions.append(PathPermission(_))

    def is_exported(self):
        if str(self.exported).lower() == 'true':
            return True
        return False


class Receiver(XmlCompact):
    def __init__(self, xml: Union[str, ET.Element]):
        super().__init__(xml)

        self.intent_filters: List[IntentFilter] = list()

        self.name: str = super().__getattr__("name")
        self.label: str = super().__getattr__("label")
        self.description: str = super().__getattr__("description")
        self.icon: str = super().__getattr__("icon")
        self.roundIcon: str = super().__getattr__("roundIcon")
        self.banner: str = super().__getattr__("banner")
        self.logo: str = super().__getattr__("logo")
        self.permission: str = super().__getattr__("permission")
        self.process: str = super().__getattr__("process")
        self.enabled: str = super().__getattr__("enabled")
        self.exported: str = super().__getattr__("exported")
        self.singleUser: str = super().__getattr__("singleUser")
        self.directBootAware: str = super().__getattr__("directBootAware")

        for _ in self.xmlET.findall("intent-filter"):
            self.intent_filters.append(IntentFilter(_))

    def is_exported(self):
        if str(self.exported).lower() == 'false':
            return False
        return True


class Permission(XmlCompact):
    def __init__(self, xml: Union[str, ET.Element]):
        super().__init__(xml)

        self.name: str = super().__getattr__("name")
        self.label: str = super().__getattr__("label")
        self.icon: str = super().__getattr__("icon")
        self.roundIcon: str = super().__getattr__("roundIcon")
        self.banner: str = super().__getattr__("banner")
        self.logo: str = super().__getattr__("logo")
        self.permissionGroup: str = super().__getattr__("permissionGroup")
        self.backgroundPermission: str = super().__getattr__("backgroundPermission")
        self.description: str = super().__getattr__("description")
        self.request: str = super().__getattr__("request")
        self.protectionLevel: str = super().__getattr__("protectionLevel")
        self.permissionFlags: str = super().__getattr__("permissionFlags")


class PermissionGroup(XmlCompact):
    def __init__(self, xml: Union[str, ET.Element]):
        super().__init__(xml)

        self.name: str = super().__getattr__("name")
        self.label: str = super().__getattr__("label")
        self.icon: str = super().__getattr__("icon")
        self.roundIcon: str = super().__getattr__("roundIcon")
        self.banner: str = super().__getattr__("banner")
        self.logo: str = super().__getattr__("logo")
        self.description: str = super().__getattr__("description")
        self.request: str = super().__getattr__("request")
        self.requestDetail: str = super().__getattr__("requestDetail")
        self.backgroundRequest: str = super().__getattr__("backgroundRequest")
        self.backgroundRequestDetail: str = super().__getattr__("backgroundRequestDetail")
        self.permissionGroupFlags: str = super().__getattr__("permissionGroupFlags")
        self.priority: str = super().__getattr__("priority")


class IntentFilter(XmlCompact):
    def __init__(self, xml: Union[str, ET.Element]):
        super().__init__(xml)

        self.actions: List[Action] = []
        self.categories: List[Category] = []
        self.datas: List[Data] = []

        self.label: str = super().__getattr__("label")
        self.icon: str = super().__getattr__("icon")
        self.roundIcon: str = super().__getattr__("roundIcon")
        self.banner: str = super().__getattr__("banner")
        self.logo: str = super().__getattr__("logo")
        self.priority: str = super().__getattr__("priority")
        self.autoVerify: str = super().__getattr__("autoVerify")
        self.order: str = super().__getattr__("order")

        for _ in self.xmlET.findall("action"):
            self.actions.append(Action(_))
        for _ in self.xmlET.findall("data"):
            self.datas.append(Data(_))
        for _ in self.xmlET.findall("category"):
            self.categories.append(Category(_))

    def __repr__(self):
        return f"<IntentFilter {len(self.actions)} actions>"


class Action(XmlCompact):
    def __init__(self, xml: Union[str, ET.Element]):
        super().__init__(xml)

        self.name: str = super().__getattr__("name")


class Category(XmlCompact):
    def __init__(self, xml: Union[str, ET.Element]):
        super().__init__(xml)

        self.name: str = super().__getattr__("name")


class Data(XmlCompact):
    def __init__(self, xml: Union[str, ET.Element]):
        super().__init__(xml)

        self.scheme: str = super().__getattr__("scheme")
        self.host: str = super().__getattr__("host")
        self.port: str = super().__getattr__("port")
        self.path: str = super().__getattr__("path")
        self.pathPattern: str = super().__getattr__("pathPattern")
        self.pathPrefix: str = super().__getattr__("pathPrefix")
        self.mimeType: str = super().__getattr__("mimeType")

    def __repr__(self):
        return f"<Data {self.scheme}://{self.host}:{self.port}/{self.path}>"


class GrantUriPermission(XmlCompact):
    def __init__(self, xml: Union[str, ET.Element]):
        super().__init__(xml)

        self.path: str = super().__getattr__("path")
        self.pathPrefix: str = super().__getattr__("pathPrefix")
        self.pathPattern: str = super().__getattr__("pathPattern")

    def __repr__(self):
        return f"<GrantUriPermission {'%s/%s/%s' % (self.path, self.pathPrefix, self.pathPattern)}>"


class PathPermission(XmlCompact):
    def __init__(self, xml: Union[str, ET.Element]):
        super().__init__(xml)

        self.path: str = super().__getattr__("path")
        self.pathPrefix: str = super().__getattr__("pathPrefix")
        self.pathPattern: str = super().__getattr__("pathPattern")
        self.pathAdvancedPattern: str = super().__getattr__("pathAdvancedPattern")
        self.permission: str = super().__getattr__("permission")
        self.readPermission: str = super().__getattr__("readPermission")
        self.writePermission: str = super().__getattr__("writePermission")

    def __repr__(self):
        return f"<PathPermission {self.path}>"
