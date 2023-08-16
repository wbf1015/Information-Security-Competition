import secretflow as sf
import spu
import time as t
import copy
from .sfLog import *
# from .sfUtils import *


pyu_user = None
pyu_TTP = None
pyu_chrome = None
aby3_config = None
spu_aby3 = None
aby3_spu_dic = {}
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




'''
transfer all the password to the SPUobject then update the dict
return the dict
'''


def transfer_password(up_dict, pyu, spu_device, store_dic):
    # password = next(iter(up_dict.values()))
    log_list = []
    for key in up_dict:
        value = up_dict[key]
        password_pyu = pyu(get_password)(value)
        password_spu = password_pyu.to(spu_device)
        # TODO 这里可不可以把三个地址都找出来？
        log_list.append(LogInfo(5, '成功分享用户'+key+'的ABY3秘密份额于'+str(password_spu)))
        store_dic[key] = password_spu
    return log_list

def init_ABY3():
    # init the sf
    log_list = []
    global pyu_user, pyu_TTP, pyu_chrome, aby3_config, spu_aby3, aby3_spu_dic
    if spu_aby3 is None:
        sf.init(['user', 'chrome', 'TTP', 'Webserver1', 'Webserver2', 'Webserver3', 'Webserver4', 'Webserver5', 'Webserver6', 'Webserver7'], address='local')
    pyu_user = None
    pyu_TTP = None
    pyu_chrome = None
    aby3_config = None
    spu_aby3 = None
    aby3_spu_dic = {}
    # init the PYU unit
    pyu_user = sf.PYU('user')
    log_list.append(LogInfo(4, 'ABY3正在模拟初始化PYU计算单元user:'+str(pyu_user.device_type)))
    pyu_TTP = sf.PYU('TTP')
    log_list.append(LogInfo(4, 'ABY3正在模拟初始化PYU计算单元可信第三方:'+ str(pyu_TTP.device_type)))
    pyu_chrome = sf.PYU('chrome')
    log_list.append(LogInfo(4, 'ABY3正在模拟初始化PYU计算单元浏览器:' +str(pyu_chrome.device_type)))
    # the aby3 config
    aby3_config = sf.utils.testing.cluster_def(
        parties=['user', 'chrome', 'TTP'],
        runtime_config={
            'protocol': spu.spu_pb2.ABY3,
            'field': spu.spu_pb2.FM64,
        })
    spu_aby3 = sf.SPU(aby3_config)
    log_list.append(LogInfo(4, 'ABY3正在模拟初始化SPU计算单元:' + str(spu_aby3)))
    return log_list

def add_user_2_aby3_spu_dic(user_name, password):
    dic = {user_name: password}
    dic = dict_encode(dic)
    return transfer_password(dic, pyu_user, spu_aby3, aby3_spu_dic)


def add_users_2_aby3_spu_dic(info_dic):
    copy_dic = copy.deepcopy(info_dic)
    dic = dict_encode(copy_dic)
    return transfer_password(dic, pyu_user, spu_aby3, aby3_spu_dic)


def erase_user_from_aby3_spu_dic(user_name):
    log_list =[]
    log_list.append(LogInfo(5, user_name+'正在取消信任第一阶段设备，将无法自动填充密码'))
    aby3_spu_dic.pop(user_name)
    return log_list


'''
Input : username
Output : password revealed by aby3 from user、chrome、TTP
'''


def get_password_from_aby3_spu_dic(user_name):
    log_list = []
    tmp = aby3_spu_dic[user_name]
    # TODO 这里可不可以把三个代码都找出来？
    # TODO 从哪两方提取秘密份额需要说清楚
    log_list.append(LogInfo(6, '正在从浏览器-客户端中提取用户'+user_name+'的ABY3秘密份额：' + str(aby3_spu_dic[user_name])))
    return decode_unicode(array2int(sf.reveal(aby3_spu_dic[user_name]))), log_list


def get_all_from_aby3_spu_dic():
    # new_dic = {}
    # for key in aby3_spu_dic:
    #     value = None
    #     new_dic[key] = value
    return list(aby3_spu_dic.keys())


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
