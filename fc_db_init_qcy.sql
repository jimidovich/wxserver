DROP DATABASE IF EXISTS fx_db;

CREATE DATABASE IF NOT EXISTS fx_db 
CHARACTER SET utf8 COLLATE utf8_general_ci;
USE fx_db;


-- 加好友
-- 什么时候退出? 什么时候加入的? 用户都不会删除

-- 用户表
DROP TABLE IF EXISTS t_user;
CREATE TABLE t_user(
_id INT PRIMARY KEY AUTO_INCREMENT,
_fx_acc VARCHAR(128),
_remark_id INT NOT NULL, -- 好友备注id
_admin_id INT NOT NULL, -- 管理员id
_subscriber CHAR(1) NOT NULL, -- 是否是订阅者
_exit CHAR(1) NOT NULL, -- 是否离开本平台
_enter_datetime DATETIME NOT NULL, -- 添加好友的时间
_exit_datetime DATETIME -- 主动删除我们的时间
);



-- 用户订阅情况详细表
DROP TABLE IF EXISTS t_subscriber;
CREATE TABLE t_subscriber(
_id INT PRIMARY KEY AUTO_INCREMENT,
_user_id INT NOT NULL, -- 引用用户表的用户id
_operation CHAR(1) NOT NULL, -- 0 取消，1 订阅
_datetime DATETIME NOT NULL,
CONSTRAINT _sub_user_id_FK FOREIGN KEY(_user_id) 
REFERENCES t_user(_id)
);




-- 外汇种类表
DROP TABLE IF EXISTS t_fx;
CREATE TABLE t_fx(
_id INT PRIMARY KEY AUTO_INCREMENT,
_name CHAR(6) UNIQUE NOT NULL, -- EURUSD
_c1 CHAR(3) NOT NULL, -- EUR
_c2 CHAR(3) NOT NULL, -- USD
_c1_chinese VARCHAR(32) NOT NULL, -- 欧元
_c2_chinese VARCHAR(32) NOT NULL, -- 美元
_css_class CHAR(3) NOT NULL -- 货币图片css样式表单
);


INSERT INTO t_fx (_name, _c1, _c2, _c1_chinese, _c2_chinese, _css_class)       VALUES ('EURUSD','EUR','USD','欧元','美元','eur');
INSERT INTO t_fx (_name, _c1, _c2, _c1_chinese, _c2_chinese, _css_class)       VALUES ('GBPUSD','GBP','USD','英镑','美元','gbp');
INSERT INTO t_fx (_name, _c1, _c2, _c1_chinese, _c2_chinese, _css_class)       VALUES ('AUDUSD','AUD','USD','澳大利亚元','美元','aud');
INSERT INTO t_fx (_name, _c1, _c2, _c1_chinese, _c2_chinese, _css_class)       VALUES ('NZDUSD','NZD','USD','新西兰元','美元','nzd');
INSERT INTO t_fx (_name, _c1, _c2, _c1_chinese, _c2_chinese, _css_class)       VALUES ('USDJPY','USD','JPY','美元','日元','jpy');
INSERT INTO t_fx (_name, _c1, _c2, _c1_chinese, _c2_chinese, _css_class)       VALUES ('USDCAD','USD','CAD','美元','加拿大元','cad');
INSERT INTO t_fx (_name, _c1, _c2, _c1_chinese, _c2_chinese, _css_class)       VALUES ('USDCHF','USD','CHF','美元','瑞士法郎','chf');
INSERT INTO t_fx (_name, _c1, _c2, _c1_chinese, _c2_chinese, _css_class)       VALUES ('USDNOK','USD','NOK','美元','挪威克朗','nok');
INSERT INTO t_fx (_name, _c1, _c2, _c1_chinese, _c2_chinese, _css_class)       VALUES ('USDSEK','USD','SEK','美元','瑞典克朗','sek');
INSERT INTO t_fx (_name, _c1, _c2, _c1_chinese, _c2_chinese, _css_class)       VALUES ('USDTRY','USD','TRY','美元','土耳其里拉','try');
INSERT INTO t_fx (_name, _c1, _c2, _c1_chinese, _c2_chinese, _css_class)       VALUES ('USDMXN','USD','MXN','美元','墨西哥比索','mxn');
INSERT INTO t_fx (_name, _c1, _c2, _c1_chinese, _c2_chinese, _css_class)       VALUES ('USDZAR','USD','ZAR','美元','南非兰特','zar');
INSERT INTO t_fx (_name, _c1, _c2, _c1_chinese, _c2_chinese, _css_class)       VALUES ('USDCNH','USD','CNH','美元','离岸人民币','cnh');


