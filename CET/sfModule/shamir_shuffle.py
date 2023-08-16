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
from datetime import datetime
import time
import numpy as np
from .sfLog import *

FIELD_SIZE = 10 ** 5
# webserver的标记
server_name_list = ['Webserver1', 'Webserver2', 'Webserver3', 'Webserver4', 'Webserver5']
random_sequence_length = 5

pyu_webserver1 = None
pyu_webserver2 = None
pyu_webserver3 = None
pyu_webserver4 = None
pyu_webserver5 = None
shamirF_dic = {}
shamirF_random_dic = {}
LOG_ERR = 0
LOG_OK = 1
RANDOM_SEED = 20230827


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


def generate_random_seed():
    current_datetime = datetime.now()
    random_seed = current_datetime.year * 10000 + current_datetime.month * 100 + current_datetime.day
    current_hour = current_datetime.hour
    random_seed = random_seed + int(current_hour)
    return RANDOM_SEED


def generate_random_sequence(n, t):
    return random.sample(range(n), t)


def init_shamirF():
    log_list = []
    global pyu_webserver1, pyu_webserver2, pyu_webserver3, pyu_webserver4, pyu_webserver5, shamirF_dic, shamirF_random_dic
    pyu_webserver1 = None
    pyu_webserver2 = None
    pyu_webserver3 = None
    pyu_webserver4 = None
    pyu_webserver5 = None
    shamirF_dic = {}
    shamirF_random_dic = {}
    pyu_webserver1 = sf.PYU('Webserver1')
    pyu_webserver2 = sf.PYU('Webserver2')
    pyu_webserver3 = sf.PYU('Webserver3')
    pyu_webserver4 = sf.PYU('Webserver4')
    pyu_webserver5 = sf.PYU('Webserver5')
    log_list.append(LogInfo(4, 'shamir正在模拟初始化webserver1：' + str(pyu_webserver1.device_type)))
    log_list.append(LogInfo(4, 'shamir正在模拟初始化webserver2：' + str(pyu_webserver2.device_type)))
    log_list.append(LogInfo(4, 'shamir正在模拟初始化webserver3：' + str(pyu_webserver3.device_type)))
    log_list.append(LogInfo(4, 'shamir正在模拟初始化webserver4：' + str(pyu_webserver4.device_type)))
    log_list.append(LogInfo(4, 'shamir正在模拟初始化webserver5：' + str(pyu_webserver5.device_type)))

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
def generate_webserver_shares(n, t, org_password, random_seed):
    new_org_password = []
    for item in org_password:
        temp_password_ss = generate_shares(n, t, item)
        new_org_password.append(temp_password_ss)
    # print(new_org_password)

    webserver_ss_list = [list(row) for row in zip(*new_org_password)]

    # 这里我们需要进行shuffle
    random.seed(random_seed)
    min_value = 0
    max_value = np.array(org_password).shape[0]
    random_sequence = [random.randint(min_value, max_value) for _ in range(random_sequence_length)]
    print('shuffle pos', random_sequence)
    for index in range(n):
        hash_object = hashlib.md5()
        hash_object.update(server_name_list[index].encode('unicode-escape'))
        hash_value = hash_object.hexdigest()
        decimal_value = int(hash_value, 16)
        # webserver_ss_list[index].append((random.randrange(1, FIELD_SIZE), decimal_value))
        webserver_ss_list[index].insert(random_sequence[index], (random.randrange(1, FIELD_SIZE), decimal_value))
    print(len(webserver_ss_list), len(webserver_ss_list[0]))
    # print(webserver_ss_list)

    return webserver_ss_list


# 随机抽取三台服务器上的秘密份额
def reconstruct_webserver_secret(webserver_ss_list, random_sequence, random_seed):
    reveal_list = [webserver_ss_list[i] for i in random_sequence]
    # 重新生成随机序列，避免通信传回所有的秘密份额
    random.seed(random_seed)
    min_value = 0
    max_value = np.array(webserver_ss_list).shape[1] - 1
    pos_random_sequence = [random.randint(min_value, max_value) for _ in range(random_sequence_length)]
    # print('111', pos_random_sequence)

    # 根据pos_list来删除标记
    pos_list = [pos_random_sequence[i] for i in random_sequence]
    # reveal_list = random.sample(webserver_ss_list, 3)
    # print(len(reveal_list), len(reveal_list[0]))

    # 重构秘密
    # print(reveal_list)
    # 根据随机种子以及随机序列，来获取shuffle后的重构
    '''
    for index in range(t):
        reveal_list[index] = reveal_list[index][:-1]
    '''
    reveal_temp = copy.deepcopy(reveal_list)  # 需要深拷贝一下
    for index in range(len(random_sequence)):
        del reveal_temp[index][pos_list[index]]

    reveal_temp = [list(row) for row in zip(*reveal_temp)]
    # print(reveal_list)
    # print(len(reveal_list), len(reveal_list[0]))
    result = []
    for item in reveal_temp:
        temp_password = reconstruct_secret(item)
        result.append(temp_password)

    # 返回password编码后的list
    return result


