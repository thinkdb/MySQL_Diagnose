#!/bin/env python
# -*- coding:utf8 -*-
from pymysql.err import DataError
import pymysql
import paramiko
import re
import os
import sys
import time
import configparser
import logging.config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class DBAPI(object):
    def __init__(self, host, user, password, port, database=None, auto_commit=0):
        self.host = host
        try:
            self.conn = pymysql.connect(host=self.host, user=user, passwd=password,
                                        port=int(port), charset='utf8mb4',
                                        )
            if database:
                self.conn.select_db(database)

            if auto_commit:
                self.conn.autocommit(auto_commit)
            self.cur = self.conn.cursor(pymysql.cursors.DictCursor)
        except Exception as e:
            Logger().logger(30).error('{ip}: '.format(ip=host) + str(e))
            sys.exit(str(e))

    def query(self, sql):
        try:
            self.cur.execute(sql)
            result = self.cur.fetchall()
        except Exception as e:
            Logger().logger(30).error('{ip}: '.format(ip=self.host) + str(e))
            result = e
        return result

    def conn_dml(self, sql):
        try:
            rel = self.cur.execute(sql)
            return rel
        except Exception as e:
            Logger().logger(30).error('{ip}: '.format(ip=self.host) + str(e))
            return e

    def dml_commit(self):
        self.conn.commit()

    def dml_rollback(self):
        self.conn.rollback()

    def close(self):
        self.cur.close()
        self.conn.close()


class RunRomoteCmd(object):
    def __init__(self, ip, ssh_user, ssh_passwd, ssh_port):
        self.ip = ip
        self.user = ssh_user
        self.passwd = ssh_passwd
        self.port = int(ssh_port)
        self.transport = paramiko.Transport(self.ip, self.port)
        self.transport.connect(username=self.user, password=self.passwd)
        self.ssh = paramiko.SSHClient()
        self.ssh._transport = self.transport

    def run_cmd(self, cmd):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            if len(stderr.read()) == 0:
                data = stdout.read()
            else:
                data = stderr.read()
            return data
        except Exception as e:
            self.close_conn()
            Logger().logger(30).error('{ip}: '.format(ip=self.ip) + str(e))
            sys.exit(str(e))

    def close_conn(self):
        self.transport.close()


