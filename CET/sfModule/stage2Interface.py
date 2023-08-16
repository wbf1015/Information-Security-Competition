from .ASS import *
from .semi2k import *
from .Brickell import *
from .shamir_shuffle import *
from user.views import append_to_loglist
from .sfLog import *


def Init_pro2(stage1_name, stage2_name):
    if stage2_name == 'ASS':
        append_to_loglist(LogInfo(100, '即将开始初始化ASS（网站服务器集群阶段）'))
        log_list = init_ASS()
        store_logs(log_list)
    if stage2_name == 'semi2k':
        append_to_loglist(LogInfo(100, '即将开始初始化SEMI2K（网站服务器集群阶段）'))
        log_list = init_SEMI2K()
        store_logs(log_list)
    if stage2_name == 'Brickell':
        append_to_loglist(LogInfo(100, '即将开始初始化Brickell（网站服务器集群阶段）'))
        log_list = init_Brickell()
        store_logs(log_list)
    if stage2_name == 'shamirF':
        append_to_loglist(LogInfo(100, '即将开始初始化shamir（网站服务器集群阶段）'))
        log_list = init_shamirF()
        store_logs(log_list)


def Init_info2(name, info_dic):
    if name == 'ASS':
        log_info = add_users_2_ASS_pyu_dic(info_dic)
        store_logs(log_info)
    if name == 'semi2k':
        log_info = add_users_2_semi2k_spu_dic(info_dic)
        store_logs(log_info)
    if name == 'Brickell':
        log_info = add_users_2_Brickell_pyu_dic(info_dic)
        store_logs(log_info)
    if name == 'shamirF':
        log_info = add_users_2_shamirF_pyu_dic(info_dic)
        store_logs(log_info)


def stage2_add_user(name, id, password):
    if name == 'ASS':
        append_to_loglist(LogInfo(100, '正在通过ASS协议增加用户'))
        log_info = add_user_2_ASS_pyu_dic(id, password)
        store_logs(log_info)
    if name == 'semi2k':
        append_to_loglist(LogInfo(100, '正在通过semi2k协议增加用户'))
        log_info = add_user_2_ASS_pyu_dic(id, password)
        store_logs(log_info)
    if name == 'Brickell':
        append_to_loglist(LogInfo(100, '正在通过Brickell协议增加用户'))
        log_info = add_user_2_Brickell_pyu_dic(id, password)
        store_logs(log_info)
    if name == 'shamirF':
        append_to_loglist(LogInfo(100, '正在通过shamir协议增加用户'))
        log_info = add_user_2_shamirF_pyu_dic(id, password)
        store_logs(log_info)


def stage2_get_password(name, id):
    if name == 'ASS':
        append_to_loglist(LogInfo(100, '正在尝试通过ASS协议获取密码'))
        password, log_list = get_password_from_ASS_pyu_dic(5, id)
        store_logs(log_list)
        return password
    if name == 'semi2k':
        append_to_loglist(LogInfo(100, '正在尝试通过semi2k协议获取密码'))
        password, log_list = get_password_from_semi2k_spu_dic(id)
        store_logs(log_list)
        return password
    if name == 'Brickell':
        append_to_loglist(LogInfo(100, '正在尝试通过Brickell协议获取密码'))
        password, log_list = get_password_from_Brickell_pyu_dic(5, id)
        store_logs(log_list)
        return password
    if name == 'shamirF':
        append_to_loglist(LogInfo(100, '正在尝试通过shamir协议获取密码'))
        password, log_list = get_password_from_shamirF_pyu_dic(5, id)
        store_logs(log_list)
        return password


def stage2_change_pro(now_pro, next_pro, info_dic):
    if next_pro == 'ASS':
        append_to_loglist(LogInfo(100, '即将更改第二阶段协议为ASS'))
        log_list = init_ASS()
        store_logs(log_list)
        log_list = add_users_2_ASS_pyu_dic(info_dic)
        store_logs(log_list)

    if next_pro == 'semi2k':
        append_to_loglist(LogInfo(100, '即将更改第二阶段协议为semi2k'))
        log_list = init_SEMI2K()
        store_logs(log_list)
        log_list = add_users_2_semi2k_spu_dic(info_dic)
        store_logs(log_list)

    if next_pro == 'Brickell':
        append_to_loglist(LogInfo(100, '即将更改第二阶段协议为Brickell'))
        log_list = init_Brickell()
        store_logs(log_list)
        log_list = add_users_2_Brickell_pyu_dic(info_dic)
        store_logs(log_list)

    if next_pro == 'shamirF':
        append_to_loglist(LogInfo(100, '即将更改第二阶段协议为shamir'))
        log_list = init_shamirF()
        store_logs(log_list)
        log_list = add_users_2_shamirF_pyu_dic(info_dic)
        store_logs(log_list)


def check_init2(pro_name):
    if pro_name == 'ASS':
        return pyu_webserver1 is None
    if pro_name == 'semi2k':
        return spu_semi2k is None
    if pro_name == 'Brickell':
        return check_init()
    if pro_name == 'shamirF':
        return check_init_shamir()


def ASS_special(id):
    append_to_loglist(LogInfo(100, '即将刷新用户'+id+'的秘密份额'))
    log_list = refresh_user_ss(id)
    store_logs(log_list)


def shamir_special(id):
    append_to_loglist(LogInfo(100, '即将针对用户'+id+'进行攻击模拟'))
    log_list = attack_simulator(5, id)
    store_logs(log_list)

def shamir_special_check(id, org_password):
    append_to_loglist(LogInfo(100, '即将针对用户'+id+'进行服务器破坏检测'))
    server_list, log_list = get_hijacked_server(id, org_password)
    store_logs(log_list)
    return server_list


def store_logs(log_list):
    for log in log_list:
        append_to_loglist(log)
