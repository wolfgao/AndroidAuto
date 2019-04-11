from utils.HTMLTestRunner import get_global_session
from utils.stfutils.device_manger import get_device_info
from utils.adbutils.adb_strategy import AdbStrategy

class STFAdb(AdbStrategy):
    """adb helper class for stf"""
    def __init__(self,udid):
        super(STFAdb,self).__init__(udid)
        self.session = get_global_session()
        self.deviceinfo = get_device_info(self.udid)
        self.execute_result = None
        self.stdoutput = ""
        self.stderrput = ""
        pass

    def on_reslove(self,dev, result):
        print(result.success)
        print(result.last_data)
        print(result.error)
        self.stdoutput = result.data
        self.stderrput = result.error
        self.execute_result = result.success


    def execute_adb_shell(self, cmd,timeout):
        Logger.INFO("execute stf adb shell cmd: {}".format(cmd))
        if self.session:
            # self.session.send_shell_cmd(self.deviceinfo, cmd, timeout_sec=timeout)
            self.session.send_shell_cmd_batch([self.deviceinfo,], cmd, timeout_sec=timeout, on_resolve=self.on_reslove)
            Logger.INFO('---adb-shell-stdoutput---')
            Logger.INFO(self.stdoutput)
            Logger.INFO('------------------------')
            return (self.execute_result, self.stdoutput, self.stderrput)
        else:
            Logger.ERROR("session is None")
            return (None, None, None)

    def _save_file_db(self, name, content):
        Logger.INFO("start saving file {}".format(name))
        if not content:
            content = 'get nothing'
        with open(name, 'wb') as f:
            f.write(content)
            Logger.INFO("end save file {}".format(name))

    def adb_pull(self, path_to_file, target_file, timeout):
        # '/sdcard/Android/data/com.ss.android.article.news/cache/debugger/debugger.db'
        HOST = 'http://thub.byted.org'
        def on_monkeylog_resolve(result):
            Logger.INFO("<------enter on_monkeylog_resolve------->")
            url = HOST + result.body['href'] + '?download'
            r = requests.get(url)
            self._save_file_db(target_file, r.content)
            # self._save_file(self.monkey_log_file, r.content)
        def on_pullfile_false(result):
            Logger.INFO("<-------pull file on reject------>")
            Logger.INFO(result)

        if self.session:
            self.session.fsretrieve(self.deviceinfo, path_to_file,
                                                on_resolve=on_monkeylog_resolve,
                                    on_reject = on_pullfile_false)

    def install_app(self, app_path, has_permission, timeout):
        Logger.INFO("execute stf adb install with app_path: {}".format(app_path))
        # if self.session:
        #     self.session.install(self.udid, href, manifest)
        pass

    def uninstall_app(self,package_name, timeout):
        Logger.INFO("execute stf adb uninstall package {}".format(package_name))
        if self.session:
            self.session.uninstall(self.deviceinfo, package_name)
        pass
