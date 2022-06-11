# -*- coding: utf-8 -*-
"""
desc:统一的日志配置文件
"""
#LOGGER_PATH日志文件夹，统一设置
from loguru import logger
import time
import os
from os.path import exists, join
LOGGER_PATH='/root/guangxi_test/Logs'
# 配置logger的样式
fmt = '{time:YYYY-MM-DD HH:mm:ss ZZ} | {level} | {file}:{function}:{line} - {message}'
#每月日志文件夹
if not os.path.exists(LOGGER_PATH):
    os.makedirs(LOGGER_PATH)
month_file = time.strftime("%Y_%m", time.localtime())
path = LOGGER_PATH + '/' + month_file + '_log'
if not exists(path):
    os.mkdir(path)
#按天生成日志文件
rq = time.strftime('%Y_%m_%d', time.localtime(time.time()))
name = rq +'_log_file.log'
log_name = join(path,name)
#邮件文件日志文件
name_e = rq +'_email_log_file.log'
log_name_e = join(path,name_e)
#配置日志文件
logger.add( log_name,
            enqueue=True,
            filter=lambda record: record['extra']['task'] == "other",
            format=fmt
            #rotation="12:00",
)
#邮件日志文件
logger.add( log_name_e,
            enqueue=True,
            filter=lambda record: record['extra']['task'] == "email",
            format=fmt
            #rotation="12:00",
)


logger_rule=logger.bind(task='other')
logger_email=logger.bind(task='email')
