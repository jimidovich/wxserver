# -*- coding: utf-8 -*-

import os
import datetime
import threading
import time
import sys

import itchat
from .fx_service import msg_service
from .fx_service import subscriber_service
from .fx_service import tech_db_service as tech_service
from .fx_service import user_service
from . import gvars
from . import parameters
parameters.DATABASE_NAME = parameters.db_names[sys.argv[1]]
if len(sys.argv) == 3:
    if sys.argv[2] == 'reset_all_remark':
        parameters.NEED_INIT_REMARK_NAME = True

from itchat.content import *
from .utils import sql_helper

itchat.auto_login(hotReload=False)
# itchat.auto_login(hotReload=True)

# 定义跨模块全局变量
gvars.sql_helper = sql_helper.SqlHelper()
gvars.itchat = itchat
gvars.sub_serv = subscriber_service.SubscriberService()
gvars.user_serv = user_service.UserService()

id_list = gvars.user_serv.get_all_user_ids_in_db(parameters.ADMIN_ID)
if len(id_list)==0:
    init_ok = gvars.user_serv.init_remark_name()
    if init_ok == 0:
        print('好友备注初始化未完成')
        os._exit(-1)

gvars.user_serv.update_contact()
gvars.tech_db_serv = tech_service.TechDbService()
gvars.fx_dic = gvars.tech_db_serv.get_fx_dic()
gvars.msg_serv = msg_service.MsgService()

@itchat.msg_register(itchat.content.TEXT)
def request_response(msg):
    print('got msg:', msg['Text'])
    # 目前只允许客户发送文本消息
    msg['req_content'] = msg['Text']
    sender_user_name = msg['FromUserName']

    # 有人在用机器人的微信号主动向用户发消息
    if gvars.me['user_name'] == sender_user_name:
        # 把自己发的消息当作是自己主动给用户发送消息的入口
        req_content = msg['Text']
        if 'all mkt' == req_content:
            print('向所有订阅用户发送市场消息')
            gvars.msg_serv.send_mkt_msg_to_subscirbers()
        elif 'all welcome' == req_content:
            print('向所有用户发送welcome')
            msg = {}
            msg['msg_type'] = parameters.SYS_MSG_TEXT
            msg['content'] = parameters.WELCOME_CONTENT
            gvars.msg_serv.send_msg_to_all_users(msg)
        elif 'all menu' == req_content:
            print('向所有用户发送菜单')
            msg = {}
            msg['msg_type'] = parameters.SYS_MSG_TEXT
            msg['content'] = parameters.MENU
            gvars.msg_serv.send_msg_to_all_users(msg)
        elif 'all h' == req_content:
            print('向所有用户发送帮助')
            msg = {}
            msg['msg_type'] = parameters.SYS_MSG_TEXT
            msg['content'] = parameters.HELP_MSG
            gvars.msg_serv.send_msg_to_all_users(msg)
        elif 'update friend' == req_content:
            print('立即更新用户信息')
            gvars.user_serv.update_contact()
        elif 'set rname begin' == req_content:
            print('开启手动设置备注模式')
            gvars.auto_add_friend = False
            max_remark_id = 0  # 当前好友的最大编号
            if len(gvars.frd_r2u_fx) > 0:
                max_remark_id = int(max(gvars.frd_r2u_fx.keys())[9:])
            reply_content = '新备注应该从%s开始' % \
                            (parameters.REMARK_PREFIX + str(max_remark_id + 1))
            print(reply_content)
            # 向文件助手发送。自己收不到自己的消息
            gvars.itchat.send(reply_content, toUserName='filehelper')
        elif 'set rname over' == req_content:
            print('手动设置备注完毕')
            # old_remark_id_set = set(list(gvars.frd_r2u_fx.keys()))
            gvars.user_serv.update_contact()
            # 还应该做的...
            # # 1. 检查前缀是否错误
            # # 2. 检查是否重复
            # # 3. 检查是否是从rid_max+1号开始编号的
            gvars.auto_add_friend = True
            gvars.itchat.send('手动添加备注成功！', toUserName='filehelper')

        else:
            if len(req_content) > 10:
                if 'all text ' == req_content[0:9]:
                    content = req_content[9:]
                    print('向所有用户发送文本消息:' + content)
                    msg = {}
                    msg['msg_type'] = parameters.SYS_MSG_TEXT
                    msg['content'] = content
                    gvars.msg_serv.send_msg_to_all_users(msg)

    # 收到用户发送的消息
    else:
        print('[收到消息] ' + msg['Text'])
        msg['remark_name'] = gvars.frd_u2r_fx[sender_user_name]
        msg['remark_id'] = int(msg['remark_name'][9:])  # 备注
        msg['sender_id_in_db'] = gvars.frd_r2dbid[msg['remark_name']]  # 数据库中用户id
        msg['sender_username'] = sender_user_name  # wx的username
        msg['req_time'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                        time.localtime(time.time()))
        gvars.msg_serv.receive_response(msg)

# 收到添加好友请求
@itchat.msg_register(FRIENDS)
def add_friend(msg):
    gvars.user_serv.receive_new_friend_request(msg)

# 推送每天的市场概况
def send_daily_mkt_msg():
    while 1:
        now = datetime.datetime.now()
        if now.weekday() in [5, 6]:  # 非工作日:
            pass
        else:  # 工作日
            now_str = now.strftime('%Y/%m/%d %H:%M:%S')[11:]
            # print(now_str)
            if now_str in parameters.SCHED_TIME_LIST:  # 发送
                gvars.msg_serv.send_mkt_msg_to_subscirbers()
        time.sleep(1)

# 更新好友列表
def update_contact_schedule_task():
    while 1:
        time.sleep(10 * 60)
        print('每隔10分钟更新一次通讯录')
        gvars.user_serv.update_contact()


# 开启多线程，每天早上8:00自动执行发送市场概况
threads = []
t1 = threading.Thread(target=itchat.run, args=())
threads.append(t1)
t1.start()

t2 = threading.Thread(target=send_daily_mkt_msg, args=())
threads.append(t2)
t2.start()

t3 = threading.Thread(target=update_contact_schedule_task, args=())
threads.append(t3)
t3.start()

