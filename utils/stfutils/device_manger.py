# -*- coding: UTF-8 -*-
'''
@author: Gaochuang Yang
@file:adblocal_helper.py
@time:2019/4/11
'''
import sys
from os import path
basedir = path.realpath(path.join(path.dirname(__file__), '../../../..'))
sys.path.append(basedir)
import urllib
import json

from utils import Logger

STF_URL = "http://xxx.xxx.xxx"                  # your stf website
GET_DEVICE = STF_URL + "/api/v1/devices"        # device entry
USE_DEVICE= STF_URL + "/api/v1/user/devices"    # user device entry
STOP_USE_DEVICE = STF_URL + "/api/v1/user/devices/%s"

##如何生成认证token
##进入stf网页端，进入设置（settings），左侧keys tab，输入任意token名字，点击下方generate new key

AUTHOR = "xxxxxx"

AUTHOR_DICT={
    "xxx1":"xxx",
    "xxx2":"xxx"
}
def get_device_info(serial):
    request = urllib.request.Request(GET_DEVICE)
    request.add_header('Authorization', "Bearer %s" % AUTHOR)
    response = urllib.request.urlopen(request)
    try:
        devices = json.loads(response.read())
        if devices['success']:
            for device in devices["devices"]:
                if device['serial'] == serial:
                    return device
    except:
        import traceback
        traceback.print_exc()
    return None


def get_target_device(expert_device_arr):
    target_devices = []
    target_devices_ipport = []
    request = urllib.request.Request(GET_DEVICE)
    request.add_header('Authorization',"Bearer %s"%AUTHOR)
    response = urllib.request.urlopen(request)

    try:
        devices = json.loads(response.read())
        if devices['success']:
            for device in devices["devices"]:
                # print device['ready'],device['using'],device['present'],device['serial']
                if device['ready'] and not device['using'] and device['present']:
                    ip_port = device['display']['url'][5:]
                    ip,port = ip_port.split(":")
                    port = int(port) + 1
                    ip_port = str(ip) + ":" + str(port)
                    if expert_device_arr.count(device['serial']) > 0:
                        target_devices.append(device['serial'])
                        target_devices_ipport.append(ip_port)
                    pass
            if len(target_devices) > 0:
                import random
                index = len(target_devices)*random.Random().random()
                return target_devices[int(index)], target_devices_ipport[int(index)]
            else:
                return None,None
    except:
        import traceback
        traceback.print_exc()
        return None,None
    return None,None

def get_available_device_list():
    target_devices = []
    request = urllib.request.Request(GET_DEVICE)
    request.add_header('Authorization', "Bearer %s" % AUTHOR)
    response = urllib.request.urlopen(request)

    try:
        devices = json.loads(response.read())
        if devices['success']:
            for device in devices["devices"]:
                # print device['ready'], device['using'], device['present'], device['serial']
                if device['ready'] and not device['using'] and device['present']:
                    target_devices.append(device['serial'])
                    pass
            else:
                return target_devices
    except:
        import traceback
        traceback.print_exc()
        return None
    Logger.INFO(target_devices)
    return target_devices


def start_use_device(udid,timeout = 1800000):
    if udid is None:
        return False
    print(udid)
    request = urllib.request.Request(USE_DEVICE)
    request.add_header('Authorization',"Bearer %s"%AUTHOR)
    request.add_header('Content-Type',"application/json")
    request.add_data('{"serial":"%s","timeout":%s}'%(udid,timeout))

    try:
        response = urllib.request.urlopen(request)
        ret = json.loads(response.read())
        if not ret['success']:
            print(ret['description'])
        return ret['success']

    except BaseException as e:
        import traceback
        traceback.print_exc()
    except urllib.error.HTTPError:
        import traceback
        traceback.print_exc()
    return False

def get_device_and_start_use(expert_device_arr,timeout=1800000):
    return start_use_device(get_target_device(expert_device_arr),timeout=timeout)

def stop_use_device(serial):
    if serial is None:
        return False

    request = urllib.request.Request(STOP_USE_DEVICE % serial)
    request.add_header('Authorization', "Bearer %s" % AUTHOR)
    request.get_method = lambda: 'DELETE'
    try:
        response = urllib.request.urlopen(request)
        return json.loads(response.read())['success']
    except BaseException:
        import traceback
        traceback.print_exc()
    except urllib.error.HTTPError:
        import traceback
        traceback.print_exc()
    return False

if __name__ == '__main__':
    print(get_available_device_list())
    print('test')

