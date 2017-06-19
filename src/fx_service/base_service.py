# -*- coding: utf-8 -*-

from src.glob import glob
import src.main.gvars as gvars


class BaseService:
    def __init__(self):
        print("BaseService::__init__(self)")
        # self.sql_helper = glob.get_value('sql_helper')
        self.sql_helper = gvars.sql_helper
        # self.itchat = glob.get_value('itchat')
        self.itchat = gvars.itchat
