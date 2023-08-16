import numpy as np
import random
from itertools import combinations
import hashlib
import secretflow as sf
import spu
import ray
import time
import copy
from .sfLog import *

FIELD_SIZE = 10 ** 5
# webserver的标记
server_name_list = ['Webserver1', 'Webserver2', 'Webserver3', 'Webserver4', 'Webserver5']
# 预定的规则
rules = [(1, 5), (2, 3, 4)]
# 向量维度
vec_dim = 3
# 目标向量
target_vector = np.array([1, 0, 0])
t, n = 3, 5
reveal_sequence = [1, 2, 3]

pyu_webserver1 = None
pyu_webserver2 = None
pyu_webserver3 = None
pyu_webserver4 = None
pyu_webserver5 = None
Brickell_dic = {}
LOG_ERR = 0
LOG_OK = 1


# Brickell方案主要的难点就是生成向量
def gen_vector(rules):
    server_vector = np.zeros((len(server_name_list), vec_dim))
    low_value = -2
    high_value = 2
    for rule in rules:
        print(rule)
        if len(rule) == 2:
            temp_vector = []
            vector1 = np.random.randint(low_value, high_value, size=3)
            vector2 = np.array([1, 0, 0], dtype=int) - vector1
            print(vector1, vector2)
            temp_vector.append(vector1)
            temp_vector.append(vector2)
            for index in range(len(rule)):
                server_vector[rule[index] - 1] = temp_vector[index]
        if len(rule) == 3:
            temp_vector = []
            vector1 = np.random.randint(low_value, high_value, size=3)
            vector2 = np.random.randint(low_value, high_value, size=3)
            vector3 = np.array([1, 0, 0], dtype=int) - vector1 - vector2
            print(vector1, vector2, vector3)
            temp_vector.append(vector1)
            temp_vector.append(vector2)
            temp_vector.append(vector3)
            for index in range(len(rule)):
                server_vector[rule[index] - 1] = temp_vector[index]
        if len(rule) == 4:
            print('Please increase the vec dim!!!')
            return np.zeros((len(server_name_list), vec_dim))
        if len(rule) == 1 or len(rule) == 5:
            print('Error rules!!!')
            return np.zeros((len(server_name_list), vec_dim))

    return server_vector


webserver_vector = gen_vector(rules)
# 转换为int类型矩阵
webserver_vector = webserver_vector.astype(int)
print(webserver_vector)


def coeff(t, secret):
    coeff = [random.randrange(0, FIELD_SIZE) for _ in range(t - 1)]
    coeff.insert(0, secret)
    return coeff


# 这里我肯定是需要一个judge判断函数，将规则内与规则外分开判断
def vector_judge(rules, server_vector):
    num = len(server_name_list)
    number_list = list(range(1, num + 1))
    lengths = number_list[1:]
    # 这里获得所有可能的排列也就是规则
    combinations_list = []
    for length in lengths:
        combs = combinations(number_list, length)
        combinations_list.extend(list(combs))
    print(len(combinations_list))
    # print(combinations_list)

    # 单独把规则内和规则外隔开，此时的combination_list就是规则之外了
    for rule in rules:
        combinations_list.remove(rule)
    print(len(combinations_list))


def generate_shares(secret, server_vector):
    vec_coeff = coeff(t, secret)
    vec_coeff_mat = np.array(vec_coeff)
    shares = []
    for vec in server_vector:
        shares.append(np.dot(vec_coeff_mat, vec))

    return shares


# 重构秘密
def reconstruct_secret(serials, shares, server_vector):
    server_vector_reveal = server_vector[serials]
    reveal_vec = []
    for vec in server_vector_reveal:
        reveal_vec.append(vec)
    coeff_matrix = np.vstack(tuple(reveal_vec)).T
    # coefficients = np.linalg.solve(coeff_matrix, target_vector)
    coefficients = [1] * len(serials)
    # print(coefficients)

    selected_shares = [shares[i] for i in serials]

    return int(np.dot(coefficients, selected_shares))


# web部分的生成秘密份额
def generate_webserver_shares(org_password, webserver_vector=webserver_vector):
    new_org_password = []
    for item in org_password:
        temp_password_ss = generate_shares(item, webserver_vector)
        new_org_password.append(temp_password_ss)
    print(new_org_password)

    webserver_ss_list = [list(row) for row in zip(*new_org_password)]
    for index in range(len(server_name_list)):
        hash_object = hashlib.md5()
        hash_object.update(server_name_list[index].encode('unicode-escape'))
        hash_value = hash_object.hexdigest()
        decimal_value = int(hash_value, 16)
        # webserver_ss_list[index].append((random.randrange(1, FIELD_SIZE), decimal_value))
        webserver_ss_list[index].append(decimal_value)
    print(len(webserver_ss_list), len(webserver_ss_list[0]))
    # print(webserver_ss_list)

    return webserver_ss_list


