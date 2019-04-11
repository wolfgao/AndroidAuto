# -*- coding: UTF-8 -*-
"""
@author: Gaochuang Yang
@file:adblocal_helper.py
@time:2019/4/11
"""
import whichcraft
import subprocess
import re
import socket
import os
from retry import retry
import uiautomator2 as u2
from utils import Logger
import time
from threading import Timer

from utils.adbutils.adb_strategy import AdbStrategy


class adb_local_helper(AdbStrategy):
    def __init__(self, udid=None):
        super(adb_local_helper,self).__init__(udid)
        self._udid = udid
        pass

    def adb_path(self):
        return whichcraft.which("adb")

    def devices(self, states=['device', 'offline']):
        """
        Returns:
            [($serial1, "device"), ($serial2, "offline")]
        """
        output = subprocess.check_output([self.adb_path(), 'devices'])
        pattern = re.compile(
            r'(?P<serial>[^\s]+)\t(?P<status>device|offline)')
        matches = pattern.findall(output.decode())
        return [(m[0], m[1]) for m in matches]

    def execute(self, *args, **kwargs):
        """
        Example:
            output = execute("ls", "-l")

        Raises:
            EnvironmentError
        """
        adb_path = self.adb_path()
        assert adb_path is not None
        cmds = [adb_path, '-s', self._udid] if self._udid else [adb_path]
        cmds.extend(args)
        cmdline = subprocess.list2cmdline(map(str, cmds))
        print(cmdline)
        try:
            return subprocess.check_output(
                cmdline, stderr=subprocess.STDOUT, shell=True,close_fds=True).decode('utf-8')
        except subprocess.CalledProcessError as e:
            if kwargs.get('raise_error', True):
                raise EnvironmentError("subprocess", cmdline,
                                       e.output.decode(
                                           'utf-8', errors='ignore'))
            # else:
            #     print("Error output:", e.output.decode(
            #         'utf-8', errors='ignore'))
            return ''

    @property
    def serial(self):
        if self._udid:
            return self._udid
        self._udid = subprocess.check_output(
            [self.adb_path(), "get-serialno"]).decode('utf-8').strip()
        return self._udid

    def forward(self, local, remote, rebind=True):
        if isinstance(local, int):
            local = 'tcp:%d' % local
        if isinstance(remote, int):
            remote = 'localabstract:webview_devtools_remote_%d' % remote
        if rebind:
            return self.execute('forward', local, remote)
        else:
            return self.execute('forward', '--no-rebind', local, remote)

    def forward_list(self):
        """
        Only return tcp:<int> format forwards
        Returns:
            {
                "{RemotePort}": "{LocalPort}"
            }
        """
        output = self.execute('forward', '--list')
        ret = {}
        for groups in re.findall('([^\s]+)\s+tcp:(\d+)\s+localabstract:webview_devtools_remote_(\d+)', output):
            if len(groups) != 3:
                continue
            serial, lport, rport = groups
            if serial != self.serial:
                continue
            ret[int(rport)] = int(lport)
        return ret

    def forward_target_list(self):
        """
        Only return tcp:<int> format forwards
        Returns:
            {
                "{RemotePort}": "{LocalPort}"
            }
        """
        output = self.execute('forward', '--list')
        ret = {}
        for groups in re.findall('([^\s]+)\s+tcp:(\d+)\s+tcp:(\d+)', output):
            if len(groups) != 3:
                continue
            serial, lport, rport = groups
            if serial != self.serial:
                continue
            ret[int(rport)] = int(lport)
        return ret

    def clear_remote_target(self):
        output = self.execute('forward', '--list')
        ret = {}
        for groups in re.findall('([^\s]+)\s+tcp:(\d+)\s+tcp:9229', output):
            if len(groups) != 3:
                continue
            serial, lport = groups
            if serial != self.serial:
                continue
            output = self.execute('forward', '--remove', 'tcp:{}'.format(lport))

    def clear_remote_start(self):
        output = self.execute('forward', '--list')
        ret = {}
        for groups in re.findall('([^\s]+)\s+tcp:(\d+)\s+localabstract:webview_devtools_remote_(\d+)', output):
            if len(groups) != 3:
                continue
            serial, lport, rport = groups
            if serial != self.serial:
                continue
            output = self.execute('forward', '--remove','tcp:{}'.format(lport))

    def find_free_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('localhost', 0))
        try:
            return s.getsockname()[1]
        finally:
            s.close()

    def forward_port(self, remote_port):
        forwards = self.forward_list()
        lport = forwards.get(remote_port)
        if lport:
            return lport
        free_port = self.find_free_port()
        self.forward(free_port, remote_port)
        return free_port

    def forward_port_xcx(self):
        forwards = self.forward_target_list()
        lport = forwards.get(9229)
        if lport:
            return lport
        free_port = self.find_free_port()
        self.forward_xcx(free_port, 9229)
        return free_port

    def forward_xcx(self,local, remote, rebind=True):
        if isinstance(local, int):
            local = 'tcp:%d' % local
        if isinstance(remote, int):
            remote = 'tcp:%d' % remote
        if rebind:
            return self.execute('forward', local, remote)
        else:
            return self.execute('forward', '--no-rebind', local, remote)


    def shell(self, *args, **kwargs):
        # print("args:{}".format(args))
        args = ["shell"] + list(args)
        # print(args)
        return self.execute(*args, **kwargs)

    def getprop(self, prop):
        return self.execute('shell', 'getprop', prop).strip()

    def push(self, src, dst, mode=0o644):
        self.execute('push', src, dst)
        if mode != 0o644:
            self.shell('chmod', oct(mode)[-3:], dst)

    def install(self, apk_path):
        sdk = self.getprop('ro.build.version.sdk')
        if int(sdk) <= 23:
            self.execute('install', '-d', '-r', apk_path)
            return
        try:
            # some device is missing -g
            self.execute('install', '-d', '-r', '-g', apk_path)
        except EnvironmentError:
            self.execute('install', '-d', '-r', apk_path)

    def uninstall(self, pkg_name):
        return self.execute('uninstall', pkg_name, raise_error=False)

    def app_start(self,pkg_name):
        return self.shell('monkey', '-p',pkg_name ,'-c' ,'android.intent.category.LAUNCHER', '1')

    def app_stop(self,pkg_name):
        return self.shell('am', 'force-stop', pkg_name)

    def package_info(self, pkg_name):
        output = self.shell('dumpsys', 'package', pkg_name)
        m = re.compile(r'versionName=(?P<name>[\d.]+)').search(output)
        version_name = m.group('name') if m else None
        m = re.search(r'PackageSignatures\{(.*?)\}', output)
        signature = m.group(1) if m else None
        if version_name is None and signature is None:
            return None
        return dict(version_name=version_name, signature=signature)

    @retry(EnvironmentError, delay=.5, tries=3, jitter=.1)
    def current_app(self):
        """
        Returns:
            dict(package, activity, pid?)

        Raises:
            EnvironementError

        For developer:
            Function reset_uiautomator need this function, so can't use jsonrpc here.
        """
        # Related issue: https://github.com/openatx/uiautomator2/issues/200
        # $ adb shell dumpsys window windows
        # Example output:
        #   mCurrentFocus=Window{41b37570 u0 com.incall.apps.launcher/com.incall.apps.launcher.Launcher}
        #   mFocusedApp=AppWindowToken{422df168 token=Token{422def98 ActivityRecord{422dee38 u0 com.example/.UI.play.PlayActivity t14}}}
        # Regexp
        #   r'mFocusedApp=.*ActivityRecord{\w+ \w+ (?P<package>.*)/(?P<activity>.*) .*'
        #   r'mCurrentFocus=Window{\w+ \w+ (?P<package>.*)/(?P<activity>.*)\}')
        _focusedRE = re.compile(
            r'mCurrentFocus=Window{.*\s+(?P<package>[^\s]+)/(?P<activity>[^\s]+)\}')

        m = _focusedRE.search(self.shell('dumpsys', 'window', 'windows')[0])
        if m:
            return dict(
                package=m.group('package'), activity=m.group('activity'))

        # try: adb shell dumpsys activity top
        _activityRE = re.compile(
            r'ACTIVITY (?P<package>[^\s]+)/(?P<activity>[^/\s]+) \w+ pid=(?P<pid>\d+)'
        )
        output= self.shell('dumpsys', 'activity', 'top')
        ms = _activityRE.finditer(output)
        ret = None
        for m in ms:
            ret = dict(
                package=m.group('package'),
                activity=m.group('activity'),
                pid=int(m.group('pid')))
        if ret:  # get last result
            return ret
        raise EnvironmentError("Couldn't get focused app")

    def setU2Driver(self):
        driver = None
        try:
            adbshellcmd = "%s -s %s shell" % (whichcraft.which("adb"), self._serial)
            readObj = os.popen(adbshellcmd+" input keyevent 3")
            readObj.close()

            killATXAgent = "%s ps -ef | grep atx |awk '{print $2}'|xargs -I {} %s kill -9 {}" % (
                adbshellcmd, adbshellcmd)
            readObj = os.popen(killATXAgent)
            readObj.close()

            killATXAgent = "%s ps | grep atx |awk '{print $2}'|xargs -I {} %s kill -9 {}" % (
                adbshellcmd, adbshellcmd)
            readObj = os.popen(killATXAgent)
            readObj.close()

            readObj = os.popen("%s am force-stop %s" % (adbshellcmd, 'com.github.uiautomator'))
            readObj.close()
            time.sleep(3)

            cmd = "python -m uiautomator2 init --serial %s" % self._serial
            readObj = os.popen(cmd)
            readObj.close()
            time.sleep(3)
            times = 3
            while (times):
                readObj = os.popen("%s am start -n %s/%s" % (adbshellcmd, 'com.github.uiautomator', '.MainActivity'))
                readObj.close()
                time.sleep(2)
                # cur_app = self.current_app()
                # if cur_app.has_key('package'):
                #     cur_pkg_name = cur_app['package']
                #
                times -= 1
            driver = u2.connect(self._serial)
            Logger.INFO(info="driver initialed",tag=self._serial)

        except:
            Logger.INFO(info="failed to connect to uiautomator2 first times",tag=self._serial)
            try:
                adbshellcmd = "%s -s %s shell" % (whichcraft.which("adb"), self._serial)

                killATXAgent = "%s ps -ef | grep atx |awk '{print $2}'|xargs -I {} %s kill -9 {}" % (
                    adbshellcmd, adbshellcmd)
                readObj = os.popen(killATXAgent)
                readObj.close()

                killATXAgent = "%s ps | grep atx |awk '{print $2}'|xargs -I {} %s kill -9 {}" % (
                    adbshellcmd, adbshellcmd)
                readObj= os.popen(killATXAgent)
                readObj.close()
                readObj = os.popen("%s am force-stop %s" % (adbshellcmd, 'com.github.uiautomator'))
                readObj.close()
                time.sleep(3)

                cmd = "python -m uiautomator2 init --mirror --serial %s" % self._serial
                readObj = os.popen(cmd)
                readObj.close()
                time.sleep(3)
                times = 3
                while (times):
                    readObj = os.popen("%s am start -n %s/%s" % (adbshellcmd, 'com.github.uiautomator', '.MainActivity'))
                    readObj.close()
                    time.sleep(2)
                    # cur_app = self.current_app()
                    # if cur_app.has_key('package'):
                    #     cur_pkg_name = cur_app['package']
                    #
                    times -= 1
                driver = u2.connect(self._serial)
                Logger.INFO("driver initialed twice time")
            except:
                adbshellcmd = "%s -s %s shell"%(whichcraft.which("adb"), self._serial)
                # killATXAgent = "%s ps | grep atx |awk '{print $2}'|xargs -I {} %s kill -9 {}"%(
                #     adbshellcmd, adbshellcmd)
                # # subprocess.Popen(killATXAgent, stdout=subprocess.PIPE,
                # #     stderr=subprocess.STDOUT, shell=True)
                # os.popen(killATXAgent)
                cmd = "python -m uiautomator2 init --mirror --serial %s"%self._serial
                # subprocess.Popen(cmd, stdout=subprocess.PIPE,
                #     stderr=subprocess.STDOUT, shell=True)
                readObj = os.popen(cmd)
                readObj.close()
                time.sleep(3)
                try:
                    driver  = u2.connect(self._serial)
                    Logger.INFO("driver initialed")
                except:
                    Logger.INFO("failed to connect to uiautomator2 third times")
        finally:
            if not driver:
                Logger.INFO("XXXXX failed to connect to uiautomator2 XXXX")
        return driver

    def swipe(self,fx, fy, tx, ty,duration=0.1, steps=None):
        if not steps:
            steps = int(duration * 200)
        self.shell('input','swipe',str(fx),str(fy),str(tx),str(ty),steps)


    def drag(self,fx, fy, tx, ty,duration=0.1, steps=None):
        if not steps:
            steps = int(duration * 200)
        self.shell('input','drag',str(fx),str(fy),str(tx),str(ty),steps)

    def execute_adb_shell(self, cmd, timeout):
        """
         local adb shell
         :param cmd: 命令字符串
         :param timeout: 设置超时时间，默认没有,单位为秒
         :return: (未超时bool，stdoutput, erroutput)
        """
        Logger.INFO(cmd)
        cmd_timer = None
        stdoutput = None
        erroutput = None
        p = subprocess.Popen("adb -s %s shell" % self.udid, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             shell=True)

        if timeout is not None:
            try:
                timeout = int(timeout)
            except:
                timeout = 20
            cmd_timer = Timer(timeout, self._kill_proc_by_timer, [p])
            cmd_timer.start()
        try:
            cmd = (cmd+"\nexit\n").encode(encoding='utf-8')
            (stdoutput, erroutput) = p.communicate(cmd, timeout=timeout)
        except BaseException as err:
            print('except' + err)
        finally:
            if cmd_timer is not None:
                cmd_timer.cancel()
        print(stdoutput)
        print(erroutput)
        return (not self.has_timer_kill, stdoutput, erroutput)
        pass

    def adb_pull(self, path_to_file, target_file, timeout):
        cmd = "adb pull {0} {1}".format(path_to_file, target_file)
        return self.execute_local_shell(cmd, timeout)

    def install_app(self, app_path, has_permission=False, timeout=None):
        print('install in localAdb')
        if has_permission:
            cmd = "adb -s %s install -g %s"%(self.udid,app_path)
        else:
            cmd = "adb -s %s install -r %s" % (self.udid, app_path)
        temp = self.execute_local_shell(cmd,timeout)
        # 解决偶发的安装失败的问题，后期可以考虑加入重试机制
        if temp[1] is not None and temp[1].count("INSTALL_FAILED_UID_CHANGED") > 0:
            return self.execute_local_shell(cmd, 30)
        else:
            return temp


    def uninstall_app(self, package_name, timeout):
        return self.execute_local_shell("adb -s %s uninstall %s" % (self.udid, package_name), timeout=timeout)

if __name__ == "__main__":
    udid = "1fa2b4c2"

    localadb = adb_local_helper(udid)
    (output0,output1,output2) = localadb.execute_adb_shell("getprop ro.product.brand",timeout=30)
    print(output1, output2)

    adb= adb_local_helper(udid)
    print(adb.adb_path())
    print(adb.devices()[0][0]) # return a device list, each element is a tuple
    print(adb.serial)
    print(adb.forward_list())
    adb.app_start("com.qiyi.video")
    print(adb.current_app()['package'])
    print(adb.current_app()['activity'])
    print(adb.current_app()['pid'])
