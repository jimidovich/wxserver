# -*- coding: utf-8 -*-

import random
import datetime
import sys
import threading
import time

import itchat
from itchat.content import *

sys.path.append('/home/yiju/wxfx/wxserver/')
import src.fx_service.msg_service as msg_service
import src.fx_service.subsriber_service as subscriber_service
import src.fx_service.tech_db_service as tech_service
import src.fx_service.user_service as user_service
import src.params.Parameters as parameters
from src.utils import sql_helper
import src.main.gvars as gvars
sys.path.append(parameters.APP_DIR)

# itchat.auto_login(False)
itchat.auto_login(True)


# 定义跨模块全局变量
gvars.sql_helper = sql_helper.SqlHelper()
gvars.itchat = itchat
gvars.sub_serv = subscriber_service.SubscriberService()
gvars.user_serv = user_service.UserService()

########### 第一次运行，请执行下一行
# gvars.user_serv.init_remark_name()
######### 第一次运行#######################
gvars.user_serv.update_contact()
gvars.tech_db_serv = tech_service.TechDbService()
gvars.fx_dic = gvars.tech_db_serv.get_fx_dic()
gvars.msg_serv = msg_service.MsgService()

@itchat.msg_register(itchat.content.TEXT)
def request_response(msg):
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
        elif 'set rname begin' == req_content:
            print('开启手动设置备注模式')
            gvars.auto_add_friend = False
            max_remark_id = 0  # 当前好友的最大编号
            if len(gvars.frd_r2u_fx) > 0:
                max_remark_id = int(max(gvars.frd_r2u_fx.keys())[9:])
            reply_content = '新备注应该从%s开始' % \
                            (parameters.REMARK_PREFIX + str(max_remark_id + 1))
            print(reply_content)
            # 自己收不到自己发的消息...
            # gvars.itchat.send(reply_content,toUserName=sender_user_name)
            gvars.itchat.send(reply_content, toUserName='filehelper')
        elif 'set rname over' == req_content:
            print('手动设置备注完毕')
            old_remark_id_set = set(list(gvars.frd_r2u_fx.keys()))
            gvars.user_serv.update_contact()
            new_remark_id_set = set(list(gvars.frd_r2u_fx.keys())) \
                                - old_remark_id_set

            # 1. 检查前缀是否错误
            # 2. 检查是否重复
            # 3. 检查是否是从rid_max+1号开始编号的
            if len(new_remark_id_set) > 0:
                for remark_name in new_remark_id_set:
                    r_id = int(remark_name[9:])
                    gvars.user_serv.add_user_into_db(r_id)

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


def send_daily_mkt_msg():
    sched_time = parameters.SCHED_TIME
    started = 0
    while 1:
        if 0 == started:
            # str(datetime.datetime.now())[0:19]
            now_str = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            # print(sched_time, ' ', now_str)
            if now_str == sched_time:
                started = 1
                # print('T=5s, exec...', now_str)
                gvars.msg_serv.send_mkt_msg_to_subscirbers()
                time.sleep(24 * 60 * 60)
                # time.sleep(10)
            else:
                # print('sleep 1s')
                time.sleep(1)
        else:
            now_str = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            # print('T=5s, exec...', now_str)
            gvars.msg_serv.send_mkt_msg_to_subscirbers()
            time.sleep(24 * 60 * 60)
            # time.sleep(10)


# 更新好友列表
def update_contact_schedule_task():
    while 1:
        time.sleep(60 * 60)
        print('更新通讯录')
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



# msg1 = {'MsgId': '7841120077399435007',
#         'FromUserName': '@4536489c5528f727d7e130eea23041e7',
#         'ToUserName': '@e9f2f84ae2c1f6cbaffd4789d0d745bfbee84c37e7700a8002b778d3e3f90c5d',
#         'MsgType': 1, 'Content': '我', 'Status': 3,
#         'ImgStatus': 1, 'CreateTime': 1497021416, 'VoiceLength': 0,
#         'PlayLength': 0, 'FileName': '', 'FileSize': '',
#         'MediaId': '', 'Url': '', 'AppMsgType': 0,
#         'StatusNotifyCode': 0, 'StatusNotifyUserName': '',
#         'RecommendInfo': {'UserName': '', 'NickName': '', 'QQNum': 0, 'Province': '', 'City': '', 'Content': '', 'Signature': '', 'Alias': '', 'Scene': 0, 'VerifyFlag': 0, 'AttrStatus': 0, 'Sex': 0, 'Ticket': '', 'OpCode': 0}, 'ForwardFlag': 0, 'AppInfo': {'AppID': '', 'Type': 0}, 'HasProductId': 0, 'Ticket': '', 'ImgHeight': 0, 'ImgWidth': 0, 'SubMsgType': 0, 'NewMsgId': 7841120077399435007, 'OriContent': '', 'Type': 'Text', 'Text': '我'}
