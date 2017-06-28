# -*- coding: utf-8 -*-

import random
import time

from .. import gvars
from .. import config


class UserService:
    def __init__(self):
        print('__init__::UserService')

    def get_all_users_in_db(self, admin_id):
        print('UserService::get_all_users_in_db')
        sql = 'select * from t_user where _admin_id = %d;' % admin_id
        rs = gvars.sql_helper.query(sql)
        # if // rs 会不会是空？
        user_list = []
        if len(rs) > 0:
            for o in rs:
                item = {}
                item['id'] = o[0]
                item['fx_acc'] = o[1]
                item['remark_id'] = o[2]
                item['admin_id'] = o[3]
                item['is_subscriber'] = o[4]
                item['is_exit'] = o[5]
                user_list.append(item)
        return user_list

    def get_all_user_ids_in_db(self, admin_id):
        print('UserService::get_all_user_ids_in_db')
        sql = 'select _id from t_user where _admin_id =%d;'
        rs = gvars.sql_helper.query(sql % admin_id)
        id_list = []
        if len(rs) > 0:
            for item in rs:
                id_list.append(item[0])
        return id_list

    # 每次启动本软件的时候，检查是否有新好友
    # 更新RAM中的好友列表，更新数据库中的好友列表
    def update_contact(self):
        print('UserService::update_contact')

        self.update_friend_in_RAM()

        # 处理还没有处理备注的好友
        max_remark_id = 0  # 当前好友的最大编号
        if len(gvars.frd_r2u_fx) > 0:
            assert max([int(r[9:]) for r in gvars.frd_r2u_fx.keys()]) == len(gvars.frd_r2u_fx)
            max_remark_id = len(gvars.frd_r2u_fx)

        new_username_l = list(set(list(gvars.frd_u2r.keys())) \
                              - set(list(gvars.frd_u2r_fx.keys())))

        for username in new_username_l:
            alias_res = gvars.itchat.set_alias(
                username, config.REMARK_PREFIX + str(max_remark_id + 1))
            if '请求成功' == alias_res['BaseResponse']['ErrMsg']:
                print('备注修改成功')
                # 加入数据库
                self.add_user_into_db(max_remark_id + 1)
                max_remark_id += 1
            else:
                print('备注修改失败')
            time.sleep(int(round(random.uniform(2, 15))))

        self.update_friend_in_RAM()
        # 如果gvars.frd_r2u_fx.keys()有不存在与数据库中的id，插入数据库
        user_id_in_db = self.get_all_user_ids_in_db(config.ADMIN_ID)
        user_rname_in_db = set()
        for uid in user_id_in_db:
            if uid in gvars.frd_dbid2r.keys():
                user_rname_in_db.add(gvars.frd_dbid2r[uid])
        new_rname_to_add = set(gvars.frd_r2u_fx.keys()) - user_rname_in_db
        for rname in new_rname_to_add:
            rid = int(rname[9:])
            self.add_user_into_db(rid)

    # 添加好友
    def add_user_into_db(self, remark_id):
        try:
            # a. 用户表
            sql = "INSERT INTO t_user (_is_subscriber, _fx_acc," \
                  "_remark_id,_admin_id, _is_exit, _enter_datetime," \
                  "_exit_datetime) VALUES ('1','',%d,%d,'0',NOW(),NOW());"

            param = (remark_id, config.ADMIN_ID)
            gvars.sql_helper.cursor.execute(sql % param)

            # b. 得到主表最后一条记录的id
            user_id = gvars.sql_helper.get_max_id_in_tb('t_user')
            gvars.sub_serv.subscribe(user_id)

        except Exception as e:
            gvars.sql_helper.connect.rollback()  # 事务回滚
            print('UserService::add_user_into_db:事务处理失败', e)
        else:
            gvars.sql_helper.connect.commit()  # 事务提交
            print('UserService::add_user_into_db:事务处理成功')

    # 把新用户添加进数据库，同时设置备注名
    def __add_user_into_db_set_alias(self, user):
        print('UserService::__add_user_into_db_set_alias')
        sql = ("INSERT INTO t_user "
               "(_is_subscriber, _fx_acc, _is_exit, _enter_datetime, _exit_datetime) VALUES "
               "('1','','0',NOW(),NOW());")

        gvars.sql_helper.update(sql) # 1. 向数据库添加1名用户
        max_id = gvars.sql_helper.get_max_id_in_tb('t_user') # 2. 得到该用户的id
        user['remark_name'] = max_id
        gvars.sub_serv.subscribe(max_id) # 3. 订阅表中开启订阅模式

        # 4. 修改微信联系人的备注
        new_remark_name = config.REMARK_PREFIX + str(max_id)
        gvars.itchat.set_alias(user['user_name'], new_remark_name)
        print(user['user_name'], new_remark_name)

        return new_remark_name

    # 初始化所有备注
    def init_remark_name(self):
        init_ok = 1
        # 1. 得到现在微信中所有用户的备注
        gvars.friend_list = gvars.itchat.get_friends(update=True)[1:]
        for f in gvars.friend_list:
            if f['RemarkName'] == config.INIT_REMARK_NAME:
                continue
            user_name = f['UserName']
            print(user_name + '初始化备注')
            counter = 3
            while counter>0:
                alias_res = gvars.itchat.set_alias(user_name, config.INIT_REMARK_NAME)
                if '请求成功' == alias_res['BaseResponse']['ErrMsg']:
                    counter = -1
                    print('初始化备注成功')
                else:
                    counter -= 1
                    print('初始化备注失败,再重试%d次'%counter)
                time.sleep(int(round(random.uniform(2, 15))))
            if counter == 0:
                init_ok = 0
        return  init_ok

    # 从数据库中查询出当前订阅的所有用户
    def get_all_subscriber_ids(self):
        sql = "SELECT _id FROM t_user WHERE _is_subscriber = '1';"
        id_list = []
        rs = gvars.sql_helper.query(sql)
        if len(rs) > 0:
            for item in rs:
                id_list.append(item[0])
        return id_list

    # 收到别人的添加好友请求
    def receive_new_friend_request(self, msg):

        if gvars.auto_add_friend:  # 自动添加好友
            # 1. 微信本身添加该好友
            gvars.itchat.add_friend(**msg['Text'])  # 该操作会自动将新好友的消息录入，不需要重载通讯录
            # 2. 更新数据库中好友表，订阅表
            username = msg['RecommendInfo']['UserName']
            self.update_contact()
            # 3. 向好友发送welcome的消息
            gvars.itchat.send_msg(config.WELCOME_CONTENT, username)
        else:  # 手动添加好友
            pass

    def update_frd_dic_by_frd_list(self, friend_list):
        users_list = self.get_all_users_in_db(config.ADMIN_ID)
        frd_r2dbid = {}
        frd_dbid2r = {}
        frd_u2r_fx = {}  # 已经设置好备注的，有后缀fx
        frd_r2u_fx = {}
        frd_u2r = {}  # 所有微信好友
        frd_r2u = {}
        for f in friend_list:
            if f['RemarkName'].startswith(config.REMARK_PREFIX):
                frd_u2r_fx[f['UserName']] = f['RemarkName']
                frd_r2u_fx[f['RemarkName']] = f['UserName']
                if len(users_list) > 0:
                    for u in users_list:
                        if u['remark_id'] == int(f['RemarkName'][len(config.REMARK_PREFIX):]):
                            frd_r2dbid[f['RemarkName']] = u['id']

            frd_u2r[f['UserName']] = f['RemarkName']
            frd_r2u[f['RemarkName']] = f['UserName']

        for k, v in frd_r2dbid.items():
            frd_dbid2r[v] = k

        gvars.frd_r2u = frd_r2u
        gvars.frd_u2r = frd_u2r
        gvars.frd_r2u_fx = frd_r2u_fx
        gvars.frd_u2r_fx = frd_u2r_fx
        gvars.frd_r2dbid = frd_r2dbid
        gvars.frd_dbid2r = frd_dbid2r

    def update_friend_in_RAM(self):

        friend_list = gvars.itchat.get_friends(update=True)
        gvars.mix_friend_list = friend_list[1:]  # 含有 现有的 + 删除的
        gvars.me = {}
        gvars.me['user_name'] = friend_list[0]['UserName']
        gvars.friend_list = gvars.mix_friend_list  # 现在含有 现有的 + 删除的

        self.update_frd_dic_by_frd_list(gvars.friend_list)
