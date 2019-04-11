# -*- coding: UTF-8 -*-
'''
@author: Gaochuang Yang
@file:adb_strategy.py
@time:2019/4/11
'''
import sys
from os import path
basedir = path.realpath(path.join(path.dirname(__file__), '../..'))
sys.path.append(basedir)

class AdbStrategy(object):
    '''
    Abdstract class for adb strategy
    '''
    def __init__(self, udid):
        self.has_timer_kill = False
        self.udid = udid
        pass

    def adb_pull(self, path_to_file, target_file):
        pass

    def execute_adb_shell(self, cmd,timeout):
        pass

    def install_app(self, app_path, has_permission, timeout):
        pass

    def uninstall_app(self, package_name, timeout):
        pass

    def execute_local_shell(self, cmd, timeout=None):
        pass

    def _kill_proc_by_timer(self, proc):
        if proc is not None:
            proc.kill()
            self.has_timer_kill = True