# web部分重构秘密
def reconstruct_webserver_secret(webserver_ss_list, reveal_sequence=reveal_sequence, server_vector=webserver_vector):
    reveal_list = webserver_ss_list
    # reveal_list = [webserver_ss_list[i] for i in reveal_sequence]
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
        temp_password = reconstruct_secret(reveal_sequence, item, server_vector)
        result.append(temp_password)

    # 返回password编码后的list
    return result





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


def init_Brickell():
    log_list = []
    global pyu_webserver1, pyu_webserver2, pyu_webserver3, pyu_webserver4, pyu_webserver5
    pyu_webserver1 = None
    pyu_webserver2 = None
    pyu_webserver3 = None
    pyu_webserver4 = None
    pyu_webserver5 = None
    pyu_webserver1 = sf.PYU('Webserver1')
    pyu_webserver2 = sf.PYU('Webserver2')
    pyu_webserver3 = sf.PYU('Webserver3')
    pyu_webserver4 = sf.PYU('Webserver4')
    pyu_webserver5 = sf.PYU('Webserver5')
    Brickell_dic = {}
    log_list.append(LogInfo(4, 'Brickell正在模拟初始化webserver1：' + str(pyu_webserver1.device_type)))
    log_list.append(LogInfo(4, 'Brickell正在模拟初始化webserver2：' + str(pyu_webserver2.device_type)))
    log_list.append(LogInfo(4, 'Brickell正在模拟初始化webserver3：' + str(pyu_webserver3.device_type)))
    log_list.append(LogInfo(4, 'Brickell正在模拟初始化webserver4：' + str(pyu_webserver4.device_type)))
    log_list.append(LogInfo(4, 'Brickell正在模拟初始化webserver5：' + str(pyu_webserver5.device_type)))
    return log_list

def share_Brickell_secret(n, user_dic, store_dic):
    log_list = []
    for key in user_dic:
        value = user_dic[key]
        shares = generate_webserver_shares(value)
        ss_pyu_webserver1 = pyu_webserver1(get_password)(shares[0])
        ss_pyu_webserver2 = pyu_webserver2(get_password)(shares[1])
        ss_pyu_webserver3 = pyu_webserver3(get_password)(shares[2])
        ss_pyu_webserver4 = pyu_webserver4(get_password)(shares[3])
        ss_pyu_webserver5 = pyu_webserver5(get_password)(shares[4])
        shares = [ss_pyu_webserver1, ss_pyu_webserver2, ss_pyu_webserver3, ss_pyu_webserver4, ss_pyu_webserver5]
        tmp = ''
        for pyu in shares:
            tmp += str(pyu)
        log_list.append(LogInfo(5, 'Brickell将用户' + key + '的秘密份额分存于' + tmp))
        store_dic[key] = shares

    return log_list


def add_user_2_Brickell_pyu_dic(user_name, password):
    dic = {user_name: password}
    dic = dict_encode(dic)
    return share_Brickell_secret(5, dic, Brickell_dic)


def add_users_2_Brickell_pyu_dic(info_dic):
    used_dic = copy.deepcopy(info_dic)
    dic = dict_encode(used_dic)
    return share_Brickell_secret(5, dic, Brickell_dic)


def get_password_from_Brickell_pyu_dic(n, user_name):
    # check()
    log_list = []
    value = copy.deepcopy(Brickell_dic[user_name])
    # TODO 这里别写死了
    log_list.append(LogInfo(6,'Brickell可以选用的规则为【1，5】，【2，3，4】，向量维度为3'))
    log_list.append(LogInfo(6, '应用规则【1，5】，brickell使用秘密份额' + str(value[0]) + '、' + str(value[4]) + '恢复用户'+user_name+'的秘密'))
    # check()
    for i in range(0, n):
        value[i] = ray.get(value[i].data)
    ret = reconstruct_webserver_secret(value)
    ret = decode_unicode(ret)
    # check()
    return ret, log_list


def get_all_from_Brickell_pyu_dic(n):
    new_dic = {}
    for key in Brickell_dic:
        value = get_password_from_Brickell_pyu_dic(n, key)
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


def check_init():
    return pyu_webserver1 is None