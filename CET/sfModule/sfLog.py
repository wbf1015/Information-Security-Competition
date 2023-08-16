
'''
id=1 : 用户登录成功
id=2 ：用户登录失败
id=3 : 用户注册成功
id=4 : 协议的初始化
id=5 ： 拆分秘密份额
id=6 ： 恢复秘密份额
id=7 : 应用场景模拟
id=100
'''

class LogInfo:
    def __init__(self, id, msg):
        self.id=id
        self.msg = msg
