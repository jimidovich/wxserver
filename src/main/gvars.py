g = {}

sql_helper = None
itchat = None
sub_serv = None
user_serv = None
msg_serv = None
tech_db_serv = None

mix_friend_list = None  # 所有的 (现有的 + 删除的)
friend_list = None
frd_u2r = None  # all remark_name -> wx username
frd_r2u = None
me = None
fx_dic = None

frd_r2u_fx = None  # remark_name with fx_prefix -> wx username
frd_u2r_fx = None

# 这是已经在数据库中的用户
frd_r2dbid = None  # remark_name -> user_id in t_user
frd_dbid2r = None

auto_add_friend = True
