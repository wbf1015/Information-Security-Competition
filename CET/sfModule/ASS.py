# Additive Sharing with facility to Refresh shares via Proactivization
import random
import hashlib
import secretflow as sf
import spu
import ray
import copy
import time as t
from .sfLog import *



FIELD_SIZE = 10**16
server_name_list = ['Webserver1', 'Webserver2', 'Webserver3', 'Webserver4', 'Webserver5']
pyu_webserver1 = None
pyu_webserver2 = None
pyu_webserver3 = None
pyu_webserver4 = None
pyu_webserver5 = None
ASS_dic = {}
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


def init_ASS():
    log_list = []
    global pyu_webserver1, pyu_webserver2, pyu_webserver3, pyu_webserver4, pyu_webserver5
    pyu_webserver1 = None
    pyu_webserver2 = None
    pyu_webserver3 = None
    pyu_webserver4 = None
    pyu_webserver5 = None
    ASS_dic = {}
    pyu_webserver1 = sf.PYU('Webserver1')
    pyu_webserver2 = sf.PYU('Webserver2')
    pyu_webserver3 = sf.PYU('Webserver3')
    pyu_webserver4 = sf.PYU('Webserver4')
    pyu_webserver5 = sf.PYU('Webserver5')
    log_list.append(LogInfo(4, 'ASS正在模拟初始化webserver1：' + str(pyu_webserver1.device_type)))
    log_list.append(LogInfo(4, 'ASS正在模拟初始化webserver2：' + str(pyu_webserver2.device_type)))
    log_list.append(LogInfo(4, 'ASS正在模拟初始化webserver3：' + str(pyu_webserver3.device_type)))
    log_list.append(LogInfo(4, 'ASS正在模拟初始化webserver4：' + str(pyu_webserver4.device_type)))
    log_list.append(LogInfo(4, 'ASS正在模拟初始化webserver5：' + str(pyu_webserver5.device_type)))
    return log_list



def getAdditiveShares(secret, N, fieldSize):
    '''Generate N additive shares from 'secret' in finite field of size 'fieldSize'.'''

    # Generate n-1 shares randomly
    shares = [random.randrange(fieldSize) for i in range(N-1)]
    # Append final share by subtracting all shares from secret
    shares.append((secret - sum(shares)) % fieldSize )
    return shares


def reconstructSecret(shares, fieldSize):
    '''Regenerate secret from additive shares'''
    return sum(shares) % fieldSize


def proactivizeShares(shares):
    '''Refreshed shares by proactivization'''

    n = len(shares)
    refreshedShares = [0]*n

    for s in shares:

        # Divide each share into sub-fragments using additive sharing
        subShares = getAdditiveShares(s, n, FIELD_SIZE)

        # Add subfragments of corresponding parties
        for p, sub in enumerate(subShares):
            refreshedShares[p] += sub

    return refreshedShares


# 获取webserver各个服务器的分片
# def generate_webserver_shares(n, t, org_password):
def generate_webserver_shares(n, org_password):
    webserver_ss_list = [getAdditiveShares(x, n, FIELD_SIZE) for x in org_password]
    # print(webserver_ss_list)
    print(len(webserver_ss_list), len(webserver_ss_list[0]))

    webserver_ss_list = [list(row) for row in zip(*webserver_ss_list)]
    print(len(webserver_ss_list), len(webserver_ss_list[0]))

    # compute the hash
    for index in range(n):
        hash_object = hashlib.md5()
        hash_object.update(server_name_list[index].encode('unicode-escape'))
        hash_value = hash_object.hexdigest()
        decimal_value = int(hash_value, 16)
        webserver_ss_list[index].append(decimal_value)
    # print(webserver_ss_list)
    print(len(webserver_ss_list), len(webserver_ss_list[0]))

    return webserver_ss_list


# 重构secret
def reconstruct_webserver_secret(n, reveal_list, FIELD_SIZE):
    for index in range(n):
        reveal_list[index] = reveal_list[index][:-1]
    reveal_list = [list(row) for row in zip(*reveal_list)]

    result = []
    for item in reveal_list:
        temp_password = reconstructSecret(item, fieldSize=FIELD_SIZE)
        result.append(temp_password)

    return result