-- SELECT CONCAT('2',_id,' ',_c1_chinese,' - ',_c2_chinese,'\\n') FROM t_fx;

-- 每日市场概况简表
DROP TABLE IF EXISTS t_daily_mkt;
CREATE TABLE t_daily_mkt(
_id INT PRIMARY KEY AUTO_INCREMENT,
_datetime DATETIME UNIQUE NOT NULL,
_file_name CHAR(32) UNIQUE NOT NULL
);


-- 每天推送的市场概况消息详细表
DROP TABLE IF EXISTS t_daily_mkt_detail;
CREATE TABLE t_daily_mkt_detail(
_id INT PRIMARY KEY AUTO_INCREMENT,
_daily_mkt_id INT NOT NULL,
_user_id INT NOT NULL,
CONSTRAINT _detail_mkt_daily_mkt_id_FK FOREIGN KEY(_daily_mkt_id) 
REFERENCES t_daily_mkt(_id),
CONSTRAINT _detail_mkt_user_id_FK FOREIGN KEY(_user_id) 
REFERENCES t_user(_id)
);


-- 用户发送的消息请求表（专门管理接收消息的表）
-- 如果发了一条很长的消息????
-- 如果乱发???? 各种奇怪的问题
-- ?? text 65,535

DROP TABLE IF EXISTS t_request;
CREATE TABLE t_request(
_id INT PRIMARY KEY AUTO_INCREMENT,
_user_id INT NOT NULL,
_datetime DATETIME UNIQUE NOT NULL,
_content TEXT NOT NULL, -- 文本内容
_request_type CHAR(1),
_replied CHAR(1),
_ans_ok CHAR(1),
CONSTRAINT _request_user_id_FK FOREIGN KEY(_user_id) 
REFERENCES t_user(_id)
);


-- 回复的菜单表
DROP TABLE IF EXISTS t_reply_menu;
CREATE TABLE t_reply_menu(
_id INT PRIMARY KEY AUTO_INCREMENT,
_request_id INT UNIQUE NOT NULL,
_content TEXT NOT NULL,
_datetime DATETIME UNIQUE NOT NULL,
CONSTRAINT _menu_request_id_FK FOREIGN KEY(_request_id) 
REFERENCES t_request(_id)
);


-- 对某一外汇对的技术指标的请求和回复表
DROP TABLE IF EXISTS t_req_res_fx_pair;
CREATE TABLE t_req_res_fx_pair(
_id INT PRIMARY KEY AUTO_INCREMENT,
_fx_id INT NOT NULL, -- 指向外汇对表的主键id
_request_id INT UNIQUE NOT NULL,
_ma_period CHAR(4) NOT NULL,
_reply_file_name CHAR(32) UNIQUE NOT NULL,
CONSTRAINT _request_fx_pair_req_id_FK FOREIGN KEY(_request_id) 
REFERENCES t_request(_id),
CONSTRAINT _request_fx_pair_fx_id_FK FOREIGN KEY(_fx_id) 
REFERENCES t_fx(_id)
);


-- 对市场概况的请求记录表
DROP TABLE IF EXISTS t_request_mkt;
CREATE TABLE t_request_mkt(
_id INT PRIMARY KEY AUTO_INCREMENT,
_request_id INT UNIQUE NOT NULL,
_reply_file_name CHAR(32) UNIQUE NOT NULL,
CONSTRAINT _request_mkt_req_id_FK FOREIGN KEY(_request_id) 
REFERENCES t_request(_id)
);


-- 系统消息表
DROP TABLE IF EXISTS t_sys_msg;
CREATE TABLE t_sys_msg(
_id INT PRIMARY KEY AUTO_INCREMENT,
_type CHAR(1) NOT NULL,
_datetime DATETIME NOT NULL UNIQUE,
_content TEXT,
_admin_id INT NOT NULL
);
