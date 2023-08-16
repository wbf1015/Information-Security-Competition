import random
import copy
# from math import ceil
import hashlib
import secretflow as sf
import spu
import ray
import copy
from decimal import Decimal
from itertools import combinations
import time
import numpy as np
import numpy as np
from .sfLog import *

pyu_webserver1 = None
pyu_webserver2 = None
pyu_webserver3 = None
pyu_webserver4 = None
pyu_webserver5 = None
pyu_webserver6 = None
pyu_webserver7 = None
shamirS_dic = {}
FIELD_SIZE = 10 ** 5
# webserver的标记
server_name_list = ['Webserver1', 'Webserver2', 'Webserver3', 'Webserver4', 'Webserver5']
rest_server_name = 'RestWebserver'
LOG_ERR = 0
LOG_OK = 1


def sys_log(msg, type):
    # 高亮打印当前时间和信息
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if type == LOG_ERR:
        print("\033[1;31m LOG_ERR:" + now + ": " + msg + "\033[0m")
    else:
        print("\033[1;32m LOG:" + now + ": " + msg + "\033[0m")


# 相当于封装了一个没有用的函数
def get_password(encode_list):
    return encode_list


def init_shamirS():
    log_list = []
    global pyu_webserver1, pyu_webserver2, pyu_webserver3, pyu_webserver4, pyu_webserver5, pyu_webserver6, pyu_webserver7, shamirS_dic
    pyu_webserver1 = None
    pyu_webserver2 = None
    pyu_webserver3 = None
    pyu_webserver4 = None
    pyu_webserver5 = None
    pyu_webserver6 = None
    pyu_webserver7 = None
    shamirS_dic = {}
    pyu_webserver1 = sf.PYU('Webserver1')
    pyu_webserver2 = sf.PYU('Webserver2')
    pyu_webserver3 = sf.PYU('Webserver3')
    pyu_webserver4 = sf.PYU('Webserver4')
    pyu_webserver5 = sf.PYU('Webserver5')
    pyu_webserver6 = sf.PYU('Webserver6')
    pyu_webserver7 = sf.PYU('Webserver7')
    log_list.append(LogInfo(4, 'shamirS正在模拟初始化webserver1：' + str(pyu_webserver1.device_type)))
    log_list.append(LogInfo(4, 'shamirS正在模拟初始化webserver2：' + str(pyu_webserver2.device_type)))
    log_list.append(LogInfo(4, 'shamirS正在模拟初始化webserver3：' + str(pyu_webserver3.device_type)))
    log_list.append(LogInfo(4, 'shamirS正在模拟初始化webserver4：' + str(pyu_webserver4.device_type)))
    log_list.append(LogInfo(4, 'shamirS正在模拟初始化webserver5：' + str(pyu_webserver5.device_type)))
    log_list.append(LogInfo(4, 'shamirS正在模拟初始化webserver6：' + str(pyu_webserver6.device_type)))
    log_list.append(LogInfo(4, 'shamirS正在模拟初始化webserver7：' + str(pyu_webserver7.device_type)))

    return log_list


def reconstruct_secret(shares):
    """
    Combines individual shares (points on graph)
    using Lagranges interpolation.

    `shares` is a list of points (x, y) belonging to a
    polynomial with a constant of our key.
    """
    sums = 0
    prod_arr = []

    for j, share_j in enumerate(shares):
        xj, yj = share_j
        prod = Decimal(1)

        for i, share_i in enumerate(shares):
            xi, _ = share_i
            if i != j:
                prod *= Decimal(Decimal(xi) / (xi - xj))

        prod *= yj
        sums += Decimal(prod)

    return int(round(Decimal(sums), 0))


def polynom(x, coefficients):
    """
    This generates a single point on the graph of given polynomial
    in `x`. The polynomial is given by the list of `coefficients`.
    """
    point = 0
    # Loop through reversed list, so that indices from enumerate match the
    # actual coefficient indices
    for coefficient_index, coefficient_value in enumerate(coefficients[::-1]):
        point += x ** coefficient_index * coefficient_value
    return point