class OsInfo(RunRomoteCmd):
    def __init__(self, ip, ssh_user, ssh_passwd, ssh_port):
        super(OsInfo, self).__init__(ip, ssh_user, ssh_passwd, ssh_port)
        self.kernel_release = None
        self.a = None
        self.b = None
        self.c = None

    def __get_iops(self):
        devices = self.run_cmd('cat /proc/diskstats').decode()
        io_stat_dict = {}
        for item in devices.split('\n')[:-1]:
            if re.search('loop', item) or re.search('ram', item) or re.search('sr', item):
                pass
            else:
                line_data = item.split()
                if re.search('.\d', line_data[2]):
                    disk_name = line_data[2]
                    read_io = line_data[4]
                    write_io = line_data[8]
                    if disk_name.startswith('dm'):
                        dm_num = disk_name.split('-')[1]
                        pv_data = self.run_cmd('cd /dev/mapper/; dmsetup  ls').decode()
                        for line in pv_data.split('\n')[:-1]:
                            pv_name = line.split()[0]
                            pv_num = line.split()[1].split(':')[1].split(')')[0]
                            if dm_num == pv_num:
                                io_stat_dict[pv_name] = {'read_io': read_io, 'write_io': write_io}
                    else:
                        io_stat_dict[disk_name] = {'read_io': read_io, 'write_io': write_io}
        return io_stat_dict

    def get_iops(self):
        new_io_stat_dict = {}
        io_data1 = self.__get_iops()
        net_tran1 = self.get_net_tran()
        time.sleep(1)
        net_tran2 = self.get_net_tran()
        io_data2 = self.__get_iops()
        for keys in net_tran1.keys():
            for item in net_tran2.keys():
                if keys == item:
                    for i in net_tran1[keys].keys():
                        for j in net_tran2[keys].keys():
                            if i == j:
                                receive = int(net_tran2[keys]['Receive']) - int(net_tran1[keys]['Receive'])
                                transmit = int(net_tran2[keys]['Transmit']) - int(net_tran1[keys]['Transmit'])
                                new_io_stat_dict[keys] = {'Receive': receive, 'Transmit': transmit}

        for keys in io_data2.keys():
            for item in io_data1.keys():
                if keys == item:
                    read_io = int(io_data2[keys]['read_io']) - int(io_data1[keys]['read_io'])
                    write_io = int(io_data2[keys]['write_io']) - int(io_data1[keys]['write_io'])
                    new_io_stat_dict[keys] = {'write_io': write_io, 'read_io': read_io}
        return new_io_stat_dict

    def get_disk_info(self):
        use_stat_dict = {}
        data = self.run_cmd("df -TmP")
        if len(data) != 0:
            disk_data = data.decode().split('\n')
            for line in disk_data[1:-1]:
                file_system_type = line.split()[1]
                total_mb = line.split()[2]
                used_mb = line.split()[3]
                use_per = line.split()[5].split('%')[0]
                avail_mb = line.split()[4]
                mount_on = line.split()[6]
                mount_disk = line.split()[0]
                use_stat_dict[mount_disk] = {"file_system_type": file_system_type,
                                             "total_mb": total_mb,
                                             "used_mb": used_mb,
                                             "use_per": use_per,
                                             "avail_mb": avail_mb,
                                             "mount_on": mount_on
                                             }
        return use_stat_dict

    def get_mem_info(self):
        mem_dict = {}
        data = self.run_cmd('cat /proc/meminfo').decode()
        for line in data.split('\n')[:-1]:
            if line.split()[0] in ('MemTotal:', 'MemFree:', 'Buffers:', 'Cached:',
                                   'SwapCached:', 'SwapTotal:', 'SwapFree:'):
                mem_dict[line.split()[0].split(':')[0]] = int(int(line.split()[1])/1024)
        free_mem = mem_dict['Buffers'] + mem_dict['Cached'] + mem_dict['MemFree']
        mem_use_per = 100 - int(free_mem / mem_dict['MemTotal'] * 100)
        mem_dict['mem_use_per'] = mem_use_per
        return mem_dict

    def get_cpu_info(self):
        cpu_load_dict = {}

        # 获取 cpu 核心数
        info_data = self.run_cmd('cat /proc/cpuinfo').decode()
        for line in info_data.split('\n')[:-1]:
            if line == '':
                pass
            elif line.split(':')[0].strip() == 'processor':
                core_num = int(line.split(':')[1].strip()) + 1
                cpu_load_dict["core"] = int(core_num)

        # 获取负载情况
        load_data = self.run_cmd('uptime').decode()
        for line in load_data.split('\n')[:-1]:
            uptime_day = line.split(',')[0].split()[2]
            uptime_hour = line.split(',')[1]
            load_1 = line.split(':')[-1].split(',')[0]
            load_5 = line.split(':')[-1].split(',')[1]
            load_15 = line.split(':')[-1].split(',')[2]
            uptime = uptime_day + ' days ' + uptime_hour
            cpu_load_dict['uptime'] = uptime
            cpu_load_dict['load_1'] = float(load_1)
            cpu_load_dict['load_5'] = float(load_5)
            cpu_load_dict['load_15'] = float(load_15.strip())

        return cpu_load_dict

    def get_net_tran(self):
        net_tran = {}
        data = self.run_cmd('cat /proc/net/dev').decode()
        for line in data.split('\n')[2:-1]:
            dev = line.split(':')[0].strip()
            if not dev.startswith('lo'):
                receive = line.split(':')[1].split()[0]
                transmit = line.split(':')[1].split()[8]
                net_tran['net_' + dev] = {'Receive': receive, 'Transmit': transmit}
        return net_tran

    def get_os_version(self):
        version_dict = {}
        data = self.run_cmd('uname -a').decode()
        version_dict['os_version'] = data.split()[0] + ' ' + data.split()[-2]
        version_dict['hostname'] = data.split()[1]
        version_dict['kernel_release'] = data.split()[2].split('-')[0]
        return version_dict

    def get_cpu_stat(self):
        """
        CPU times:
        (user, nice, system, idle, iowait, irq, softirq [steal, [guest,[guest_nice]]])
        Last 3 fields may not be available on all Linux kernel versions.
        - user
        - nice (UNIX)
        - system
        - idle
        - iowait (Linux)
        - irq (Linux, FreeBSD)
        - softirq (Linux)
        - steal (Linux >= 2.6.11)
        - guest (Linux >= 2.6.24)
        - guest_nice (Linux >= 3.2.0)
        """
        if not self.kernel_release:
            self.kernel_release = self.get_os_version()['kernel_release']
        self.a, self.b, self.c = self.kernel_release.split('.')
        cpu_stat = {}
        data = self.run_cmd('cat /proc/stat').decode().split('\n')
        for item in data:
            if re.search('^cpu[0-9]+', item):
                cpu_stat_list = item.split()
                cpu_stat[cpu_stat_list[0]] = {
                    'user': cpu_stat_list[1],
                    'nice': cpu_stat_list[2],
                    'system': cpu_stat_list[3],
                    'idle': cpu_stat_list[4],
                    'iowait': cpu_stat_list[5],
                    'irq': cpu_stat_list[6],
                    'softirq': cpu_stat_list[7]
                }
                if int(self.a) == 2 and int(self.c) >= 11:
                    cpu_stat[cpu_stat_list[0]]['steal'] = cpu_stat_list[8]
                if int(self.a) == 2 and int(self.c) >= 24:
                    cpu_stat[cpu_stat_list[0]]['guest'] = cpu_stat_list[9]
                if int(self.a) == 3 and int(self.b) >= 2:
                    cpu_stat[cpu_stat_list[0]]['guest_nice'] = cpu_stat_list[10]
        return cpu_stat