# 更新webserver的秘密份额
def refresh_webserver_secret(webserver_ss_list):
    hash_list = []
    for ss_list in webserver_ss_list:
        hash_value = ss_list.pop()
        hash_list.append(hash_value)
    # print(len(webserver_ss_list), len(webserver_ss_list[0]))
    # print(hash_list)

    # refresh the data element
    webserver_ss_list = [list(row) for row in zip(*webserver_ss_list)]
    # print(len(webserver_ss_list), len(webserver_ss_list[0]))
    for index in range(len(webserver_ss_list)):
        webserver_ss_list[index] = proactivizeShares(webserver_ss_list[index])

    webserver_ss_list = [list(row) for row in zip(*webserver_ss_list)]
    # print(len(webserver_ss_list), len(webserver_ss_list[0]))
    for index in range(len(webserver_ss_list)):
        webserver_ss_list[index].append(hash_list[index])
    # print(len(webserver_ss_list), len(webserver_ss_list[0]))
    return webserver_ss_list


def refresh_user_ss(id):
    log_list = []
    value = copy.deepcopy(ASS_dic[id])
    for i in range(0,5):
        value[i] = ray.get(value[i].data)
    log_list.append(LogInfo(7, '未刷新前ASS协议节点内容为' + str(value[0]) + '、' + str(value[1]) + '、' + str(
        value[2]) + '、' + str(value[3]) + '、' + str(value[4])))
    shares = refresh_webserver_secret(value)
    log_list.append(LogInfo(7, '刷新后ASS协议节点内容为' + str(shares[0]) + '、' + str(shares[1]) + '、' + str(
        shares[2]) + '、' + str(shares[3]) + '、' + str(shares[4])))
    ss_pyu_webserver1 = pyu_webserver1(get_password)(shares[0])
    ss_pyu_webserver2 = pyu_webserver2(get_password)(shares[1])
    ss_pyu_webserver3 = pyu_webserver3(get_password)(shares[2])
    ss_pyu_webserver4 = pyu_webserver4(get_password)(shares[3])
    ss_pyu_webserver5 = pyu_webserver5(get_password)(shares[4])
    shares = [ss_pyu_webserver1, ss_pyu_webserver2, ss_pyu_webserver3, ss_pyu_webserver4, ss_pyu_webserver5]
    tmp = ''
    for pyu in shares:
        tmp += str(pyu)
    ASS_dic[id] = shares
    print('刷新成功')
    log_list.append(LogInfo(7, '用户'+id+'的ASS秘密份额刷新成功'))
    return log_list


def share_ASS_secret(n, user_dic, store_dic):
    log_list = []
    for key in user_dic:
        value = user_dic[key]
        shares = generate_webserver_shares(n,value)
        ss_pyu_webserver1 = pyu_webserver1(get_password)(shares[0])
        ss_pyu_webserver2 = pyu_webserver2(get_password)(shares[1])
        ss_pyu_webserver3 = pyu_webserver3(get_password)(shares[2])
        ss_pyu_webserver4 = pyu_webserver4(get_password)(shares[3])
        ss_pyu_webserver5 = pyu_webserver5(get_password)(shares[4])
        shares = [ss_pyu_webserver1,ss_pyu_webserver2,ss_pyu_webserver3,ss_pyu_webserver4,ss_pyu_webserver5]
        tmp = ''
        for pyu in shares:
            tmp += str(pyu)
        log_list.append(LogInfo(5, 'ASS将用户'+key+'的秘密份额分存于'+tmp))
        store_dic[key] = shares

    return log_list


def add_user_2_ASS_pyu_dic(user_name,password):
    dic = {user_name:password}
    dic = dict_encode(dic)
    return share_ASS_secret(5,dic,ASS_dic)


def add_users_2_ASS_pyu_dic(info_dic):
    used_dic = copy.deepcopy(info_dic)
    dic = dict_encode(used_dic)
    return share_ASS_secret(5, dic, ASS_dic)

def get_password_from_ASS_pyu_dic(n, user_name):
    # check()
    log_list = []
    value = copy.deepcopy(ASS_dic[user_name])
    # TODO 简化写法
    log_list.append(LogInfo(6, 'ASS协议使用节点' + str(value[0]) + '、' + str(value[1]) + '、' + str(
        value[2]) + '、' + str(value[3]) + '、' + str(value[4])+ '恢复用户' + user_name + '的秘密份额'))
    # check()
    for i in range(0,n):
        value[i] = ray.get(value[i].data)
    ret = reconstruct_webserver_secret(n, value, FIELD_SIZE)
    ret = decode_unicode(ret)
    # check()
    return ret, log_list


def get_all_from_ASS_pyu_dic(n):
    new_dic = {}
    for key in ASS_dic:
        value = get_password_from_ASS_pyu_dic(n, key)
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