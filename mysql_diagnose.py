#!/bin/env python
# -*- coding:utf8 -*-
import json
from lib.funcs import DBAPI
from lib.funcs import get_config
from monitor import monitor
from lib.funcs import Logger
from multiprocessing import Pool


def get_account_info_for_db(host, user, passwd, port, db, level, processing, logger):
    """
    获取要连接的机器列表
    :param host: MySQL 地址
    :param user: MySQL 账号
    :param passwd: MySQL 密码
    :param port: MySQL 端口
    :param db: 数据表存放的库名
    :return: 元组 ((host1, mysql_account, mysql_passwd, mysql_port, ssh_account, ssh_port, ssh_passwd), ())
    """
    diagnose_sql = "select host, mysql_account, mysql_passwd, mysql_port, ssh_account, ssh_passwd, ssh_port " \
                   "from diagnose_account_info"
    my_conn = DBAPI(host=host, user=user, password=passwd, port=int(port), database=db)
    account_list = my_conn.query(diagnose_sql)
    max_len = len(account_list)
    pool = Pool(processing)
    for i in range(max_len):
        p = pool.apply_async(func=monitor, args=(account_list[i], level,))
        logger.logger(level).info("Start collecting {Host} info: ".format(Host=account_list[i]['host']))
    pool.close()
    pool.join()


def get_account_info_for_json(processing, level, logger):
    account_all_info = json.load(open("./conf/account_info.json", "r"))
    pool = Pool(processing)
    for account in account_all_info:
        p = pool.apply_async(func=monitor, args=(account_all_info[account], level,))
        logger.logger(level).info("Start collecting {Host} info: ".format(Host=account))
    pool.close()
    pool.join()


if __name__ == "__main__":
    Logger = Logger()
    conf_info = get_config()
    level = int(conf_info['log_level'])
    host = conf_info['host']
    user = conf_info['user']
    password = conf_info['password']
    port = int(conf_info['port'])
    database = conf_info['database']
    processing = int(conf_info['processing'])
    datasource_type = int(conf_info['type'])

    Logger.logger(level).info('Start collecting data of performance !!!')
    if datasource_type == 1:
        get_account_info_for_json(processing, level, Logger)
    else:
        get_account_info_for_db(host, user, password, port, database, level, processing, Logger)
