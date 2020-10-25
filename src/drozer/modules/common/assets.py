from . import loader

class Assets(loader.ClassLoader):
    """
    Utility methods for interacting with the Android Asset Manager.
    """

    def getAndroidManifest(self, package) -> str:
        """
        Extract the AndroidManifest.xml file from a package on the device, and
        recover it as an XML representation.
        """
        # https://github.com/LeadroyaL/ShrinkApkAnalyzer
        ApkAnalyzerCli = self.loadClass("common/shrink.apk", "com.android.tools.apk.analyzer.ApkAnalyzerCli")
        ApkAnalyzerImpl = self.loadClass("common/shrink.apk", "com.android.tools.apk.analyzer.ApkAnalyzerImpl")

        """
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        PrintStream ps = new PrintStream(baos, true, "utf-8");
        ApkAnalyzerCli(ps, ps, ApkAnalyzerImpl(ps));
        String content = new String(baos.toByteArray(), StandardCharsets.UTF_8);
        ps.close();
        baos.close();
        """

        baos = self.new('java.io.ByteArrayOutputStream')
        ps = self.new('java.io.PrintStream', baos)
        impl = self.reflector.construct(ApkAnalyzerImpl, ps)
        cli = self.reflector.construct(ApkAnalyzerCli, ps, ps, impl)
        cli.run(["manifest", "print", package])
        ret = baos.toByteArray().data().decode('utf-8')
        ps.close()
        baos.close()
        if "ERROR" in ret:
            self.stderr.write(ret)
            raise RuntimeError("Cannot get manifest: " + package)
        return ret

    def getAssetManager(self, package):
        """
        Get a handle on the AssetManager for the specified package.
        """

        return self.getContext().createPackageContext(package, 0).getAssets()
