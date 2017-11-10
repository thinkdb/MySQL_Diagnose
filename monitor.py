#!/bin/env python
# -*- coding:utf8 -*-
from mysql.mysql_html_result import *
from machine.machine_html_result import *
from lib.funcs import OsInfo
from lib.funcs import MySQLBseInfo
from lib.funcs import Logger


def get_machine_info(os_connected_stream, host_ip, level, fd):
    Logger().logger(level).info('Start get machine base info: {host}'.format(host=host_ip))
    host_info = get_host_info(os_connected_stream)
    Logger().logger(level).info('Start get machine disk info: {host}'.format(host=host_ip))
    disk_info = get_disk_info(os_connected_stream)
    fd.write("<h3 class='awr'>Machine Summary</h3>")
    fd.write(host_info)
    fd.write(disk_info)


def get_master_info(mysql_connected_stream, os_connected_stream, host_ip, level, fd):
    metadata = mysql_connected_stream.my_conn.query('select @@innodb_stats_on_metadata as innodb_stats_on_metadata;')
    metadata_flag = int(metadata[0]['innodb_stats_on_metadata'])

    # 如果打开 innodb_stats_on_metadata, 则不收集 MySQL 相关信息
    if not metadata_flag:
        # 获取 MySQL 实例信息
        Logger().logger(level).info('Start get MySQL base info: {host}'.format(host=host_ip))
        mysql_base = get_mysql_base(mysql_connected_stream)
        Logger().logger(level).info('Start get Slave info: {host}'.format(host=host_ip))
        slave_info = get_slave_info(mysql_connected_stream)
        Logger().logger(level).info('Start get Null password account info: {host}'.format(host=host_ip))
        user_info = get_security_user(mysql_connected_stream)
        Logger().logger(level).info('Start get INNODB info: {host}'.format(host=host_ip))
        innodb_info = get_innodb_status(mysql_connected_stream)
        Logger().logger(level).info('Start get Binlog info: {host}'.format(host=host_ip))
        binlog_info = get_binlog_info(mysql_connected_stream, os_connected_stream)
        Logger().logger(level).info('Start get MySQL config file info: {host}'.format(host=host_ip))
        my_cnf_info = get_my_cnf(os_connected_stream)
        Logger().logger(level).info('Start get TPS info: {host}'.format(host=host_ip))
        tps_info = get_tps_qps(mysql_connected_stream, times=20, interval=1)
        # 最多显示10s的tps信息
        Logger().logger(level).info('Start get table without primary key info: {host}'.format(host=host_ip))
        not_primary_key_table_info = get_not_primary_key(mysql_connected_stream)
        Logger().logger(level).info('Start get table without innodb engine info: {host}'.format(host=host_ip))
        not_innodb_tables_info = get_not_innodb_tables(mysql_connected_stream)
        Logger().logger(level).info('Start get routines info: {host}'.format(host=host_ip))
        routines_info = get_routines(mysql_connected_stream)
        Logger().logger(level).info('Start check auto increment column info: {host}'.format(host=host_ip))
        auto_increment_info = get_auto_increment(mysql_connected_stream)

        engine_table = get_engine_table_info(mysql_connected_stream)
        Logger().logger(level).info('Start get important variables info: {host}'.format(host=host_ip))
        imp_variables = get_important_variables(mysql_connected_stream)
        current_connection = get_current_connection(mysql_connected_stream)
        performance = performance_analyse(mysql_connected_stream)

        fd.write("<h3 class='awr'>MySQL Summary</h3>")
        fd.write(mysql_base)

        if current_connection:
            fd.write(current_connection)

        fd.write(tps_info)
        if slave_info:
            fd.write(slave_info)
        fd.write(innodb_info)
        fd.write(performance)
        if user_info:
            fd.write(user_info)
        fd.write(binlog_info)
        if auto_increment_info:
            fd.write(auto_increment_info)
        if not_primary_key_table_info:
            fd.write(not_primary_key_table_info)
        if not_innodb_tables_info:
            fd.write(not_innodb_tables_info)
        if routines_info:
            fd.write(routines_info)

        if engine_table:
            fd.write(engine_table)

        if imp_variables:
            fd.write(imp_variables)

        fd.write(my_cnf_info)


def monitor(account_info, level):
    html_head = """
    <html>
    <head>
    <title>MySQL Diagnose Report</title>
    <link rel="shortcut icon" href="../imgs/favicon.ico" />
    <style type="text/css">
    body.awr   {font:bold 10pt Arial,Helvetica,Geneva,sans-serif;color:black; background:White;}
    pre.awr    {font:8pt Courier;color:black; background:White;}
    h1.awr     {font:bold 20pt Arial,Helvetica,Geneva,sans-serif;color:#336699;background-color:White;border-bottom:1px solid #cccc99;margin-top:0pt; margin-bottom:0pt;padding:0px 0px 0px 0px;}
    h2.awr     {font:bold 18pt Arial,Helvetica,Geneva,sans-serif;color:#336699;background-color:White;margin-top:4pt; margin-bottom:0pt;}
    h3.awr     {font:bold 16pt Arial,Helvetica,Geneva,sans-serif;color:#336699;background-color:White;margin-top:4pt; margin-bottom:0pt;}
    li.awr     {font: 8pt Arial,Helvetica,Geneva,sans-serif; color:black; background:White;}
    th.awrnobg {font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:black; background:White;padding-left:4px; padding-right:4px;padding-bottom:2px}
    th.awrbg   {font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;padding-left:4px; padding-right:4px;padding-bottom:2px}
    td.awrnc   {font:8pt Arial,Helvetica,Geneva,sans-serif;color:black;background:White;vertical-align:top;}
    td.awrwaring {font:8pt Arial,Helvetica,Geneva,sans-serif;color:black;background:orange;vertical-align:top;}
    td.awrcritical {font:8pt Arial,Helvetica,Geneva,sans-serif;color:black;background:red;vertical-align:top;}
    td.awrnc   {font:8pt Arial,Helvetica,Geneva,sans-serif;color:black;background:White;vertical-align:top;}
    td.awrc    {font:8pt Arial,Helvetica,Geneva,sans-serif;color:black;background:#FFFFCC; vertical-align:top;}
    td.awrmbg  {font:bold 8pt Arial,Helvetica,Geneva,sans-serif; color:White; background:#0066CC;text-align:center;}
    a.awr      {font:bold 8pt Arial,Helvetica,sans-serif;color:#663300; vertical-align:top;margin-top:0pt; margin-bottom:0pt;}
    </style>

    </head>

    <body class='awr'>
    <h1 class="awr">
    MySQL DIAGNOSE REPOSITORY report for
    </h1>
    """
    current_time = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))
    host_ip = account_info['host']

    fd = open('./AWR_report/MySQL_AWR_{host}_{time}.html'.format(host=host_ip, time=current_time), 'w')

    Logger().logger(level).info('Start get machine connect handle: {host}'.format(host=host_ip))
    os_connected_stream = OsInfo(account_info['host'], account_info['ssh_account'],
                                 account_info['ssh_passwd'], account_info['ssh_port'])
    Logger().logger(level).info('Start get MySQL connect handle: {host}'.format(host=host_ip))
    mysql_connected_stream = MySQLBseInfo(account_info['host'], account_info['mysql_account'],
                                          account_info['mysql_passwd'], account_info['mysql_port'])

    fd.write(html_head)
    # 获取机器信息
    get_machine_info(os_connected_stream, host_ip, level, fd)
    get_master_info(mysql_connected_stream, os_connected_stream, host_ip, level, fd)
    fd.write("\n</body></html>")
    fd.flush()
    fd.close()
