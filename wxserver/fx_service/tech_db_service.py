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


