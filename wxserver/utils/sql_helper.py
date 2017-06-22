# -*- coding: utf-8 -*-

import pymysql.cursors

import src.params.Parameters as parameters


class SqlHelper:
    def __init__(self):
        print('SqlHelper::__init__')
        connect = pymysql.Connect(
            host='localhost',
            port=3306,
            user=parameters.SQL_USER_NAME,
            passwd=parameters.SQL_PASSWORD,
            db=parameters.DATABASE_NAME,
            charset='utf8'
        )
        self.connect = connect
        self.cursor = connect.cursor()

    def query(self, sql):
        try:
            self.cursor.execute(sql)
            rs = self.cursor.fetchall()
            return rs
        except:
            print('query:' + sql + ' 失败')

    def update(self, sql):
        try:
            print('sql_helper::update ' + sql)
            self.cursor.execute(sql)
            self.connect.commit()  # 返回值呢？
        except:
            print('update:' + sql + ' 失败')

    # 更新数据库(含事务处理)
    def update_with_tx(self, sql_list):
        try:
            for sql in sql_list:
                self.cursor.execute(sql)
        except Exception as e:
            self.connect.rollback()  # 事务回滚
            print('update_with_tx:事务处理失败', e)
        else:
            self.connect.commit()  # 事务提交
            print('update_with_tx:事务处理成功')

    def get_max_id_in_tb(self, table_name):
        sql = "SELECT _id FROM %s ORDER BY _id DESC LIMIT 0,1;" % table_name
        return self.query(sql)[0][0]

    def __del__(self):
        print('SqlHelper::__del__')
        try:
            self.cursor.close()
            self.connect.close()
        except:
            print('cursor，connection关闭失败')
