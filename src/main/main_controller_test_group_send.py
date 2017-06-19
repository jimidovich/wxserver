# -*- coding: utf-8 -*-


import sys

import itchat

import src.fx_service.user_service as user_service
from src.glob import glob
from src.utils import sql_helper
import src.main.gvars as gvars

# sys.path.append(parameters.APP_DIR)
sys.path.append('F:/source_files/quant/wechat/dev/src')
# itchat.auto_login(False)
# itchat.auto_login(True)

# glob.__init__()  # 先必须在主模块初始化（只在Main模块需要一次即可）

sql_helper = sql_helper.SqlHelper()

# 定义跨模块全局变量
# glob.set_value('sql_helper', sql_helper)
# glob.set_value('itchat', itchat)
gvars.sql_helper = sql_helper
gvars.itchat = itchat

# sub_serv = subscriber_service.SubscriberService()
# glob.set_value('sub_serv',sub_serv)
#
user_serv = user_service.UserService()
# glob.set_value('user_serv',user_serv)


####################### 第一次运行，请运行下一行
# user_serv.init_remark_name()
######### 第一次运行

# user_serv.update_contact()

# friend_list = itchat.get_friends(update=True)
# # username和remarkname互转
# frd_u2r = {}
# frd_r2u = {}
# for f in friend_list:
#     frd_u2r[f['UserName']] = f['RemarkName']
#     frd_r2u[f['RemarkName']] = f['UserName']
#
# # 机器人自己
# me = {}
# me['user_name'] = friend_list[0]['UserName']
#
# frd_dic = {}
# frd_dic['u2r'] = frd_u2r # userName2remarkName
# frd_dic['r2u'] = frd_r2u
#
# glob.set_value('friend_list',friend_list)
# glob.set_value('frd_dic',frd_dic)
# glob.set_value('me',me)

#
# tech_db_serv = tech_service.TechDbService()
# glob.set_value('tech_db_serv',tech_db_serv)
#
# fx_dic = tech_db_serv.get_fx_dic()
# glob.set_value('fx_dic',fx_dic)
#
# msg_serv = msg_service.MsgService()
# glob.set_value('msg_serv',msg_serv)

#
# @itchat.msg_register(itchat.content.TEXT)
# def request_response(msg):
#
#     # 目前只允许客户发送文本消息
#     msg['req_content'] = msg['Text']
#     sender_user_name = msg['FromUserName']
#
#     # 有人在用机器人的微信号主动向用户发消息
#     if me['user_name'] == sender_user_name:
#         pass
#
#     # 机器人收到用户发送的消息
#     else:
#         print('收到消息' + msg['Text'])
#         msg['sender_id'] = int(frd_dic['u2r'][sender_user_name][9:]) # 数据库中用户id
#         msg['sender_username'] = msg['FromUserName'] # wx的username
#         msg['req_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
#         msg_serv.receive_response(msg)
#         # 查询出发送消息的人在数据库中的id
#         print(msg)
#
#
# # 收到添加好友请求
# @itchat.msg_register(FRIENDS)
# def add_friend(msg):
#     msg_serv.receive_new_friend_request(msg)


# 应该是开启多线程


# itchat.run()


# m_list = get_daily_mkt_list()
# tech_db_serv.add_daily_mkt(m_list)

# msg_serv.send_mkt_msg_to_subscirbers()

# m = tech_db_serv.get_last_daily_mkt_img_url()
# print(m)

# msg1 = {'MsgId': '7841120077399435007',
#         'FromUserName': '@4536489c5528f727d7e130eea23041e7',
#         'ToUserName': '@e9f2f84ae2c1f6cbaffd4789d0d745bfbee84c37e7700a8002b778d3e3f90c5d',
#         'MsgType': 1, 'Content': '我', 'Status': 3,
#         'ImgStatus': 1, 'CreateTime': 1497021416, 'VoiceLength': 0,
#         'PlayLength': 0, 'FileName': '', 'FileSize': '',
#         'MediaId': '', 'Url': '', 'AppMsgType': 0,
#         'StatusNotifyCode': 0, 'StatusNotifyUserName': '',
#         'RecommendInfo': {'UserName': '', 'NickName': '', 'QQNum': 0, 'Province': '', 'City': '', 'Content': '', 'Signature': '', 'Alias': '', 'Scene': 0, 'VerifyFlag': 0, 'AttrStatus': 0, 'Sex': 0, 'Ticket': '', 'OpCode': 0}, 'ForwardFlag': 0, 'AppInfo': {'AppID': '', 'Type': 0}, 'HasProductId': 0, 'Ticket': '', 'ImgHeight': 0, 'ImgWidth': 0, 'SubMsgType': 0, 'NewMsgId': 7841120077399435007, 'OriContent': '', 'Type': 'Text', 'Text': '我'}