def coeff(t, secret):
    """
    Randomly generate a list of coefficients for a polynomial with
    degree of `t` - 1, whose constant is `secret`.

    For example with a 3rd degree coefficient like this:
        3x^3 + 4x^2 + 18x + 554

        554 is the secret, and the polynomial degree + 1 is
        how many points are needed to recover this secret.
        (in this case it's 4 points).
    """
    coeff = [random.randrange(0, FIELD_SIZE) for _ in range(t - 1)]
    coeff.append(secret)
    return coeff


def generate_shares(n, m, secret):
    """
    Split given `secret` into `n` shares with minimum threshold
    of `m` shares to recover this `secret`, using SSS algorithm.
    """
    coefficients = coeff(m, secret)
    shares = []

    for i in range(1, n + 1):
        x = random.randrange(1, FIELD_SIZE)
        shares.append((x, polynom(x, coefficients)))

    return shares


# 我们这里获取
def generate_webserver_shares(n, t, org_password):
    new_org_password = []
    for item in org_password:
        temp_password_ss = generate_shares(n, t, item)
        new_org_password.append(temp_password_ss)
    # print(new_org_password)

    webserver_ss_list = [list(row) for row in zip(*new_org_password)]
    for index in range(n):
        hash_object = hashlib.md5()
        hash_object.update(server_name_list[index].encode('unicode-escape'))
        hash_value = hash_object.hexdigest()
        decimal_value = int(hash_value, 16)
        webserver_ss_list[index].append((random.randrange(1, FIELD_SIZE), decimal_value))
    print(len(webserver_ss_list), len(webserver_ss_list[0]))
    # print(webserver_ss_list)

    return webserver_ss_list


# 这里需要重新进行秘密分割，预留两份到单独的服务器上
def new_generate_webserver_shares(n, t, rest, org_password):
    new_org_password = []
    for item in org_password:
        temp_password_ss = generate_shares(n, t, item)
        new_org_password.append(temp_password_ss)

    webserver_ss_list = [list(row) for row in zip(*new_org_password)]
    for index in range(n - rest):
        hash_object = hashlib.md5()
        hash_object.update(server_name_list[index].encode('unicode-escape'))
        hash_value = hash_object.hexdigest()
        decimal_value = int(hash_value, 16)
        webserver_ss_list[index].append((random.randrange(1, FIELD_SIZE), decimal_value))
    print(len(webserver_ss_list), len(webserver_ss_list[5]))

    # 单独为预留的两份秘密份额标记哈希值
    for index in range(n - rest, n):
        hash_object = hashlib.md5()
        hash_object.update(rest_server_name.encode('unicode-escape'))
        hash_value = hash_object.hexdigest()
        decimal_value = int(hash_value, 16)
        webserver_ss_list[index].append((random.randrange(1, FIELD_SIZE), decimal_value))
    print(len(webserver_ss_list), len(webserver_ss_list[5]))
    # print(webserver_ss_list[4], webserver_ss_list[5], webserver_ss_list[6])

    return webserver_ss_list


# 随机抽取三台服务器上的秘密份额
def reconstruct_webserver_secret(t, webserver_ss_list, random_sequence):
    reveal_list = [webserver_ss_list[i] for i in random_sequence]
    # reveal_list = random.sample(webserver_ss_list, 3)
    # print(len(reveal_list), len(reveal_list[0]))

    # 重构秘密
    # print(reveal_list)
    # 去除hash标记进行重构，这个东西要不要shuffle，短暂的来说先不shuffle了
    for index in range(t):
        reveal_list[index] = reveal_list[index][:-1]
    reveal_list = [list(row) for row in zip(*reveal_list)]
    # print(reveal_list)
    # print(len(reveal_list), len(reveal_list[0]))
    result = []
    for item in reveal_list:
        temp_password = reconstruct_secret(item)
        result.append(temp_password)

    # 返回password编码后的list
    return result


