# -*- coding: utf-8 -*-
import os
import sys

# 数据库
SQL_USER_NAME = 'root'
SQL_PASSWORD = 'jim'
DATABASE_NAME = None

db_names = {'mikens': 'db_wxfx_mikens_testing',
            'testing': 'db_wxfx_testing'}

# 管理员编号！同一家公司的不同微信号，要用不同的Admin_ID以示区别
ADMIN_ID = 1

# 图片大小最低门限
IMG_SIZE_LOW_THRESH = 180 * 1024

SCHED_TIME_LIST = ['08:00:00', '12:00:00', '20:00:00']

# 多线程发送任务的线程数量
SEND_MKT_MSG_THREAD_POOL_NUMBER = 10
SEND_SYS_MSG_THREAD_POOL_NUMBER = 10

INIT_REMARK_NAME = '初始备注'
REMARK_PREFIX = '_$fxuid$_'  # 好友的备注前缀
TEST_DROPPED_FRIENDS_CHATROOM = 'TEST_DROPPED_FRIENDS_CHATROOM'
SET_REMARK_NAME_TIME_SLEEP_SECONDS = 10
SEND_DAILY_MKT_MSG_TIME_SLEEP_SECONDS = 0.5

DY_SUCCESS = '外汇市场概况订阅成功！您将在每天早上8:00收到xxx。退订请回复TD。'
TD_SUCCESS = '已成功取消订阅消息，感谢您的使用！重新开启订阅请回复DY。'

WELCOME_CONTENT = """欢迎使用外汇跟踪机器人！已为您订阅外汇市场每日概况。
您将在每天早晚收到我们为您推送的外汇市场每日概况。

回复
1: 获取即时市场概况
货币 周期: 获取单个货币详情
h: 获取货币详情命令帮助

当前正在调试，出现异常情况请不必在意。"""

MENU = """欢迎使用外汇小帮手
查询市场概况请回复1

==获取分钟技术指标==
欧元兑美元: o m
英镑兑美元: y m
澳元兑美元: a m
新西兰元兑美元: x m
美元兑加元: j m
美元兑日元: r m

查询日K线将m替换为d，小时线为h，空缺默认为小时

更多帮助请回复 h"""
# 人工服务请拨打 021-xxxxxxxx"""

HELP_MSG = """==外汇小帮手使用说明==

市场概况回复1

单个货币对请按 [货币 周期] 的格式回复
货币: 可输入货币代号、拼音首字母或第一个汉字
周期: 可输入m(分),h(时),d(日)

例子: 回复以下命令均可查询欧元兑美元(小时）
o h、e h、eur h、eurusd h、欧 h

==目前支持的货币有==
欧元兑美元:           o
美元兑日元:           r
英镑兑美元:           y
澳元兑美元:           a
新西兰元兑美元:   x
美元兑加元:           j"""
# 人工服务请拨打 021-xxxxxxxx"""

SYSTEM_BUSY = '系统繁忙，请稍后再试'

CMD_ERROR = '命令格式有误，您可以回复h获取帮助'


DY_MSG_TYPE = '1'       # 订阅
TD_MSG_TYPE = '2'       # 退订
TEXT_MSG_TYPE = '3'     # 文本消息
MKT_MSG_TYPE = '4'      # 请求全市场
FX_PAIR_MSG_TYPE = '5'  # 单一品种的消息
HELP_MSG_TYPE = '6'     # 帮助信息
UNKNOWN_MSG_TYPE = '0'  # 未知消息

TD_CMD = 'TD'
DY_CMD = 'DY'
MKT_CMD = '1'
SINGLE_FX_CMD = '2'

DEFAULT_FREQ = 'H1'  # 默认技术指标周期

# 系统消息
SYS_MSG_TEXT = '1'
SYS_MSG_IMG = '2'


# PROJECT_DIR = 'F:/source_files/quant/wechat/arch/wxfx/'
# OUTPUT_DIR = 'D:/G绿了itHub/wxpic_invitation/'
OUTPUT_DIR = '/home/yiju/wxfx/'
DAILY_MKT_IMG_DIR = OUTPUT_DIR + 'wxpic/output/'
FX_PAIR_IMG_DIR = OUTPUT_DIR + 'wxpic/output/'
MKT_IMG_DIR = OUTPUT_DIR + 'wxpic/output/'

WXSERVER_DIR = os.path.abspath(os.path.join(sys.path[0], os.pardir))
DAILY_MKT_MSG_STORE_DIR = WXSERVER_DIR + '/stored_data/mkt_msg/'
REPLY_FX_PAIR_STORE_DIR = WXSERVER_DIR + '/stored_data/reply_data/fx_pair/'
REPLY_MKT_STORE_DIR = WXSERVER_DIR + '/stored_data/reply_data/mkt/'


SEND_NO_CHECK = False
