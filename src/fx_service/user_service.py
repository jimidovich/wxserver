# -*- coding: utf-8 -*-

import time

import src.fx_service.base_service as base_service
import src.params.Parameters as parameters
from src.glob import glob
import src.main.gvars as gvars


class UserService(base_service.BaseService):
    def __init__(self):
        print('__init__::UserService')
        base_service.BaseService.__init__(self)
        # self.sub_serv = glob.get_value('sub_serv')

    def get_all_users_in_db(self):
        print('UserService::get_all_users_in_db')
        sql = 'select * from t_user;'
        rs = gvars.sql_helper.query(sql)
        # if // rs 会不会是空？
        if len(rs) > 0:
            for item in rs:
                print(item)

    def get_all_user_ids_in_db(self):
        print('UserService::get_all_user_ids_in_db')
        sql = 'select _id from t_user;'
        rs = gvars.sql_helper.query(sql)
        id_list = []
        if len(rs) > 0:
            for item in rs:
                id_list.append(item[0])
                print(item[0])
        return id_list

    def get_all_remark_name_in_wx(self, friend_list):
        id_list = []
        wx_user_name_list = []
        for f in friend_list:
            remark_name = f['RemarkName']  # 对应t_user中的_id
            id_list.append(remark_name)
        return id_list

    # 每次启动本软件的时候，检查是否有新好友
    # 并把已经删除的好友的订阅状态设置为 '0'

    def update_contact(self):
        print('UserService::update_contact')

        # 1. 得到现在微信中所有用户的备注
        # 难道不能及时更新???????????????
        friend_list = gvars.itchat.get_friends(update=True)
        # 如果该用户的备注名不是以 _$fxuid$_ 开始，就加入数据库，并为其修改备注名
        for i in range(1, len(friend_list)):  # 排除自己

            f = friend_list[i]
            remark_name = f['RemarkName']
            print('原备注:' + remark_name)
            if parameters.REMARK_PREFIX != remark_name[0:9]:
                user = {}
                user['user_name'] = f['UserName']
                new_remark_name = self.__add_user_into_db_set_alias(user)
                print('新用户' + new_remark_name + '已添加')
                time.sleep(parameters.SET_REMARK_NAME_TIME_SLEEP_SECONDS)
            else:
                print('用户' + remark_name + '已存在')

    # 把新用户添加进数据库，同时设置备注名
    # 没有开启事务！！！！！！！ -_-!!
    def __add_user_into_db_set_alias(self, user):
        print('UserService::__add_user_into_db_set_alias')
        sql = "INSERT INTO t_user (_subscriber, _fx_acc,\
         _exit, _enter_datetime, _exit_datetime)\
        VALUES ('1','','0',NOW(),NOW());"
        # 1. 向数据库添加1名用户
        gvars.sql_helper.update(sql)

        # 如果同时 inserst 进去了怎么办??
        # 2. 得到该用户的id
        # 就算只有一个数据库，也要开串行执行!!
        # sql = "SELECT _id FROM t_user ORDER BY _id DESC LIMIT 0,1;"
        # max_id = gvars.sql_helper.query(sql)[0][0]
        max_id = gvars.sql_helper.get_max_id_in_tb('t_user')
        user['remark_name'] = max_id

        # 3. 订阅表中开启订阅模式
        gvars.sub_serv.subscribe(max_id)

        # 4. 修改微信联系人的备注
        new_remark_name = parameters.REMARK_PREFIX + str(max_id)
        gvars.itchat.set_alias(user['user_name'], new_remark_name)
        print(user['user_name'], new_remark_name)

        return new_remark_name

    def init_remark_name(self):
        # 1. 得到现在微信中所有用户的备注
        friend_list = gvars.itchat.get_friends(update=True)
        # 如果该用户的备注名不是以 _$fxuid$_ 开始，就加入数据库，并为其修改备注名
        for f in friend_list:
            user_name = f['UserName']
            print(user_name + '初始化备注')
            gvars.itchat.set_alias(user_name, parameters.INIT_REMARK_NAME)
            time.sleep(parameters.SET_REMARK_NAME_TIME_SLEEP_SECONDS)

    # 从数据库中查询出当前订阅的所有用户
    def get_all_subscriber_ids(self):
        sql = "SELECT _id FROM t_user WHERE _subscriber = '1';"
        id_list = []
        rs = gvars.sql_helper.query(sql)
        if len(rs) > 0:
            for item in rs:
                id_list.append(item[0])
        return id_list
