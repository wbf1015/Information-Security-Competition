from .ABY3 import *
from .cheetah import *
from user.views import append_to_loglist
from .sfLog import *


def Init_pro(name):
    if name == 'ABY3':
        append_to_loglist(LogInfo(100, '即将开始初始化ABY3（用户-浏览器-可信第三方阶段）'))
        log_list = init_ABY3()
        store_logs(log_list)
    else:
        append_to_loglist(LogInfo(100, '即将开始初始化cheetah（用户-浏览器-可信第三方阶段）'))
        log_list = init_cheetah()
        store_logs(log_list)


def Init_info(name, info_dic):
    if name == 'ABY3':
        log_list = add_users_2_aby3_spu_dic(info_dic)
        store_logs(log_list)
    else:
        log_list = add_users_2_cheetah_spu_dic(info_dic)
        store_logs(log_list)


def stage1_add_user(name, id, password):
    if name == 'ABY3':
        append_to_loglist(LogInfo(100, '正在通过ABY3协议增加用户'))
        log_list = add_user_2_aby3_spu_dic(id, password)
        store_logs(log_list)
    else:
        append_to_loglist(LogInfo(100, '正在通过cheetah协议增加用户'))
        log_list = add_user_2_cheetah_spu_dic(id, password)
        store_logs(log_list)


def stage1_get_password(name, id):
    if name == 'ABY3':
        append_to_loglist(LogInfo(100, '正在尝试通过ABY3协议获取密码'))
        password, log_list = get_password_from_aby3_spu_dic(id)
        log_list.append(LogInfo(100, str(name)+'协议恢复用户'+str(id)+'密码为'+str(password)))
        store_logs(log_list)
        return password
    else:
        append_to_loglist(LogInfo(100, '正在通过cheetah协议比对密码'))
        password, log_list = get_password_from_cheetah_spu_dic(id)
        log_list.append(LogInfo(100, str(name) + '协议恢复用户' + str(id) + '密码为' + str(password)))
        store_logs(log_list)
        return password


def stage1_change_pro(now_pro, info_dic):
    info_dic = get_precious_user(now_pro, info_dic)
    if now_pro == 'ABY3':
        append_to_loglist(LogInfo(100, '即将更改第一阶段协议为cheetah'))
        Init_pro('cheetah')
        Init_info('cheetah', info_dic)
    else:
        append_to_loglist(LogInfo(100, '即将更改第一阶段协议为ABY3'))
        Init_pro('ABY3')
        Init_info('ABY3', info_dic)


def check_init(pro_name):
    if pro_name == 'ABY3':
        return aby3_config is None
    else:
        return cheetah_config is None


def get_stage1_all_users(pro_name):
    if pro_name == 'ABY3':
        return get_all_from_aby3_spu_dic()
    else:
        return get_all_from_cheetah_spu_dic()


def erase_stage1_users(pro_name, stu_name):
    if pro_name == 'ABY3':
        log_list = erase_user_from_aby3_spu_dic(stu_name)
        store_logs(log_list)
    else:
        log_list = erase_user_from_cheetah_spu_dic(stu_name)
        store_logs(log_list)

def get_precious_user(now_pro, info_dic):
    precious_user = get_stage1_all_users(now_pro)
    ret_dic = {}
    for users in precious_user:
        ret_dic[users] = info_dic[users]
    return ret_dic


def store_logs(log_list):
    for log in log_list:
        append_to_loglist(log)
