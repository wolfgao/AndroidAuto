# -*- coding: UTF-8 -*-

import time
import sys
import threading
from utils.HTMLTestRunner import _TestResult


Log2File = False

def ERROR(info):
    #_表示不能被调用
    _worker("%s[ERROR][%s][%s]%s"%(_now(),__FUNC__(), __thread__(),info))

def FATAL(info):
    _worker("%s[FATAL][%s][%s]%s"%(_now(),__FUNC__(),__thread__(),info))

def WARN(info):
    _worker("%s[WARN][%s][%s]%s"%(_now(),__FUNC__(),__thread__(), info))

def INFO(info, tag="INFO"):
    _worker("%s[%s][%s][%s]%s"%(_now(), tag, __FUNC__(),__thread__(),info))

def _worker(info):
    if Log2File is True:
        _log2File(info)
    else:
        log2stdout(info)
        log2stringio(info)


def log2stdout(info):
    _TestResult.restore_stdout()
    print(info)

def log2stringio(info):
    if _TestResult.redirect2outputbuffer():
        print(info)
        _TestResult.restore_stdout()


def _log2File(info):
    pass

def _now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
# Use Only For Logger
def __FUNC__():
    ss_name = sys._getframe(2).f_code.co_name
    return ss_name

def __thread__():
    return threading.currentThread().name