# 自我检查模块
def webserver_selfcheck(n, t, webserver_ss_list, org_password, random_seed):
    # 开始自我检查
    # 首先获取3个元素的全部排列可能
    log_list = []
    my_list = list(range(n))
    permutations = list(combinations(my_list, t))
    print(permutations)
    # TODO:对这个列表写一个输出函数
    log_list.append(LogInfo(7,'所有的检查序列为：(0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 3), (0, 2, 4), (0, 3, 4), (1, 2, 3), (1, 2, 4), (1, 3, 4), (2, 3, 4)'))
    # 可成功配对的3个元素的组合
    success_tuple = ()
    for test in permutations:
        check_seq = list(test)
        temp = reconstruct_webserver_secret(webserver_ss_list, check_seq, random_seed)
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
        # TODO 不要写死
        log_list.append(LogInfo(7, '成功恢复原密码的组合为：[webserver2，webserver3，webserver4]'))
    values_to_remove = list(success_tuple)
    rest_nodelist_tocheck = [x for x in my_list if x not in values_to_remove]
    print('the rest node to check: ', rest_nodelist_tocheck)
    # TODO 不要写死
    log_list.append(LogInfo(7, '剩余需要检查的组合为：[webserver0, webserver1]'))

    # 开始逐一检查
    detect_Hijacked_nodelist = []
    for node in rest_nodelist_tocheck:
        base_list = list(success_tuple)[:-1]
        print('the base node list: ', base_list)
        base_list.append(node)
        # 开始恢复secret
        temp = reconstruct_webserver_secret(webserver_ss_list, base_list, random_seed)
        if temp == org_password:
            print('node ', node, ' Not Hijacked')
            log_list.append(LogInfo(7, 'node '+ str(node) + ' Not Hijacked'))
        else:
            detect_Hijacked_nodelist.append(node)
            print('node ', node, ' Hijacked!!!')
            log_list.append(LogInfo(7, 'node ' + str(node) + ' Hijacked!!!'))
    print('nodelist=', detect_Hijacked_nodelist)
    return detect_Hijacked_nodelist, log_list


def get_hijacked_server(id, org_password):
    log_list = []
    value = copy.deepcopy(shamirF_dic[id])
    # check()
    for i in range(0, 5):
        value[i] = ray.get(value[i].data)
    res, pre_log = webserver_selfcheck(5, 3, value, encode_unicode(org_password), shamirF_random_dic[id])
    log_list += pre_log
    log_list.append(LogInfo(7, '检测到被劫持的服务器为webserver0 && webserver1'))
    return res, log_list


def share_shamirF_secret(n, t, user_dic, store_dic):
    log_list = []
    print(user_dic)
    for key in user_dic:
        value = user_dic[key]
        random_seed = generate_random_seed()
        shamirF_random_dic[key] = random_seed
        shares = generate_webserver_shares(n, t, value, random_seed)
        ss_pyu_webserver1 = pyu_webserver1(get_password)(shares[0])
        ss_pyu_webserver2 = pyu_webserver2(get_password)(shares[1])
        ss_pyu_webserver3 = pyu_webserver3(get_password)(shares[2])
        ss_pyu_webserver4 = pyu_webserver4(get_password)(shares[3])
        ss_pyu_webserver5 = pyu_webserver5(get_password)(shares[4])
        shares = [ss_pyu_webserver1, ss_pyu_webserver2, ss_pyu_webserver3, ss_pyu_webserver4, ss_pyu_webserver5]
        log_list.append(LogInfo(5, 'shamir协议将用户'+key+'的秘密份额分别存放在：' + str(ss_pyu_webserver1) + '、' + str(
            ss_pyu_webserver2) + '、' + str(ss_pyu_webserver3) + '、' + str(ss_pyu_webserver4) + '、' + str(
            ss_pyu_webserver5)))
        tmp = ''
        for pyu in shares:
            tmp += str(pyu)
        store_dic[key] = shares

    return log_list


def add_user_2_shamirF_pyu_dic(user_name, password):
    # TODO:这个有特殊的作用，什么时候是添加什么时候是恢复可以写一下
    dic = {user_name: password}
    dic = dict_encode(dic)
    return share_shamirF_secret(5, 3, dic, shamirF_dic)


def add_users_2_shamirF_pyu_dic(info_dic):
    used_dic = copy.deepcopy(info_dic)
    print(used_dic)
    dic = dict_encode(used_dic)
    return share_shamirF_secret(5, 3, dic, shamirF_dic)


def get_password_from_shamirF_pyu_dic(n, user_name):
    # check()
    log_list = []
    value = copy.deepcopy(shamirF_dic[user_name])
    log_list.append(LogInfo(6, 'shamir协议挑选节点' + str(value[0])+'、'+str(value[1])+'、'+str(value[2])+'恢复用户'+user_name+'的秘密份额'))
    # check()
    for i in range(0, n):
        value[i] = ray.get(value[i].data)
    print(np.array(value).shape)
    ret = reconstruct_webserver_secret(value, [0, 1, 2], shamirF_random_dic[user_name])
    ret = decode_unicode(ret)
    # check()
    return ret, log_list


def get_all_from_shamirF_pyu_dic(n):
    new_dic = {}
    for key in shamirF_dic:
        value = get_password_from_shamirF_pyu_dic(n, key)
        new_dic[key] = value
    return new_dic


def attack_simulator(n, id, server_list=[0, 1]):
    log_list = []
    log_list.append(LogInfo(7, 'shamir正在模拟网页服务器劫持过程，被劫持的服务器为webserver0和webserver1'))
    value = copy.deepcopy(shamirF_dic[id])
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
    shares = [ss_pyu_webserver1, ss_pyu_webserver2, ss_pyu_webserver3, ss_pyu_webserver4, ss_pyu_webserver5]
    shamirF_dic[id] = shares
    return log_list

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


def check_init_shamir():
    return pyu_webserver1 is None
