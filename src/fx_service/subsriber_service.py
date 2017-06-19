# -*- coding: utf-8 -*-

import src.main.gvars as gvars


class SubscriberService:
    def __init__(self):
        print('SubscriberService::init')

    # 开启订阅
    def subscribe(self, user_id):
        sql1 = "INSERT INTO t_subscriber (_user_id,\
         _operation, _datetime) VALUES (%d,'1',NOW());" % user_id
        sql2 = "UPDATE t_user SET _subscriber = '1' WHERE _id = %d;" % user_id
        gvars.sql_helper.update_with_tx([sql1, sql2])
        # 怎么看得出来数据库已经修改成功???????????

    # 取消订阅
    def unsubscribe(self, user_id):
        sql1 = "INSERT INTO t_subscriber (_user_id,\
                 _operation, _datetime) VALUES (%d,'0',NOW());" % user_id
        sql2 = "UPDATE t_user SET _subscriber = '0' WHERE _id = %d;" % user_id
        gvars.sql_helper.update_with_tx([sql1, sql2])
