from npmfix import (get_lockfile_json, loop_through_packages)
import unittest


class TestCases(unittest.TestCase):

    def test01(self):
        """Test if both packages can have their data added."""
        lockfile = get_lockfile_json("./test-files/01.package-lock.json", True)
        loop_through_packages(lockfile['packages'], False, True)

        aix_fixed: bool = 'resolved' in lockfile['packages']["node_modules/@esbuild/aix-ppc64"]
        aix_fixed = aix_fixed and 'integrity' in lockfile['packages']["node_modules/@esbuild/aix-ppc64"]

        arm_fixed: bool = 'resolved' in lockfile['packages']["node_modules/@esbuild/android-arm"]
        arm_fixed = arm_fixed and 'integrity' in lockfile['packages']["node_modules/@esbuild/android-arm"]

        self.assertTrue(aix_fixed and arm_fixed)

    def test02(self):
        """Do a only_without_resolved check"""
        lockfile = get_lockfile_json("./test-files/02.package-lock.json", True)
        loop_through_packages(lockfile['packages'], True, True)

        aix_fixed: bool = 'resolved' in lockfile['packages']["node_modules/@esbuild/aix-ppc64"]
        aix_fixed = aix_fixed and 'integrity' in lockfile['packages']["node_modules/@esbuild/aix-ppc64"]

        arm_fixed: bool = 'resolved' in lockfile['packages']["node_modules/@esbuild/android-arm"]
        arm_fixed = arm_fixed and 'integrity' not in lockfile['packages']["node_modules/@esbuild/android-arm"]

        self.assertTrue(aix_fixed and arm_fixed)

    def test03(self):
        """Test if both packages can have their data added."""
        lockfile = get_lockfile_json("./test-files/03.package-lock.json", True)
        loop_through_packages(lockfile['packages'], False, True)

        aix_fixed: bool = 'resolved' in lockfile['packages']["node_modules/@esbuild/aix-ppc64"]
        aix_fixed = aix_fixed and 'integrity' in lockfile['packages']["node_modules/@esbuild/aix-ppc64"]

        arm_fixed: bool = 'resolved' in lockfile['packages']["node_modules/@esbuild/android-arm"]
        arm_fixed = arm_fixed and 'integrity' in lockfile['packages']["node_modules/@esbuild/android-arm"]

        self.assertTrue(aix_fixed and arm_fixed)


unittest.main()
