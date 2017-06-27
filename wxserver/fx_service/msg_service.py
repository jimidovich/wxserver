# -*- coding: utf-8 -*-

import os
import random
import shutil
import time
import uuid
from multiprocessing.dummy import Pool as ThreadPool

from wxserver import config
from .. import gvars


class MsgService:
    def __init__(self):
        self.fx_cmd_dic2 = gvars.tech_db_serv.get_fx_cmd_dic()
        self.fx_pair_cmd_set = self.get_fx_cmd_set()  # 获取外汇对的命令
        print('MsgService::init')

    # # 构造获取单个货币对技术指标的命令
    def get_fx_cmd_set(self):

        cmd_set = set()
        # 简写的货币对代号 e m
        l = list(self.fx_cmd_dic2.values())
        for o in l:
            for o2 in o:
                cmd_set.add(o2)

        # 完整的货币对代号 EURUSD M
        l2 = list(gvars.fx_dic.keys())
        freq_list = ['M', 'D', 'H']
        for o in l2:
            for o2 in freq_list:
                s = o + ' ' + o2
                cmd_set.add(s)

        # 更新gvars.fx_dic[xxx]的['cmd']
        for k, v in gvars.fx_dic.items():
            for f in freq_list:
                if 'cmd' in gvars.fx_dic[k].keys():
                    gvars.fx_dic[k]['cmd'].add(k + ' ' + f)

        return cmd_set

    # 解析用户发来的命令，判断请求类型
    def __parse_msg(self, msg):

        req_content = msg['req_content'].upper()

        # 退订请求
        if config.TD_CMD == req_content:
            msg['request_type'] = config.TD_MSG_TYPE
            msg['ans_ok'] = '1'  # 已经解决问题
            msg['replied'] = '1'

        # 订阅请求
        elif config.DY_CMD == req_content:
            msg['request_type'] = config.DY_MSG_TYPE
            msg['ans_ok'] = '1'  # 已经解决问题
            msg['replied'] = '1'  # 已回复

        # 市场概况
        elif config.MKT_CMD == req_content:
            msg['request_type'] = config.MKT_MSG_TYPE
            msg['ans_ok'] = '1'  # 已经解决问题
            msg['replied'] = '1'

        # 请求单个外汇对的技术指标
        elif req_content in self.fx_pair_cmd_set:
            msg['request_type'] = config.FX_PAIR_MSG_TYPE
            msg['ans_ok'] = '1'  # 已经解决问题
            msg['replied'] = '1'

            cont_list = req_content.split(' ')
            if len(cont_list) > 1:
                # 有周期
                freq = cont_list[1].upper()
                if freq == 'M' or freq == 'H':
                    freq += '1'
            else:  # 默认周期
                freq = config.DEFAULT_FREQ

            # 根据value，找key
            fx_cont = req_content.upper()
            for k, v in gvars.fx_dic.items():
                cmd = v['cmd']
                if fx_cont in cmd:
                    fx = k
                    break

            msg['fx'] = fx
            msg['fx_id'] = gvars.fx_dic[fx]['id']
            msg['freq'] = freq

        # 普通文本
        else:
            msg['request_type'] = config.TEXT_MSG_TYPE
            msg['replied'] = '1'
            msg['ans_ok'] = '1'  # 已经解决问题

            if req_content.upper() in ['H', 'HELP', '帮助', 'BZ']:
                msg['request_type'] = config.HELP_MSG_TYPE

    # 调用itchat回复msg，同时把回复的内容存入数据库
    def __itchat_reply_save_into_db(self, msg):
        # a. 调用itchat回复
        res_content = msg['res_content']
        if config.SEND_NO_CHECK:
            gvars.itchat.send(res_content, toUserName=msg['FromUserName'])
        else:
            gvars.itchat.send(res_content, toUserName=msg['sender_username'])
            try:
                # a. 插入主表
                sql1 = ("INSERT INTO t_request "
                        "(_user_id, _datetime, _content, _request_type, _replied, _ans_ok) VALUES "
                        "(%d, '%s','%s', '%s', '%s', '%s');")
                params1 = (msg['sender_id_in_db'], msg['req_time'], msg['req_content'],
                           msg['request_type'], msg['replied'], msg['ans_ok'])
                gvars.sql_helper.cursor.execute(sql1 % params1)

                # b. 得到主表最后一条记录的id
                request_id = gvars.sql_helper.get_max_id_in_tb('t_request')

                # c. 从表
                sql2 = ("INSERT INTO t_reply_menu "
                        "(_request_id, _content, _datetime) VALUES "
                        "(%d, '%s', NOW());")
                params2 = (request_id, msg['res_content'])
                gvars.sql_helper.cursor.execute(sql2 % params2)

            except Exception as e:
                gvars.sql_helper.connect.rollback()  # 事务回滚
                print('MsgService::__itchat_reply_save_into_db:事务处理失败', e)
            else:
                gvars.sql_helper.connect.commit()  # 事务提交
                print('MsgService::__itchat_reply_save_into_db:事务处理成功')

    # 接收请求，解析消息，回复消息，操作数据库。
    def receive_response(self, msg):
        # 0. 解析消息
        self.__parse_msg(msg)

        sender_id_in_db = msg['sender_id_in_db']
        request_type = msg['request_type']

        if config.HELP_MSG_TYPE == request_type:
            msg['res_content'] = config.HELP_MSG
            # b. 回复消息 & 把回复的消息存入数据库
            self.__itchat_reply_save_into_db(msg)

        # 不是命令的文本消息（得到菜单，获取菜单，在菜单上操作等）
        elif config.TEXT_MSG_TYPE == request_type:
            # a. 根据规则，生成需要回复的文字
            msg['res_content'] = config.MENU
            # b. 回复消息 & 把回复的消息存入数据库
            self.__itchat_reply_save_into_db(msg)

        # 订阅
        elif config.DY_MSG_TYPE == request_type:
            gvars.sub_serv.subscribe(sender_id_in_db)  # a. 修改数据库（订阅状态）
            res_content = config.DY_SUCCESS  # b. 回复消息 & 把回复的消息存入数据库
            msg['res_content'] = res_content
            self.__itchat_reply_save_into_db(msg)

        # 退订
        elif config.TD_MSG_TYPE == request_type:
            gvars.sub_serv.unsubscribe(sender_id_in_db)  # a. 修改数据库（退订状态）
            res_content = config.TD_SUCCESS  # b. 回复消息 & 把回复的消息存入数据库
            msg['res_content'] = res_content
            self.__itchat_reply_save_into_db(msg)

        # 请求市场概况
        elif config.MKT_MSG_TYPE == request_type:

            print('请求市场概况')
            new_file_name = uuid.uuid1().hex

            # 把数据文件复制到回复数据的地方
            file_prefix = config.DAILY_MKT_IMG_DIR + 'snapshot'
            img_url = file_prefix + '.png'

            # 检查图片大小是否小于180KB...
            size = os.path.getsize(img_url)
            if size < config.IMG_SIZE_LOW_THRESH:  # 图片还没有生成完毕
                time.sleep(1)
                size = os.path.getsize(img_url)  # 再次检查
                if size < config.IMG_SIZE_LOW_THRESH:
                    gvars.itchat.send(config.SYSTEM_BUSY, msg['FromUserName'])
                    return

            self.mkt_img_url = img_url
            file_name = file_prefix + '.csv'
            shutil.copyfile(file_name,
                            config.REPLY_MKT_STORE_DIR + new_file_name)

            # 检查当前时间和市场概况图片的时间之差
            # 如果相隔很近，则发送。否则，显示系统正在维护……???????

            # 调用itchat发送图片
            if config.SEND_NO_CHECK:
                gvars.itchat.send_image(img_url, msg['FromUserName'])
            else:
                gvars.itchat.send_image(img_url, msg['sender_username'])

                try:
                    # a. 插入主表
                    sql = ("INSERT INTO t_request "
                           "(_user_id, _datetime, _content, _request_type, _replied, _ans_ok) VALUES "
                           "(%d, '%s','%s', '%s', '%s', '%s');")
                    params = (msg['sender_id_in_db'], msg['req_time'], msg['req_content'],
                              msg['request_type'], msg['replied'], msg['ans_ok'])
                    gvars.sql_helper.cursor.execute(sql % params)

                    # b. 得到主表最后一条记录的id
                    request_id = gvars.sql_helper.get_max_id_in_tb('t_request')

                    # c. 从表
                    sql = ("INSERT INTO t_request_mkt (_request_id, _reply_file_name) VALUES "
                           "(%d, '%s');")
                    params = (request_id, new_file_name)
                    gvars.sql_helper.cursor.execute(sql % params)

                except Exception as e:
                    gvars.sql_helper.connect.rollback()  # 事务回滚
                    print('MsgService::receive_response:市场概况事务处理失败', e)
                else:
                    gvars.sql_helper.connect.commit()  # 事务提交
                    print('MsgService::receive_response:市场概况事务处理成功')

        elif config.FX_PAIR_MSG_TYPE == request_type:

            print('请求单一外汇技术指标')
            freq = msg['freq']
            fx = msg['fx']

            file_prefix = config.FX_PAIR_IMG_DIR + fx + '_' + freq

            # 读取单一外汇技术指标的图片
            img_url = file_prefix + '.png'
            size = os.path.getsize(img_url)
            if size < config.IMG_SIZE_LOW_THRESH:  # 图片还没有生成完毕
                time.sleep(1)
                size = os.path.getsize(img_url)  # 再次检查
                if size < config.IMG_SIZE_LOW_THRESH:
                    gvars.itchat.send(config.SYSTEM_BUSY, msg['FromUserName'])
                    return

            # 把数据文件复制到回复数据的地方
            file_name = file_prefix + '.csv'
            new_file_name = uuid.uuid1().hex
            shutil.copyfile(file_name,
                            config.REPLY_FX_PAIR_STORE_DIR + new_file_name)

            # 调用itchat发送图片
            if config.SEND_NO_CHECK:
                gvars.itchat.send_image(img_url, msg['FromUserName'])
            else:
                gvars.itchat.send_image(img_url, msg['sender_username'])

                # 更新数据库，事务提交 （暂时没有串行执行）
                # (1) 把用户的请求插入数据库
                # (2) 查询最后一条请求的id
                # (3) 把请求插入对某一外汇对的技术指标的请求记录表

                try:
                    sql = ("INSERT INTO t_request " 
                           "(_user_id, _datetime, _content, _request_type, _replied, _ans_ok) VALUES "
                           "(%d, '%s','%s', '%s', '%s', '%s');")
                    params = (msg['sender_id_in_db'], msg['req_time'], msg['req_content'],
                              msg['request_type'], msg['replied'], msg['ans_ok'])
                    gvars.sql_helper.cursor.execute(sql % params)

                    request_id = gvars.sql_helper.get_max_id_in_tb('t_request')
                    fx_id = msg['fx_id']

                    sql = ("INSERT INTO t_req_res_fx_pair "
                           "(_fx_id, _ma_period, _request_id, _reply_file_name) VALUES "
                           "(%d, '%s' ,%d, '%s');")
                    params = (fx_id, freq, request_id, new_file_name)
                    gvars.sql_helper.cursor.execute(sql % params)

                except Exception as e:
                    gvars.sql_helper.connect.rollback()  # 事务回滚
                    print('MsgService::receive_response:单一外汇事务处理失败', e)
                else:
                    gvars.sql_helper.connect.commit()  # 事务提交
                    print('MsgService::receive_response:单一外汇事务处理成功')

        elif config.UNKONW_MSG_TYPE == request_type:
            msg['res_content'] = '暂时不知道回复什么……'

    # 向所有订阅用户发送市场概况
    def send_mkt_msg_to_subscirbers(self):

        # 1. 查询当前所有的订阅用户
        subscriber_id_list = gvars.user_serv.get_all_subscriber_ids()
        subscriber_wx_username_list = []
        for u_id in subscriber_id_list:
            remark_name = config.REMARK_PREFIX + str(u_id)
            if remark_name in gvars.frd_r2u.keys():
                subscriber_wx_username_list.append(gvars.frd_r2u[remark_name])

        # 2 & 3 把数据文件复制到回复数据的地方
        # 2 & 3. 把该消息存入数据库的 t_daily_mkt表 和 t_daily_mkt_detail表
        new_file_name = uuid.uuid1().hex
        file_prefix = config.DAILY_MKT_IMG_DIR + 'snapshot'
        img_url = file_prefix + '.png'

        counter = 3
        while counter > 0:
            size = os.path.getsize(img_url)
            if size < config.IMG_SIZE_LOW_THRESH:  # 图片还没有生成完毕
                counter -= 1
                time.sleep(1)
            else:
                counter = -1
        if counter == 0:
            print('每日市场概况图片生成不成功')
            return

        file_name = file_prefix + '.csv'
        shutil.copyfile(file_name,
                        config.DAILY_MKT_MSG_STORE_DIR + new_file_name)
        self.mkt_img_url = img_url

        try:
            # a. 哪一条市场概况
            sql = ("INSERT INTO t_daily_mkt (_datetime, _file_name) VALUES "
                   "(NOW(), '%s');" % (new_file_name))
            gvars.sql_helper.cursor.execute(sql)

            # b. 每日市场概况消息记录表的id是多少
            max_id = gvars.sql_helper.get_max_id_in_tb('t_daily_mkt')

            # c. 向哪些用户发送了
            sql = ""
            for sub_user_id in subscriber_id_list:
                sql += ("INSERT INTO t_daily_mkt_detail " 
                        "(_daily_mkt_id, _user_id) VALUES " 
                        "(%d, %d);" % (max_id, sub_user_id))
            gvars.sql_helper.cursor.execute(sql)

        except Exception as e:
            gvars.sql_helper.connect.rollback()  # 事务回滚
            print('MsgService::send_mkt_msg_to_subscirbers:事务处理失败', e)
        else:
            gvars.sql_helper.connect.commit()  # 事务提交
            print('MsgService::send_mkt_msg_to_subscirbers:事务处理成功')

        # 4. 多线程向所有订阅用户发送市场概况
        thread_pool_num = config.SEND_MKT_MSG_THREAD_POOL_NUMBER
        pool = ThreadPool(thread_pool_num)
        pool.map(self.__do_send_daily_mkt_img, subscriber_wx_username_list)
        pool.close()

    # 向所有用户发送消息
    def send_msg_to_all_users(self, msg):
        msg_type = msg['msg_type']
        if config.SYS_MSG_TEXT == msg_type:
            print('发送文本消息')
            content = msg['content']
            self.sys_msg = msg
            username_list = list(gvars.frd_u2r.keys())

            # 把系统消息记录到数据库中
            sql = ("INSERT INTO t_sys_msg (_type, _datetime, _content,_admin_id) VALUES "
                   "('%s',NOW(),'%s',%d);" % (config.SYS_MSG_TEXT, content, config.ADMIN_ID))
            gvars.sql_helper.update(sql)

            # 多线程向所有用户发送文本消息
            thread_pool_num = config.SEND_SYS_MSG_THREAD_POOL_NUMBER
            pool = ThreadPool(thread_pool_num)
            pool.map(self.__do_send_sys_txt_msg, username_list)
            pool.close()

    def __do_send_sys_txt_msg(self, wx_user_name):
        time.sleep(round(random.uniform(0, 5), 1))
        gvars.itchat.send_msg(self.sys_msg['content'], wx_user_name)

    def __do_send_daily_mkt_img(self, user_name):
        time.sleep(round(random.uniform(0, 10), 1))
        gvars.itchat.send_image(self.mkt_img_url, toUserName=user_name)
