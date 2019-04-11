# -*- coding: UTF-8 -*-

'''
@author: Gaochuang Yang
@file:adblocal_helper.py
@time:2019/4/11
'''

import re
from utils.HTMLTestRunner import get_global_session
from utils import Logger
from utils.adbutils.adb_stf import STFAdb
from utils.adbutils.adblocal_helper import adb_local_helper

class AdbHelper(object):

    def __init__(self, udid, isSTF=False):
        self.udid = udid
        self.has_timer_kill = False
        if get_global_session():
            isSTF = True
        else:
            isSTF = False

        if isSTF == True:
            self.adbstrategy = STFAdb(self.udid)
        else:
            self.adbstrategy = adb_local_helper(self.udid)
        pass

    def execute_adb_shell(self, cmd, timeout=30):
        return self.adbstrategy.execute_adb_shell(cmd, timeout)

    def pull_file(self, path_to_file, target_file, timeout=60):
        self.adbstrategy.adb_pull(path_to_file, target_file, timeout=timeout)

    def install_app(self, app_path, has_permission=False, timeout=30):
        self.adbstrategy.install_app(app_path, has_permission, timeout)

    def uninstall_app(self, package_name, timeout=30):
        self.adbstrategy.uninstall_app(package_name, timeout)

    def remove_sdkcard_apk(self):
        return self.execute_adb_shell("rm /sdcard/Download/*.apk")

    def start_page_by_schema(self, schema):
        return self.execute_adb_shell("am start -a android.intent.action.VIEW "
                                      "-d %s --activity-clear-task" % schema)

    def get_devices_ip_address(self):
        l = self.execute_adb_shell('ip addr | grep global')
        reg = re.compile('\d+\.\d+\.\d+\.\d+')
        return re.findall(reg, l[1])[0]

    def get_device_brand(self):
        cmd = "getprop ro.product.brand"
        # (execute_result, stdout, stderr) = self.adb_helper.adbstrategy.execute_adb_shell(cmd,timeout=30)
        (execute_result, stdout, stderr) = self.execute_adb_shell(cmd, timeout=30)
        Logger.INFO("brand type is: {}".format(stdout))
        # brand = stdout.split("\n")[0]
        brand=stdout.decode("utf-8")
        #brand = stdout.split("\n")
        brand = brand.split("\n")
        print(len(brand))
        if len(brand)<=2:
            brandname = brand[0]
        else:
            brandname = stdout.split("\r\n")[3]
        #.split("\r")[0]
        return brandname

if __name__ == '__main__':
    adb_helper = AdbHelper("1fa2b4c2", isSTF=False)
    print(adb_helper.get_device_brand())
