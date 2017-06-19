# -*- coding: utf-8 -*-


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

####################### 第一次运行，请执行下一行
# gvars.user_serv.init_remark_name()
######### 第一次运行#######################


gvars.user_serv.update_contact()

gvars.friend_list = itchat.get_friends(update=True)
# username和remarkname互转
gvars.frd_u2r = {}
gvars.frd_r2u = {}
for f in gvars.friend_list:
    gvars.frd_u2r[f['UserName']] = f['RemarkName']
    gvars.frd_r2u[f['RemarkName']] = f['UserName']

# 机器人自己
gvars.me = {}
gvars.me['user_name'] = gvars.friend_list[0]['UserName']

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
        pass

    # 机器人收到用户发送的消息
    else:
        print('收到消息' + msg['Text'])
        msg['sender_id'] = int(gvars.frd_u2r[sender_user_name][9:])  # 数据库中用户id
        msg['sender_username'] = msg['FromUserName']  # wx的username
        msg['req_time'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                        time.localtime(time.time()))
        gvars.msg_serv.receive_response(msg)
        # 查询出发送消息的人在数据库中的id
        print(msg)


# 收到添加好友请求
@itchat.msg_register(FRIENDS)
def add_friend(msg):
    gvars.msg_serv.receive_new_friend_request(msg)


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


# 开启多线程，每天早上8:00自动执行发送市场概况
threads = []
t1 = threading.Thread(target=itchat.run, args=())
threads.append(t1)
t1.start()

t2 = threading.Thread(target=send_daily_mkt_msg, args=())
threads.append(t2)
t2.start()



# msg1 = {'MsgId': '7841120077399435007',
#         'FromUserName': '@4536489c5528f727d7e130eea23041e7',
#         'ToUserName': '@e9f2f84ae2c1f6cbaffd4789d0d745bfbee84c37e7700a8002b778d3e3f90c5d',
#         'MsgType': 1, 'Content': '我', 'Status': 3,
#         'ImgStatus': 1, 'CreateTime': 1497021416, 'VoiceLength': 0,
#         'PlayLength': 0, 'FileName': '', 'FileSize': '',
#         'MediaId': '', 'Url': '', 'AppMsgType': 0,
#         'StatusNotifyCode': 0, 'StatusNotifyUserName': '',
#         'RecommendInfo': {'UserName': '', 'NickName': '', 'QQNum': 0, 'Province': '', 'City': '', 'Content': '', 'Signature': '', 'Alias': '', 'Scene': 0, 'VerifyFlag': 0, 'AttrStatus': 0, 'Sex': 0, 'Ticket': '', 'OpCode': 0}, 'ForwardFlag': 0, 'AppInfo': {'AppID': '', 'Type': 0}, 'HasProductId': 0, 'Ticket': '', 'ImgHeight': 0, 'ImgWidth': 0, 'SubMsgType': 0, 'NewMsgId': 7841120077399435007, 'OriContent': '', 'Type': 'Text', 'Text': '我'}
