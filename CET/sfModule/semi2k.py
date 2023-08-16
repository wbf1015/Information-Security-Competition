import random

import secretflow as sf
import spu
import time as t
import copy
from .sfLog import *

pyu_webserver1 = None
pyu_webserver2 = None
pyu_webserver3 = None
pyu_webserver4 = None
pyu_webserver5 = None
semi2k_spu_dic = {}
spu_semi2k = None
LOG_ERR = 0
LOG_OK = 1


def sys_log(msg, type):
    # 高亮打印当前时间和信息
    now = t.strftime("%Y-%m-%d %H:%M:%S", t.localtime())
    if type == LOG_ERR:
        print("\033[1;31m LOG_ERR:" + now + ": " + msg + "\033[0m")
    else:
        print("\033[1;32m LOG:" + now + ": " + msg + "\033[0m")


# 相当于封装了一个没有用的函数
def get_password(encode_list):
    return encode_list


def transfer_password(up_dict, pyu, spu_device, store_dic):
    # password = next(iter(up_dict.values()))
    log_list = []
    for key in up_dict:
        value = up_dict[key]
        password_pyu = pyu(get_password)(value)
        password_spu = password_pyu.to(spu_device)
        # TODO 这里可不可以把三个地址都找出来？
        log_list.append(LogInfo(5, '成功分享用户' + key + '的semi2k秘密份额于' + str(password_spu)))
        store_dic[key] = password_spu

    return log_list


def init_SEMI2K():
    log_list = []
    global pyu_webserver1, pyu_webserver2, pyu_webserver3, pyu_webserver4, pyu_webserver5, semi2k_spu_dic, spu_semi2k
    pyu_webserver1 = None
    pyu_webserver2 = None
    pyu_webserver3 = None
    pyu_webserver4 = None
    pyu_webserver5 = None
    semi2k_spu_dic = {}
    pyu_webserver1 = sf.PYU('Webserver1')
    pyu_webserver2 = sf.PYU('Webserver2')
    pyu_webserver3 = sf.PYU('Webserver3')
    pyu_webserver4 = sf.PYU('Webserver4')
    pyu_webserver5 = sf.PYU('Webserver5')

    log_list.append(LogInfo(4, 'semi2k正在模拟初始化webserver1：' + str(pyu_webserver1.device_type)))
    log_list.append(LogInfo(4, 'semi2k正在模拟初始化webserver2：' + str(pyu_webserver2.device_type)))
    log_list.append(LogInfo(4, 'semi2k正在模拟初始化webserver3：' + str(pyu_webserver3.device_type)))
    log_list.append(LogInfo(4, 'semi2k正在模拟初始化webserver4：' + str(pyu_webserver4.device_type)))
    log_list.append(LogInfo(4, 'semi2k正在模拟初始化webserver5：' + str(pyu_webserver5.device_type)))

    semi2k_config = sf.utils.testing.cluster_def(
        parties=['Webserver1', 'Webserver2', 'Webserver3', 'Webserver4', 'Webserver5'],
        runtime_config={
            'protocol': spu.spu_pb2.SEMI2K,
            'field': spu.spu_pb2.FM64,
        },
    )
    spu_semi2k=sf.SPU(semi2k_config)
    log_list.append(LogInfo(4, 'semi2k正在模拟初始化spu计算单元：' + str(spu_semi2k)))
    return log_list

def add_user_2_semi2k_spu_dic(user_name, password):
    dic = {user_name: password}
    dic = dict_encode(dic)
    return transfer_password(dic, pyu_webserver1, spu_semi2k, semi2k_spu_dic)


def add_users_2_semi2k_spu_dic(info_dic):
    copy_dic = copy.deepcopy(info_dic)
    dic = dict_encode(copy_dic)
    return transfer_password(dic, pyu_webserver1, spu_semi2k, semi2k_spu_dic)


def get_password_from_semi2k_spu_dic(user_name):
    tmp = semi2k_spu_dic[user_name]
    log_list = []
    sample = random.sample(range(5),3)
    # TODO 这里可不可以把三个代码都找出来？
    # TODO 这里不要写死
    log_list.append(
        LogInfo(6, '正在从webserver0 && webserver2 && webserver3中提取用户' + user_name + '的semi2k秘密份额：' + str(semi2k_spu_dic[user_name])))
    return decode_unicode(array2int(sf.reveal(semi2k_spu_dic[user_name]))), log_list


def get_all_from_semi2k_spu_dic():
    new_dic = {}
    for key in semi2k_spu_dic:
        value = None
        new_dic[key] = value
    return new_dic


# 判断是否是合法的unicode
def is_valid_unicode(i):
    if i < 0:
        return False
    if i >= 1114112:
        return False
    return True


'''we need to transfer the string type to the int list'''


def encode_unicode(string):
    encoded = []
    for char in string:
        encoded.append(ord(char))
    return encoded


'''we can choose to transfer the int list to the string type'''


def decode_unicode(int_list):
    for i in int_list:
        if not is_valid_unicode(i):
            return ''
    string = ''.join([chr(i) for i in int_list])
    return string


'''we need to transfer the password in dict to SPUobject'''


def dict_encode(up_dict):
    for key in up_dict:
        value = up_dict[key]
        new_value = encode_unicode(value)
        up_dict[key] = new_value
    return up_dict


# ========================================================================

'''here we want to peel off the jax array'''


def array2int(list_of_arrays):
    new_list = [arr.item() for arr in list_of_arrays]
    return new_list