class MySQLBseInfo(object):
    def __init__(self, host, user, passwd, port):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = int(port)
        self.variables_dict = {}
        self.status_dict = {}
        self.slave_info_dict = {}
        self.master_info_dict = {}
        self.my_conn = DBAPI(self.host, self.user, self.passwd, self.port)
        self.__check_sql_mode()

    def get_global_variables(self, name=None):
        """
        :param name: str,list or tuple
        :return:
        """
        variables_dict = {}
        name_list = []
        if not self.variables_dict:
            variables_tuple = self.my_conn.query('show global variables')
            for items in variables_tuple:
                self.variables_dict[items['Variable_name']] = items['Value']
        if name:
            if isinstance(name, str):
                name_list.append(name)
                name = tuple(name_list)
            else:
                name = tuple(name)
            for item in name:
                if self.variables_dict.get(item):
                    variables_dict[item] = self.variables_dict[item]
                else:
                    variables_dict[item] = DataError
        else:
            variables_dict = self.variables_dict
        return variables_dict

    def get_global_status(self, name=None, get_diff=None):
        """
        :param name: str, list or tuple
        :param get_diff:
        :return:
        """
        name_list = []
        if not self.status_dict:
            status_tuple = self.my_conn.query('show global status')
            for items in status_tuple:
                self.status_dict[items['Variable_name']] = items['Value']
        if get_diff:
            status_dict_2 = {}
            status_tuple = self.my_conn.query('show global status')
            for items in status_tuple:
                status_dict_2[items['Variable_name']] = items['Value']

            return status_dict_2

        status_dict = {}

        if name:
            if isinstance(name, str):
                name_list.append(name)
                name = tuple(name_list)
            else:
                name = tuple(name)
            for item in name:
                if self.status_dict.get(item):
                    status_dict[item] = self.status_dict[item]
                else:
                    status_dict[item] = DataError
        else:
            status_dict = self.status_dict
        return status_dict

    def get_slave_info(self):
        if not self.slave_info_dict:
            slave_info_tuple = self.my_conn.query('show slave status')
            if slave_info_tuple:
                self.slave_info_dict = slave_info_tuple[0]
        return self.slave_info_dict

    def get_master_info(self):
        if not self.master_info_dict:
            self.master_info_dict = self.my_conn.query('show master status')[0]
        return self.master_info_dict

    def close(self):
        self.my_conn.close()

    def __check_sql_mode(self):
        mode_str = ''
        sql = "show variables like 'sql_mode'"
        ret = self.my_conn.query(sql)
        sql_mode_list = ret[0]['Value'].split(',')
        if 'ONLY_FULL_GROUP_BY' in sql_mode_list:
            sql_mode_list.remove('ONLY_FULL_GROUP_BY')
            for item in sql_mode_list:
                mode_str += item + ','
            mode_str = mode_str[:-1]
            self.my_conn.conn_dml("set sql_mode='{mode}'".format(mode=mode_str))


class Logger(object):
    def logger(self, log_level):
        """
        logger().level(str(message))
        """

        level = logging.INFO

        if log_level == 10:
            level = logging.DEBUG
        if log_level == 20:
            level = logging.INFO
        if log_level == 30:
            level = logging.WARNING
        if log_level == 40:
            level = logging.ERROR
        if log_level == 50:
            level = logging.CRITICAL
        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'verbose': {
                    'format': "%(asctime)s - [%(levelname)s]  %(message)s",
                    'datefmt': "%c"
                },
            },
            'handlers': {
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose'
                },
                'file': {
                    'level': 'DEBUG',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': BASE_DIR + '/logs/mysql_diagnose.log',
                    'formatter': 'verbose'
                }
            },
            'loggers': {
                '': {
                    'handlers': ['file'],
                    'level': level,
                },
            }
        })

        logger1 = logging.getLogger()

        return logger1


def get_config():
    config = configparser.ConfigParser()
    config.read('./conf/diagnose.cnf', encoding='utf-8')
    section_has = config.has_section('default')
    if not section_has:
        sys.exit("Error: The '[default]' not find")
    processing = config.get("default", "processing")
    host = config.get("default", "host")
    user = config.get("default", "user")
    password = config.get("default", "password")
    port = config.get("default", "port")
    database = config.get("default", "database")
    log_level = config.get("default", "log_level")
    type = config.get("default", "type")

    conf_dict = {
        'processing': processing,
        'user': user,
        'host': host,
        'password': password,
        'port': port,
        'database': database,
        'log_level': log_level,
        'type': type
    }
    return conf_dict