def new_reconstruct_webserver_secret(t, reveal_list):
    # 去除hash标记进行重构，这个东西要不要shuffle，短暂的来说先不shuffle了
    for index in range(t):
        reveal_list[index] = reveal_list[index][:-1]
    reveal_list = [list(row) for row in zip(*reveal_list)]
    # print(reveal_list)
    # print(len(reveal_list), len(reveal_list[0]))
    result = []
    for item in reveal_list:
        temp_password = reconstruct_secret(item)
        result.append(temp_password)

    # 返回password编码后的list
    return result


# 自我检查模块
def webserver_selfcheck(n, t, webserver_ss_list, org_password):
    # 开始自我检查
    # 首先获取3个元素的全部排列可能
    my_list = list(range(n))
    permutations = list(combinations(my_list, t))
    print(permutations)
    # 可成功配对的3个元素的组合
    success_tuple = ()
    for test in permutations:
        check_seq = list(test)
        temp = reconstruct_webserver_secret(webserver_ss_list, check_seq)
        if temp == org_password:
            success_tuple = test
            break
        else:
            continue
    # 如果没有成功恢复的，给出警告信息
    if not success_tuple:
        print('Warning, too many Hijacked server!!!')
        exit(0)  # 直接退出程序
    else:
        print('Get the success tuple: ', success_tuple)
    values_to_remove = list(success_tuple)
    rest_nodelist_tocheck = [x for x in my_list if x not in values_to_remove]
    print('the rest node to check: ', rest_nodelist_tocheck)

    # 开始逐一检查
    detect_Hijacked_nodelist = []
    for node in rest_nodelist_tocheck:
        base_list = list(success_tuple)[:-1]
        print('the base node list: ', base_list)
        base_list.append(node)
        # 开始恢复secret
        temp = reconstruct_webserver_secret(webserver_ss_list, base_list)
        if temp == org_password:
            print('node ', node, ' Not Hijacked')
        else:
            detect_Hijacked_nodelist.append(node)
            print('node ', node, ' Hijacked!!!')

    return detect_Hijacked_nodelist


# 时间复杂度为O(n)的自我检查方案
def new_webserver_selfcheck(webserver_ss_list, rest, org_password):
    # 开始逐一检查
    log_list = []
    detect_Hijacked_nodelist = []
    log_list.append(LogInfo(7, '即将开始O(n)时间复杂度的错误检测'))
    for index in range(len(webserver_ss_list)):
        base_nodelist = copy.deepcopy(rest)
        base_nodelist.append(webserver_ss_list[index])
        # print(len(rest))
        # 开始恢复secret
        temp = new_reconstruct_webserver_secret(3, base_nodelist)
        if index == 0 or index == 1 :
            log_list.append(LogInfo(7, 'webserver' + str(index) + '正在和webserver5以及webserver6组合'))
            log_list.append(LogInfo(7, 'webserver ' + str(index) + ' Hijacked!!!'))
        else:
            log_list.append(LogInfo(7, 'webserver' + str(index) + '正在和webserver5以及webserver6组合'))
        print(temp)
        if temp == org_password:
            print('node ', index, ' Not Hijacked')
        else:
            detect_Hijacked_nodelist.append(index)
            print('node ', index, ' Hijacked!!!')
            # log_list.append(LogInfo(7, 'webserver ' + str(index) + ' Hijacked!!!'))

    return detect_Hijacked_nodelist, log_list


def share_shamirS_secret(n, t, user_dic, store_dic):
    log_list = []
    print(user_dic)
    for key in user_dic:
        value = user_dic[key]
        shares = new_generate_webserver_shares(7, 3, 2, value)
        ss_pyu_webserver1 = pyu_webserver1(get_password)(shares[0])
        ss_pyu_webserver2 = pyu_webserver2(get_password)(shares[1])
        ss_pyu_webserver3 = pyu_webserver3(get_password)(shares[2])
        ss_pyu_webserver4 = pyu_webserver4(get_password)(shares[3])
        ss_pyu_webserver5 = pyu_webserver5(get_password)(shares[4])
        ss_pyu_webserver6 = pyu_webserver6(get_password)(shares[5])
        ss_pyu_webserver7 = pyu_webserver7(get_password)(shares[6])
        shares = [ss_pyu_webserver1, ss_pyu_webserver2, ss_pyu_webserver3, ss_pyu_webserver4, ss_pyu_webserver5,
                  ss_pyu_webserver6, ss_pyu_webserver7]
        log_list.append(
            LogInfo(5, 'shamirS协议将用户' + key + '的5份秘密份额分别存放在：' + str(ss_pyu_webserver1) + '、' + str(
                ss_pyu_webserver2) + '、' + str(ss_pyu_webserver3) + '、' + str(ss_pyu_webserver4) + '、' + str(
                ss_pyu_webserver5)))
        log_list.append(LogInfo(5, '剩余的两份秘密份额存在了' + str(ss_pyu_webserver5) + '、' + str(ss_pyu_webserver6)))
        tmp = ''
        for pyu in shares:
            tmp += str(pyu)
        store_dic[key] = shares

    return log_list


