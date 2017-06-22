# -*- coding: utf-8 -*-

import uuid

from .. import gvars


class TechDbService:
    def __init__(self):
        print('TechDbService::__init__')

    def get_fx_dic(self):
        sql = "SELECT * FROM t_fx;"
        rs = gvars.sql_helper.query(sql)
        fx_dic = {}
        fx_cmd_dic = self.get_fx_cmd_dic()
        cmd_keys = fx_cmd_dic.keys()

        for o in rs:
            item = {}
            item['id'] = o[0]
            item['name'] = o[1]
            item['c1'] = o[2]
            item['c2'] = o[3]
            item['c1_chn'] = o[4]
            item['c2_chn'] = o[5]
            item['css'] = o[6]
            if o[6].upper() in cmd_keys:
                item['cmd'] = fx_cmd_dic[o[6].upper()]
            fx_dic[o[1]] = item

        return fx_dic

    def get_fx_cmd_dic(self):

        fx_list_chinese = ['欧', '加', '澳', '新', '英', '日', '瑞']
        # 日本的j和加拿大的j是一个 -_-!!
        # fx_first_eng = ['E', 'C', 'A', 'N', 'G', 'J', 'C']
        fx_eng = ['EUR', 'CAD', 'AUD', 'NZD', 'GBP', 'JPY', 'CHF']
        fx_py = ['O', 'J', 'A', 'X', 'Y', 'R', 'C']
        freq_set = {'M', 'H', 'D'}

        fx_cmd_dic = {}
        for i in range(len(fx_eng)):
            item = set()
            for freq in freq_set:
                item.add(fx_list_chinese[i] + ' ' + freq)
                # item.add(fx_first_eng[i] + ' ' + freq)
                item.add(fx_eng[i] + ' ' + freq)
                item.add(fx_py[i] + ' ' + freq)

                # 不加周期命令
                item.add(fx_list_chinese[i])
                # item.add(fx_first_eng[i])
                item.add(fx_eng[i])
                item.add(fx_py[i])

                fx_cmd_dic[fx_eng[i]] = item

        # syms = list(zip(fx_list_chinese, fx_eng, fx_py))
        # {sym[1]: set(sym) | {s+' '+f for s in sym for f in freq_set} for sym in syms}

        return fx_cmd_dic

    # 把每日市场概况添加进数据库 -- 每天定时推送的市场概况数据
    # 当前还没有串行执行
    def add_daily_mkt(self, daily_mkt_list):

        img_url = uuid.uuid1().hex
        try:
            # a. 插入主表
            sql = "INSERT INTO t_daily_mkt (_datetime, _img_url) " \
                  "VALUES ( NOW(), '%s');" % (img_url)
            gvars.sql_helper.cursor.execute(sql)

            # b. 得到主表最后一条记录的id
            _daily_mkt_id = gvars.sql_helper.get_max_id_in_tb('t_daily_mkt')

            # c. 从表
            sql = ""
            for m in daily_mkt_list:
                param = (_daily_mkt_id, m['id'], m['mid'], m['prev_mid'])
                sql += "INSERT INTO t_daily_mkt_detail ( _daily_mkt_id," \
                       " _fx_id, _mid, _prev_mid) VALUES " \
                       "(%d,%d,%.5f,%.5f);" % param
                gvars.sql_helper.cursor.execute(sql)

        except Exception as e:
            gvars.sql_helper.connect.rollback()  # 事务回滚
            print('TechDbService::add_daily_mkt:事务处理失败', e)
        else:
            gvars.sql_helper.connect.commit()  # 事务提交
            print('TechDbService::add_daily_mkt:事务处理成功')

    # # 这个函数干嘛的？从数据库中查询最新的每日市场概况？？？？
    # def get_last_daily_mkt(self):
    #
    #     sql = "SELECT * FROM t_daily_mkt ORDER BY _id DESC LIMIT 0,1;"
    #     rs = self.sql_helper.query(sql)
    #     daily_mkt = {}
    #     daily_mkt['id'] = rs[0][0]
    #     daily_mkt['datetime'] = rs[0][1]
    #     daily_mkt['url'] = rs[0][2]
    #
    #     sql = "SELECT * FROM t_daily_mkt_detail dmd, " \
    #           "t_fx f WHERE dmd._fx_id = f._id AND " \
    #           "_daily_mkt_id = %d;"%(daily_mkt['id'])
    #     rs = self.sql_helper.query(sql)
    #     daily_mkt_list = []
    #     for obj in rs:
    #         item = {}
    #         item['mid'] = obj[3]
    #         item['prev_mid'] = obj[4]
    #         item['name'] = obj[6]
    #         item['c1'] = obj[7]
    #         item['c2'] = obj[8]
    #         item['c1_chn'] = obj[9] # 第一种货币的汉语
    #         item['c2_chn'] = obj[10]
    #         item['css'] = obj[11]
    #         daily_mkt_list.append(item)
    #
    #     daily_mkt['list'] = daily_mkt_list
    #
    #     return daily_mkt

    # 从数据库中查询最新的每日市场概况 --> 每天定时推送的市场概况数据
    def get_last_daily_mkt_img_url(self):

        sql = "SELECT * FROM t_daily_mkt ORDER BY _id DESC LIMIT 0,1;"
        rs = gvars.sql_helper.query(sql)
        daily_mkt = {}
        daily_mkt['id'] = rs[0][0]
        daily_mkt['datetime'] = rs[0][1]
        daily_mkt['url'] = rs[0][2]

        return daily_mkt

    # 从数据库中得到最新的，单一品种的技术指标
    def get_last_tech_single(self, req):

        sql = "SELECT * FROM t_tech_single t, t_fx f " \
              "WHERE _ma_period = '%s' AND f._id = t._id " \
              "AND _fx_id = %d ORDER BY t._id DESC LIMIT 0,1;"
        params = (req['freq'], req['fx_id'])
        rs = gvars.sql_helper.query(sql % params)

