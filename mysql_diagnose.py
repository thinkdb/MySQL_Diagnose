#!/bin/env python
# -*- coding:utf8 -*-
from lib.funcs import DBAPI
from lib.funcs import get_config
from monitor import monitor
from lib.funcs import Logger
from multiprocessing import Pool


def get_account_info(host, user, passwd, port, db):
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
    account_info = my_conn.query(diagnose_sql)
    return account_info

if __name__ == "__main__":
    conf_info = get_config()

    LEVEL = int(conf_info['log_level'])
    host = conf_info['host']
    user = conf_info['user']
    password = conf_info['password']
    port = int(conf_info['port'])
    database = conf_info['database']
    processing = int(conf_info['processing'])

    Logger = Logger()
    Logger.logger(LEVEL).info('Start collecting data of performance !!!')
    account_list = get_account_info(host=host, user=user, passwd=password, port=port, db=database)

    Logger.logger(LEVEL).debug("Source data info: "+str(account_list))
    max_len = len(account_list)
    pool = Pool(processing)
    for i in range(max_len):
        p = pool.apply_async(func=monitor, args=(account_list[i], LEVEL,))
        Logger.logger(LEVEL).debug("Start collecting {Host} info: ".format(Host=account_list[i]['host']))
    pool.close()
    pool.join()

