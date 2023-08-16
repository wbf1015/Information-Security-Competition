from manager.db_operation import user as sf_user
import time as t

LOG_ERR = 0
LOG_OK = 1


# 记录日志
def sys_log(msg, type):
    # 高亮打印当前时间和信息
    now = t.strftime("%Y-%m-%d %H:%M:%S", t.localtime())
    if type == LOG_ERR:
        print("\033[1;31m LOG_ERR:" + now + ": " + msg + "\033[0m")
    else:
        print("\033[1;32m LOG:" + now + ": " + msg + "\033[0m")


# 从数据库中得到所有的用户名和密码
def get_all_student_user():
    students, _ = sf_user.get_all_students()
    ret_dic = {}
    for student in students:
        msg = 'find stu_user:' + student.name + 'password:' + student.password
        sys_log(msg, 1)
        ret_dic[str(student.phone)] = str(student.password)

    return ret_dic


# 更改协议为ABY3或是cheetah
def change_Protocol(now):
    if now == 'ABY3':
        return 'cheetah'

    return 'ABY3'


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