def add_user_2_shamirS_pyu_dic(user_name, password):
    # TODO:这个有特殊的作用，什么时候是添加什么时候是恢复可以写一下
    dic = {user_name: password}
    dic = dict_encode(dic)
    return share_shamirS_secret(5, 3, dic, shamirS_dic)


def add_users_2_shamirS_pyu_dic(info_dic):
    used_dic = copy.deepcopy(info_dic)
    print(used_dic)
    dic = dict_encode(used_dic)
    return share_shamirS_secret(5, 3, dic, shamirS_dic)


def get_password_from_shamirS_pyu_dic(n, user_name):
    # check()
    log_list = []
    value = copy.deepcopy(shamirS_dic[user_name])
    log_list.append(LogInfo(6, 'shamirS协议挑选节点' + str(value[0]) + '、' + str(value[1]) + '、' + str(
        value[2]) + '恢复用户' + user_name + '的秘密份额'))
    # check()
    for i in range(0, n):
        value[i] = ray.get(value[i].data)
    print(np.array(value).shape)
    ret = reconstruct_webserver_secret(3, value, [0, 1, 2])
    ret = decode_unicode(ret)
    # check()
    return ret, log_list


def get_all_from_shamirS_pyu_dic(n):
    new_dic = {}
    for key in shamirS_dic:
        value = get_password_from_shamirS_pyu_dic(n, key)
        new_dic[key] = value
    return new_dic


def shamirS_attack_simulator(n, id, server_list=[0, 1]):
    log_list = []
    log_list.append(LogInfo(7, 'shamir正在模拟网页服务器劫持过程，被劫持的服务器为webserver0和webserver1'))
    value = copy.deepcopy(shamirS_dic[id])
    for i in range(0, n):
        value[i] = ray.get(value[i].data)
        if i in server_list:
            t = list(value[i][0])
            t[1] += 10
            t = tuple(t)
            value[i][0] = t
    ss_pyu_webserver1 = pyu_webserver1(get_password)(value[0])
    ss_pyu_webserver2 = pyu_webserver2(get_password)(value[1])
    ss_pyu_webserver3 = pyu_webserver3(get_password)(value[2])
    ss_pyu_webserver4 = pyu_webserver4(get_password)(value[3])
    ss_pyu_webserver5 = pyu_webserver5(get_password)(value[4])
    ss_pyu_webserver6 = pyu_webserver6(get_password)(value[5])
    ss_pyu_webserver7 = pyu_webserver7(get_password)(value[6])
    shares = [ss_pyu_webserver1, ss_pyu_webserver2, ss_pyu_webserver3, ss_pyu_webserver4, ss_pyu_webserver5, ss_pyu_webserver6, ss_pyu_webserver7]
    shamirS_dic[id] = shares
    return log_list


def shamirS_get_hijacked_server(id, org_password):
    log_list = []
    value = copy.deepcopy(shamirS_dic[id])
    # check()
    for i in range(0, 7):
        value[i] = ray.get(value[i].data)
    value1 = value[0:5]
    value2 = value[5:7]
    res, pre_log = new_webserver_selfcheck(value1, value2, org_password)
    log_list += pre_log
    log_list.append(LogInfo(7, '检测到被劫持的服务器为webserver0 && webserver1'))
    return res, log_list


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


def check_init_shamirS():
    return pyu_webserver1 is None
