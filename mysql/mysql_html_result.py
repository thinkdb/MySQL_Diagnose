#!/bin/env python
# -*- coding:utf8 -*-
import time
import re
from mysql.sys_variables_status import SYS_PARM_FILTER


def get_slave_info(mysql_connected_stream):
    slave = mysql_connected_stream.get_slave_info()

    if slave:
        slave_info = "<p>Slave Info</p>" \
                     "<p><table border='1' width='500'><tr>" \
                     "<th class='awrbg' scope='col'>Variables</th>" \
                     "<th class='awrbg' scope='col'>Value</th>" \
                     "</tr>" \
                     "<tr>" \
                     "<td class='awrnc'>Master_Host</td>" \
                     "<td class='awrnc'>{Master_Host}</td>" \
                     "</tr>" \
                     "<tr>" \
                     "<td class='awrc'>Master_User</td>" \
                     "<td class='awrc'>{Master_User}</td>" \
                     "</tr>" \
                     "<tr>" \
                     "<td class='awrnc'>Master_Port</td>" \
                     "<td class='awrnc'>{Master_Port}</td>" \
                     "</tr>" \
                     "<tr>" \
                     "<td class='awrc'>Slave_IO_Running</td>" \
                     "<td class='awrc'>{Slave_IO_Running}</td>" \
                     "</tr>" \
                     "<tr>" \
                     "<td class='awrnc'>Slave_SQL_Running</td>" \
                     "<td class='awrnc'>{Slave_SQL_Running}</td>" \
                     "</tr>" \
                     "<tr>" \
                     "<td class='awrc'>Master_Log_File</td>" \
                     "<td class='awrc'>{Master_Log_File}</td>" \
                     "</tr>" \
                     "<tr>" \
                     "<td class='awrnc'>Relay_Master_Log_File</td>" \
                     "<td class='awrnc'>{Relay_Master_Log_File}</td>" \
                     "</tr>" \
                     "<tr>" \
                     "<td class='awrc'>Read_Master_Log_Pos</td>" \
                     "<td class='awrc'>{Read_Master_Log_Pos}</td>" \
                     "</tr>" \
                     "<tr>" \
                     "<td class='awrnc'>Exec_Master_Log_Pos</td>" \
                     "<td class='awrnc'>{Exec_Master_Log_Pos}</td>" \
                     "</tr>" \
                     "<tr>" \
                     "<td class='awrc'>Relay_Log_File</td>" \
                     "<td class='awrc'>{Relay_Log_File}</td>" \
                     "</tr>" \
                     "<tr>" \
                     "<td class='awrnc'>Relay_Log_Pos</td>" \
                     "<td class='awrnc'>{Relay_Log_Pos}</td>" \
                     "</tr>" \
                     "<tr>" \
                     "<td class='awrc'>Master_Server_Id</td>" \
                     "<td class='awrc'>{Master_Server_Id}</td>" \
                     "</tr>" \
                     "<tr>" \
                     "<td class='awrnc'>Seconds_Behind_Master</td>" \
                     "<td class='awrnc'>{Seconds_Behind_Master}</td>" \
                     "</tr>" \
                     "<tr>" \
                     "<td class='awrc'>Replicate_Do_DB</td>" \
                     "<td class='awrc'>{Replicate_Do_DB}</td>"\
                     "</tr>" \
                     "<tr>" \
                     "<td class='awrnc'>Replicate_Ignore_DB</td>" \
                     "<td class='awrnc'>{Replicate_Ignore_DB}</td>" \
                     "</tr>" \
                     "<tr>" \
                     "<td class='awrc'>Master_Info_File</td>" \
                     "<td class='awrc'>{Master_Info_File}</td>" \
                     "</tr></table></p>".format(Master_Host=slave['Master_Host'],
                                                Master_User=slave['Master_User'],
                                                Master_Port=slave['Master_Port'],
                                                Master_Log_File=slave['Master_Log_File'],
                                                Read_Master_Log_Pos=slave['Read_Master_Log_Pos'],
                                                Relay_Log_File=slave['Relay_Log_File'],
                                                Relay_Log_Pos=slave['Relay_Log_Pos'],
                                                Relay_Master_Log_File=slave['Relay_Master_Log_File'],
                                                Slave_IO_Running=slave['Slave_IO_Running'],
                                                Slave_SQL_Running=slave['Slave_SQL_Running'],
                                                Exec_Master_Log_Pos=slave['Exec_Master_Log_Pos'],
                                                Master_Server_Id=slave['Master_Server_Id'],
                                                Seconds_Behind_Master=slave['Seconds_Behind_Master'],
                                                Master_Info_File=slave['Master_Info_File'],
                                                Replicate_Ignore_DB=slave['Replicate_Ignore_DB'],
                                                Replicate_Do_DB=slave['Replicate_Do_DB']
                                                )
        return slave_info


def get_mysql_base(mysql_connected_stream):
    slave_flag = 'Is not a slave, '
    slave = mysql_connected_stream.get_slave_info()
    if slave:
        slave_flag = 'Is a slave, '

    slave_count = mysql_connected_stream.my_conn.query("select count(*) as num from information_schema.processlist "
                                                       "where COMMAND = 'Binlog Dump' "
                                                       "or COMMAND = 'Binlog Dump GTID';")[0]['num']
    replication = slave_flag + "has {num} slaves connected".format(num=slave_count)
    status_dict = mysql_connected_stream.get_global_status()
    variables_dict = mysql_connected_stream.get_global_variables()

    uptime_info = status_dict['Uptime']
    conn_peak_value = status_dict['Max_used_connections']
    current_time = time.time()
    start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time-int(uptime_info)))
    d, s = divmod(int(uptime_info), 3600*24)
    time_sec = time.strftime('%H:%M:%S', time.localtime(s))
    uptime = '{start_time} (Up {day}+{time_sec})'.format(start_time=start_time,
                                                         day=d,
                                                         time_sec=time_sec)
    version_info = variables_dict['version']
    version_comment = variables_dict['version_comment']
    version = version_info + ' ' + version_comment

    base_info = "<p><table border='1' width='500'><tr>" \
                "<th class='awrbg' scope='col'>Variable</th>" \
                "<th class='awrbg' scope='col'>Value</th>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrnc'>Version</td>" \
                "<td scope='row' class='awrnc'>{Version}</td>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrc'>Started</td>" \
                "<td class='awrc'>{Uptime}</td>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrnc'>Max Connections</td>" \
                "<td class='awrnc'>{Max}</td>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrc'>Current Connections</td>" \
                "<td class='awrc'>{Current}</td>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrnc'>Connection Pack Value</td>" \
                "<td class='awrnc'>{pack}</td>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrc'>Server Character</td>" \
                "<td class='awrc'>{Server}</td>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrnc'>DB Character</td>" \
                "<td class='awrnc'>{DB}</td>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrc'>Port</td>" \
                "<td class='awrc'>{port}</td>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrnc'>Replication</td>" \
                "<td class='awrnc'>{Replication}</td>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrc'>Datadir</td>" \
                "<td class='awrc'>{Datadir}</td>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrnc'>Pidfile</td>" \
                "<td class='awrnc'>{Pidfile}</td>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrc'>Socket</td>" \
                "<td class='awrc'>{Socket}</td>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrnc'>Binlogdir</td>" \
                "<td class='awrnc'>{Binlogdir}</td>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrc'>Binlog Size</td>" \
                "<td class='awrc'>{binlog} MB</td>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrnc'>Innodb Buffer Pool</td>" \
                "<td class='awrnc'>{ibp} MB</td>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrc'>Innodb Log File Size</td>" \
                "<td class='awrc'>{log_file} MB</td>" \
                "</tr>" \
                "<tr>" \
                "<td class='awrnc'>Error Log File</td>" \
                "<td class='awrnc'>{error}</td>" \
                "</tr></table></p>".format(Version=version,
                                           Uptime=uptime,
                                           Max=variables_dict['max_connections'],
                                           Current=status_dict['Threads_connected'],
                                           Server=variables_dict['character_set_server'],
                                           DB=variables_dict['character_set_database'],
                                           Replication=replication,
                                           ibp=int(variables_dict['innodb_buffer_pool_size'])/1024/1024,
                                           port=variables_dict['port'],
                                           Datadir=variables_dict['datadir'],
                                           Pidfile=variables_dict['pid_file'],
                                           Socket=variables_dict['socket'],
                                           Binlogdir=variables_dict['log_bin_basename'],
                                           log_file=variables_dict['innodb_log_files_in_group'] + ' * ' +
                                                    str(int(variables_dict['innodb_log_file_size'])/1024/1024),
                                           binlog=int(variables_dict['max_binlog_size'])/1024/1024,
                                           error=variables_dict['log_error'],
                                           pack=conn_peak_value
                                           )
    return base_info


def get_security_user(mysql_connected_stream):
    version = mysql_connected_stream.my_conn.query("select @@version version")
    version_num = version[0]['version'].split('-')[0].split('.')[1]
    if version_num >= '7':
        # sql = "SELECT user, host FROM mysql.user where host = '%'"
        sql = "SELECT user, host FROM mysql.user WHERE authentication_string = '' " \
              "OR authentication_string IS NULL " \
              "OR host = '%';"
    else:
        sql = "SELECT user, host FROM mysql.user WHERE password = '' OR password IS NULL OR host = '%';"

    user_info = mysql_connected_stream.my_conn.query(sql)
    table_html = "<p>Unsafe Account Info</p>" \
                 "<p><table border='1' width='300'><tr>" \
                 "<th class='awrbg' scope='col'>User</th>" \
                 "<th class='awrbg' scope='col'>Host</th></tr>"
    emp_str = ''
    if user_info:
        for id, item in enumerate(user_info):
            a, b = divmod(id, 2)
            if b == 1:
                class_style = "awrc"
            else:
                class_style = "awrnc"

            user_html = "<tr>" \
                        "<td class={class_style}>{user}</td>" \
                        "<td class={class_style}>{host}</td></tr>".format(user=item['user'],
                                                                          host=item['host'],
                                                                          class_style=class_style)
            emp_str += user_html
        return table_html + emp_str + "</table>"


def get_innodb_status(mysql_connected_stream):
    lsn = 0
    last_checkpoint = 0
    history_list_len = 0
    status = mysql_connected_stream.my_conn.query('show engine innodb status')[0]
    status_info_list = status['Status'].split('\n')
    for item in status_info_list:
        if item.startswith('Log flushed up to'):
            lsn = item.split()[-1]
        if item.startswith('Last checkpoint at'):
            last_checkpoint = item.split()[-1]
        if item.startswith('History list length'):
            history_list_len = item.split()[-1]

    checkpoint_age = int(lsn) - int(last_checkpoint)
    innodb_status = mysql_connected_stream.get_global_status()
    innodb_varables = mysql_connected_stream.get_global_variables()

    all_read_request = int(innodb_status['Innodb_buffer_pool_reads']) + \
                       int(innodb_status['Innodb_buffer_pool_read_requests'])
    write_request = int(innodb_status['Innodb_buffer_pool_write_requests'])

    write_per = write_request / (all_read_request + write_request) * 100
    read_per = 100 - write_per

    read_write = '{:.2f}% / '.format(read_per) + '{:.2f}%'.format(write_per)

    ibp_hint = int(innodb_status['Innodb_buffer_pool_read_requests'])/all_read_request * 100
    ibp_use_per = int(innodb_status['Innodb_buffer_pool_bytes_data'])/int(innodb_varables['innodb_buffer_pool_size']) * 100
    dirty_per = int(innodb_status['Innodb_buffer_pool_bytes_dirty']) / int(innodb_varables['innodb_buffer_pool_size']) * 100
    log_file_size = innodb_varables['innodb_log_files_in_group'] + '*' + \
                    str(int(innodb_varables['innodb_log_file_size'])/1024/1024)

    table_html = "<p>Innodb Info</p>" \
                 "<p><table border='1' width='500'><tr>" \
                 "<th class='awrbg' scope='col'>Variable</th>" \
                 "<th class='awrbg' scope='col'>Value</th>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrnc'>Buffer Pool Size</td>" \
                 "<td class='awrnc'>{ibp} MB</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrc'>Buffer Pool Instances</td>" \
                 "<td class='awrc'>{ibp_ins}</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrnc'>Data File Path</td>" \
                 "<td class='awrnc'>{data_file_path}</td>"\
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrc'>Page Size</td>" \
                 "<td class='awrc'>{page_size} KB</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrnc'>Log File Size</td>" \
                 "<td class='awrnc'>{log_file_size} MB</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrc'>Txn Isolation Level</td>" \
                 "<td class='awrc'>{tx_iso}</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrnc'>Flush Method</td>" \
                 "<td class='awrnc'>{flush_method}</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrc'>Checksums</td>" \
                 "<td class='awrc'>{checksums}</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrnc'>File Per Table</td>" \
                 "<td class='awrnc'>{file_per_table}</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrc'>Flush Log At Commit</td>" \
                 "<td class='awrc'>{trx_commit}</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrnc'>Flush Neighbors</td>" \
                 "<td class='awrnc'>{neighbors}</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrc'>Locks Unsafe For Binlog</td>" \
                 "<td class='awrc'>{locks_unsafe_for_binlog}</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrnc'>Max Dirty Pages Pct</td>" \
                 "<td class='awrnc'>{max_dirty_pages_pct}</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrc'>Read Io Threads</td>" \
                 "<td class='awrc'>{read_io_threads}</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrnc'>Write Io Threads</td>" \
                 "<td class='awrnc'>{write_io_threads}</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrc'>Log Buffer Size</td>" \
                 "<td class='awrc'>{log_buffer_size} MB</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrnc'>Buffer Pool Hint</td>" \
                 "<td class='awrnc'>{ibp_hint}%</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrc'>Buffer Pool Use Per</td>" \
                 "<td class='awrc'>{ibp_use_per}%</td>"\
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrnc'>Buffer Pool Dirty Per</td>" \
                 "<td class='awrnc'>{dirty_per}%</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrc'>Checkpoint Age</td>" \
                 "<td class='awrc'>{age}</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrnc'>History List Len</td>" \
                 "<td class='awrnc'>{his}</td>" \
                 "</tr>" \
                 "<tr>" \
                 "<td class='awrc'>Read / Write</td>" \
                 "<td class='awrc'>{read}</td>" \
                 "</tr></table></p>".format(ibp=int(innodb_varables['innodb_buffer_pool_size'])/1024/1024,
                                            ibp_ins=innodb_varables['innodb_buffer_pool_instances'],
                                            data_file_path=innodb_varables['innodb_data_file_path'],
                                            log_buffer_size=int(innodb_varables['innodb_log_buffer_size'])/1024/1024,
                                            write_io_threads=innodb_varables['innodb_write_io_threads'],
                                            read_io_threads=innodb_varables['innodb_read_io_threads'],
                                            max_dirty_pages_pct=innodb_varables['innodb_max_dirty_pages_pct'],
                                            neighbors=innodb_varables['innodb_flush_neighbors'],
                                            trx_commit=innodb_varables['innodb_flush_log_at_trx_commit'],
                                            file_per_table=innodb_varables['innodb_file_per_table'],
                                            checksums=innodb_varables['innodb_checksums'],
                                            flush_method=innodb_varables['innodb_flush_method'],
                                            locks_unsafe_for_binlog=innodb_varables['innodb_locks_unsafe_for_binlog'],
                                            tx_iso=innodb_varables['tx_isolation'],
                                            page_size=int(innodb_varables['innodb_page_size'])/1024,
                                            log_file_size=log_file_size,
                                            ibp_hint='{:.2f}'.format(ibp_hint),
                                            ibp_use_per='{:.2f}'.format(ibp_use_per),
                                            dirty_per='{:.2f}'.format(dirty_per),
                                            age=checkpoint_age,
                                            his=history_list_len,
                                            read=read_write
                                            )
    return table_html


def get_binlog_info(mysql_connected_stream, os_connected_stream):
    binlog_info = mysql_connected_stream.my_conn.query('show binary logs;')
    size = 0
    binlog_ignore_db = ''
    binlog_do_db = ''
    binlog_num = len(binlog_info)
    for item in binlog_info:
        size += item['File_size']
    variable_dict = mysql_connected_stream.get_global_variables()

    my_cnf_info = collect_my_cnf(os_connected_stream)
    for item in my_cnf_info:
        for m_k in my_cnf_info[item]:
            if m_k == '[mysqld]':
                for k in my_cnf_info[item]['[mysqld]'].keys():
                    if k.lower() in ['replicate_ignore_db', 'replicate-ignore-db']:
                        binlog_ignore_db = my_cnf_info[item]['[mysqld]']['k']
                    if k.lower() in ['replicate-do-db', 'replicate_do_db']:
                        binlog_do_db = my_cnf_info[item]['[mysqld]']['k']

    binlog_html = "<p>Binlog Info</p>" \
                  "<p><table border='1' width='300'><tr>" \
                  "<th class='awrbg' scope='col'>Variable</th>" \
                  "<th class='awrbg' scope='col'>Value</th>" \
                  "</tr>" \
                  "<tr>" \
                  "<td class='awrnc'>Binlog Number</td>" \
                  "<td class='awrnc'>{number}</td>" \
                  "</tr>" \
                  "<tr>" \
                  "<td class='awrc'>Total Size</td>" \
                  "<td class='awrc'>{size} MB</td>" \
                  "</tr>" \
                  "<tr>" \
                  "<td class='awrnc'>Format</td>" \
                  "<td class='awrnc'>{Format}</td>" \
                  "</tr>" \
                  "<tr>" \
                  "<td class='awrc'>Expire Logs Days</td>" \
                  "<td class='awrc'>{expire_logs_days}</td>" \
                  "</tr>" \
                  "<tr>" \
                  "<td class='awrnc'>Sync Binlog</td>" \
                  "<td class='awrnc'>{sync_binlog}</td>"\
                  "</tr>" \
                  "<tr>" \
                  "<td class='awrc'>Server Id</td>" \
                  "<td class='awrc'>{server_id}</td>" \
                  "</tr>" \
                  "<tr>" \
                  "<td class='awrnc'>Binlog Do Db</td>" \
                  "<td class='awrnc'>{binlog_do_db}</td>"\
                  "</tr>" \
                  "<tr>" \
                  "<td class='awrc'>Binlog Ignore Db</td>" \
                  "<td class='awrc'>{binlog_ignore_db}</td>" \
                  "</tr></table></p>".format(server_id=variable_dict['server_id'],
                                             sync_binlog=variable_dict['sync_binlog'],
                                             expire_logs_days=variable_dict['expire_logs_days'],
                                             Format=variable_dict['binlog_format'],
                                             size='{:.2f}'.format(size/1024/1024),
                                             number=binlog_num,
                                             binlog_ignore_db=binlog_ignore_db,
                                             binlog_do_db=binlog_do_db
                                             )
    return binlog_html


def collect_my_cnf(os_connected_stream):
    my_cnf_dict = {}
    my_cnf_list = ['/etc/my.cnf', '/etc/mysql/my.cnf', '/usr/local/mysql/etc/my.cnf']
    default_file = os_connected_stream.run_cmd('ps -ef | grep -v mysqld_safe | grep defaults-file | grep -v grep')
    default_file_list = default_file.decode().split('--')
    if default_file_list:
        for item in default_file_list:
            if item.startswith('defaults-file'):
                my_cnf_list.append(item.split('=')[1].strip())
    for item in set(my_cnf_list):
        file_dict = {}

        my_cnf_flag = os_connected_stream.run_cmd('ls {file}'.format(file=item))
        if my_cnf_flag:
            my_cnf_dict[item] = file_dict
            my_cnf_stream = os_connected_stream.run_cmd('cat {file}'.format(file=item))
            for line in my_cnf_stream.decode().split('\n'):
                if line and line[0] != '#':
                    if line[0] == "[":
                        b_dict = {}
                        file_dict[line] = b_dict
                    else:
                        if re.search('=', line):
                            k, v = line.split('=')
                            b_dict[k.strip()] = v.strip()
                        else:
                            b_dict[line] = ''
    return my_cnf_dict


def get_my_cnf(os_connected_stream):
    my_cnf_file = collect_my_cnf(os_connected_stream)
    conf_content = ''
    cont_html = ''
    table_head = "<p>Configuration File Info</p>" \
                 "<table border='1' width='500'>"
    conf_head = ""
    table_body = ""
    # 读取配置文件名
    for item in my_cnf_file:
        conf_head += "<tr><td class='awrmbg' scope='col' colspan=2>{conf_name}</td></tr>".format(conf_name=item)
        # 读取[mysqld]类似的模块
        for k in my_cnf_file[item]:
            # 读取模块下的内容
            mode_html = "<tr><td class='awrmbg' >{key}</td><td class='awrbg' scope='col'></td></tr>".format(key=k)
            # [mysqld] 里面的参数值
            for id, m in enumerate(my_cnf_file[item][k]):
                a, b = divmod(id, 2)
                if b == 0:
                    class_style = 'awrnc'
                else:
                    class_style = 'awrc'
                conf_content += "<tr><td class={class_style}>{key}</td>" \
                                "<td class={class_style}>{value}</td></tr>".format(class_style=class_style,
                                                                                   key=m,
                                                                                   value=my_cnf_file[item][k][m])
            cont_html += mode_html + conf_content
            conf_content = ''
        table_body += conf_head + cont_html
        conf_head = ''
        cont_html = ''
    return table_head+table_body+'</table>'


def get_tps_qps(mysql_connected_stream, times=1, interval=1):
    table_head = "<p>Current Operation State</p>" \
                 "<table border='1' width='800'>" \
                 "<tr>" \
                 "<th></th>" \
                 "<th></th>" \
                 "<th class='awrbg' scope='col' colspan=4>MySQL Command Status</th>" \
                 "<th class='awrbg' scope='col' colspan=4>Innodb Row Operation</th>" \
                 "</tr>" \
                 "<tr>" \
                 "<th class='awrbg' scope='col'>Time</td>" \
                 "<th class='awrbg' scope='col'>QPS</td>" \
                 "<th class='awrbg' scope='col'>Select</td>" \
                 "<th class='awrbg' scope='col'>Update</td>" \
                 "<th class='awrbg' scope='col'>Insert</td>" \
                 "<th class='awrbg' scope='col'>Delete</td>" \
                 "<th class='awrbg' scope='col'>Reads</td>" \
                 "<th class='awrbg' scope='col'>Update</td>" \
                 "<th class='awrbg' scope='col'>Insert</td>" \
                 "<th class='awrbg' scope='col'>Delete</td>" \
                 "</tr>"
    temp_html = ''
    status_list = tps_qps(mysql_connected_stream, times, interval)
    for status in status_list:
        tr_html = "<tr>" \
                  "<td class='{class_style}'>{time}</td>" \
                  "<td class='{class_style}'>{qps}</td>" \
                  "<td class='{class_style}'>{select}</td>" \
                  "<td class='{class_style}'>{update}</td>" \
                  "<td class='{class_style}'>{insert}</td>" \
                  "<td class='{class_style}'>{delete}</td>" \
                  "<td class='{class_style}'>{innodb_read}</td>" \
                  "<td class='{class_style}'>{innodb_update}</td>" \
                  "<td class='{class_style}'>{innodb_insert}</td>" \
                  "<td class='{class_style}'>{innodb_delete}</td>" \
                  "</tr>".format(class_style=status['class_style'],
                                 time=status['time'],
                                 qps=status['qps'],
                                 select=status['select'],
                                 update=status['update'],
                                 insert=status['insert'],
                                 delete=status['delete'],
                                 innodb_read=status['ibp_read'],
                                 innodb_update=status['ibp_update'],
                                 innodb_insert=status['ibp_insert'],
                                 innodb_delete=status['ibp_delete']
                                 )
        temp_html += tr_html
        # temp_html.extend(tr_html)
    return table_head+temp_html+"</table>"


def tps_qps(mysql_connected_stream, times, interval):
    if times > 10:
        times = 10
    status_dict = {}
    temp_status = ''
    for item in range(times+1):
        if item % 2 == 0 and item > 0:
            status_dict['class_style'] = 'awrc'
        else:
            status_dict['class_style'] = 'awrnc'
        if not temp_status:
            mysql_status_1 = mysql_connected_stream.get_global_status(get_diff=1)
            mysql_status_2 = mysql_status_1
            temp_status = mysql_status_2
        else:
            time.sleep(interval)
            current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            mysql_status_1 = temp_status
            mysql_status_2 = mysql_connected_stream.get_global_status(get_diff=1)
            status_dict['time'] = current_time
            status_dict['select'] = int(mysql_status_2['Com_insert']) - int(mysql_status_1['Com_insert'])
            status_dict['update'] = int(mysql_status_2['Com_update']) - int(mysql_status_1['Com_update'])
            status_dict['delete'] = int(mysql_status_2['Com_delete']) - int(mysql_status_1['Com_delete'])
            status_dict['insert'] = int(mysql_status_2['Com_insert']) - int(mysql_status_1['Com_insert'])
            status_dict['qps'] = int(mysql_status_2['Queries']) - int(mysql_status_1['Queries'])
            status_dict['ibp_delete'] = int(mysql_status_2['Innodb_rows_deleted']) - int(mysql_status_1[
                                                                                             'Innodb_rows_deleted'])
            status_dict['ibp_insert'] = int(mysql_status_2['Innodb_rows_inserted']) - int(mysql_status_1[
                                                                                              'Innodb_rows_inserted'])
            status_dict['ibp_read'] = int(mysql_status_2['Innodb_rows_read']) - int(mysql_status_1[
                                                                                        'Innodb_rows_read'])
            status_dict['ibp_update'] = int(mysql_status_2['Innodb_rows_updated']) - int(mysql_status_1[
                                                                                             'Innodb_rows_updated'])
            temp_status = mysql_status_2
            yield status_dict
            status_dict = {}


def get_not_primary_key(mysql_connected_stream):
    table_head = "<p>Table information without a primary key</p>" \
                 "<table border='1' width='300'>" \
                 "<tr>" \
                 "<th class='awrbg' scope='col'>Schema</th>" \
                 "<th class='awrbg' scope='col'>Name</th>" \
                 "</tr>"
    cont_html = ""
    sql = """
    select  a.table_schema, a.table_name
    from information_schema.tables a
    left join (select table_name
    from information_schema.STATISTICS
    where table_schema not in ("INFORMATION_SCHEMA" ,"PERFORMANCE_SCHEMA", "MYSQL", "SYS")
    and INDEX_NAME = 'PRIMARY') b
    on a.table_name = b.table_name
    where  a.table_schema not in ("INFORMATION_SCHEMA" ,"PERFORMANCE_SCHEMA", "MYSQL", "SYS")
    and b.table_name is null;
    """
    ret = mysql_connected_stream.my_conn.query(sql)
    if ret:
        for id, item in enumerate(ret):
            if id % 2 == 0:
                class_style = 'awrnc'
            else:
                class_style = 'awrc'
            cont_html += "<tr><td class='{class_style}'>{schema}</td>" \
                         "<td class='{class_style}'>{name}</td></tr>".format(schema=item['table_schema'],
                                                                             name=item['table_name'],
                                                                             class_style=class_style)

        return table_head + cont_html + "</table>"


def get_not_innodb_tables(mysql_connected_stream):
    table_head = "<p>Not INNODB Engine Tables</p>" \
                 "<table border='1' width='300'>" \
                 "<tr>" \
                 "<th class='awrbg' scope='col'>Schema</th>" \
                 "<th class='awrbg' scope='col'>Name</th>" \
                 "<th class='awrbg' scope='col'>Engine</th>" \
                 "</tr>"
    cont_html = ""
    sql = """
    SELECT TABLE_SCHEMA,TABLE_NAME,ENGINE FROM
    INFORMATION_SCHEMA.TABLES WHERE
    ENGINE != 'innodb' AND
    TABLE_SCHEMA NOT IN
    ("INFORMATION_SCHEMA" ,"PERFORMANCE_SCHEMA", "MYSQL", "SYS");
    """
    ret = mysql_connected_stream.my_conn.query(sql)
    if ret:
        for id, item in enumerate(ret):
            if id % 2 == 0:
                class_style = 'awrnc'
            else:
                class_style = 'awrc'
            cont_html += "<tr><td class='{class_style}'>{schema}</td>" \
                         "<td class='{class_style}'>{name}</td>" \
                         "<td class='{class_style}'>{engine}</td>" \
                         "</tr>".format(schema=item['TABLE_SCHEMA'],
                                        name=item['TABLE_NAME'],
                                        engine=item['ENGINE'],
                                        class_style=class_style)
        return table_head + cont_html + "</table>"


def get_auto_increment(mysql_connected_stream):
    """如果有结果，需要根据column_type 中的值去判断是否要设置警告"""
    sql = """
    SELECT t.table_schema, t.table_name, t.engine, ifnull(t.auto_increment,0) as auto_increment, c.data_type, c.column_type
    FROM information_schema.tables t, information_schema.columns c
    where t.TABLE_SCHEMA not in ("INFORMATION_SCHEMA" ,"PERFORMANCE_SCHEMA", "MYSQL", "SYS")
    and t.table_name = c.table_name
    and t.table_schema = c.table_schema
    and c.extra='auto_increment'
    having(auto_increment) > 2142483647;
    """

    """
    int: 2147483647, 4294967295
    bigint: 9223372036854775807, 18446744073709551615
    """

    table_head = "<p>Auto Increment Info</p>" \
                 "<table border='1' width='800'>" \
                 "<tr>" \
                 "<th class='awrbg' scope='col'>Schema</th>" \
                 "<th class='awrbg' scope='col'>Name</th>" \
                 "<th class='awrbg' scope='col'>Engine</th>" \
                 "<th class='awrbg' scope='col'>Auto Increment</th>" \
                 "<th class='awrbg' scope='col'>Available Id</th>" \
                 "<th class='awrbg' scope='col'>Data Type</th>" \
                 "<th class='awrbg' scope='col'>Column Type</th>" \
                 "</tr>"
    cont_html = ""

    ret = mysql_connected_stream.my_conn.query(sql)
    if ret:
        for id, item in enumerate(ret):
            if id % 2 == 0:
                class_style = 'awrnc'
            else:
                class_style = 'awrc'

            if item['data_type'] == 'int':
                if len(item['column_type'].split()) > 1 and item['column_type'].split()[1].lower() == 'unsigned':
                    diff = 4294967295-int(item['auto_increment'])
                else:
                    diff = 2147483647 - int(item['auto_increment'])
            if item['data_type'] == 'bigint':
                if len(item['column_type'].split()) > 1 and item['column_type'].split()[1].lower() == 'unsigned':
                    diff = 18446744073709551615-int(item['auto_increment'])
                else:
                    diff = 9223372036854775807 - int(item['auto_increment'])
            if diff < 4000000:
                cont_html += "<tr><td class='{class_style}'>{schema}</td>" \
                             "<td class='{class_style}'>{name}</td>" \
                             "<td class='{class_style}'>{engine}</td>" \
                             "<td class='{class_style}'>{Auto}</td>" \
                             "<td class='{class_style}'>{available}</td>" \
                             "<td class='{class_style}'>{Data}</td>" \
                             "<td class='{class_style}'>{Column}</td>" \
                             "</tr>".format(schema=item['table_schema'],
                                            name=item['table_name'],
                                            engine=item['engine'],
                                            Auto=item['auto_increment'],
                                            Data=item['data_type'],
                                            Column=item['column_type'],
                                            available=diff,
                                            class_style=class_style)

                return table_head + cont_html + "</table>"


def get_routines(mysql_connected_stream):
    sql = """
    select routine_schema, routine_name, routine_type
    from information_schema.routines
    where routine_schema not in ('information_schema', 'sys', 'performance_schema', 'mysql')
    union
    select  trigger_schema , trigger_name, 'TRIGGER'
    from information_schema.triggers
    where trigger_schema not in ('information_schema', 'sys', 'performance_schema', 'mysql');
    """

    table_head = "<p>Routines, Triggers And Procedures Info</p>" \
                 "<table border='1' width='300'>" \
                 "<tr>" \
                 "<th class='awrbg' scope='col'>Schema</th>" \
                 "<th class='awrbg' scope='col'>Name</th>" \
                 "<th class='awrbg' scope='col'>Engine</th>" \
                 "</tr>"
    cont_html = ""

    ret = mysql_connected_stream.my_conn.query(sql)
    if ret:
        for id, item in enumerate(ret):
            if id % 2 == 0:
                class_style = 'awrnc'
            else:
                class_style = 'awrc'
            cont_html += "<tr><td class='{class_style}'>{schema}</td>" \
                         "<td class='{class_style}'>{name}</td>" \
                         "<td class='{class_style}'>{type}</td>" \
                         "</tr>".format(schema=item['routine_schema'],
                                        name=item['routine_name'],
                                        type=item['routine_type'],
                                        class_style=class_style)
        return table_head + cont_html + "</table>"


def get_engine_table_info(mysql_connected_stream):
    sql = """
    select ifnull(sum(data_length)+sum(index_length), 0) size, ifnull(engine, 'View') engine_name, count(*) as table_count, table_schema
    from information_schema.tables
    where table_schema not in ('information_schema', 'sys', 'performance_schema', 'mysql')
    group by engine_name
    """
    ret = mysql_connected_stream.my_conn.query(sql)
    table_head = "<p>Count the number and size of tables per engine</p>" \
                 "<table border='1' width='300'>" \
                 "<tr>" \
                 "<th class='awrbg' scope='col'>Schema</th>" \
                 "<th class='awrbg' scope='col'>Engine</th>" \
                 "<th class='awrbg' scope='col'>Table count</th>" \
                 "<th class='awrbg' scope='col'>Size (MB)</th>" \
                 "</tr>"
    cont_html = ""
    if ret:
        for id, item in enumerate(ret):
            if id % 2 == 0:
                class_style = 'awrnc'
            else:
                class_style = 'awrc'
            cont_html += "<tr><td class='{class_style}'>{schema}</td>" \
                         "<td class='{class_style}'>{engine}</td>" \
                         "<td class='{class_style}'>{count}</td>" \
                         "<td class='{class_style}'>{size}</td>" \
                         "</tr>".format(schema=item['table_schema'],
                                        engine=item['engine_name'],
                                        count=item['table_count'],
                                        size='{:.2f}'.format(int(item['size'])/1024/1024),
                                        class_style=class_style)
        return table_head + cont_html + "</table>"


def get_important_variables(mysql_connected_stream):
    ret = mysql_connected_stream.get_global_variables(SYS_PARM_FILTER)

    table_head = "<p>Important variables</p>" \
                 "<table border='1' width='300'>" \
                 "<tr>" \
                 "<th class='awrbg' scope='col'>Name</th>" \
                 "<th class='awrbg' scope='col'>Value</th>" \
                 "</tr>"
    cont_html = ""

    if ret:
        for id, item in enumerate(ret):
            if id % 2 == 0:
                class_style = 'awrnc'
            else:
                class_style = 'awrc'
            cont_html += "<tr><td class='{class_style}'>{name}</td>" \
                         "<td class='{class_style}'>{value}</td>" \
                         "</tr>".format(name=item,
                                        value=ret[item],
                                        class_style=class_style)
        return table_head + cont_html + "</table>"


def performance_analyse(mysql_connected_stream):
    my_status = mysql_connected_stream.get_global_status()
    status_list = {}

    key_read_requests = int(my_status['Key_read_requests'])
    if key_read_requests:
        key_buffer_read_hit = "{:.2f}%".format((1-int(my_status['Key_reads'])/key_read_requests) * 100)
    else:
        key_buffer_read_hit = '100%'
    key_write_requests = int(my_status['Key_write_requests'])
    if key_write_requests:
        key_buffer_write_hit = "{:.2f}%".format((1-int(my_status['Key_writes'])/key_write_requests) * 100)
    else:
        key_buffer_write_hit = '100%'
    binlog_buffer = my_status['Binlog_cache_disk_use']  # 如果 Binlog_cache_disk_use 不为0， 则要加大 binlog_cache_size
    innodb_log_waits = my_status['Innodb_log_waits']  # Innodb_log_waits值不等于0的话，表明 innodblog  buffer 因为空间不足而等待
    # 这个值越小越好
    disk_tmp_table_per = "{:.2f}%".format(int(my_status['Created_tmp_disk_tables'])/(int(my_status['Created_tmp_disk_tables']) +
                                                                                     int(my_status['Created_tmp_tables'])) * 100)

    # 越小，就要增加 thread_cache_size 值
    thread_cache_hit = "{:.2f}%".format((1 - int(my_status['Threads_created'])/int(my_status['Connections'])) * 100)
    handler_read_first = my_status['Handler_read_first']  # 如果较高，它建议服务器正执行大量全索引扫描
    handler_read_key = my_status['Handler_read_key']  # 如果较高，说明查询和表的索引正确
    handler_read_next = my_status['Handler_read_next']  # 按照键顺序读下一行的请求数。如果你用范围约束或如果执行索引扫描来查询索引列，该值增加。
    handler_read_prev = my_status['Handler_read_prev']  # 按照键顺序读前一行的请求数。该读方法主要用于优化ORDER BY … DESC。
    handler_read_rnd = my_status['Handler_read_rnd']  # 值过大，表示全表扫描的可能性更大，没有正确使用索引
    handler_read_rnd_next = my_status['Handler_read_rnd_next']  # 没有正确使用索引
    table_locks_waited = my_status['Table_locks_waited']   # 不能立即获得的表的锁的次数
    sort_merge_passes = my_status['Sort_merge_passes']   # 排序算法已经执行的合并的数量。如果这个变量值较大，应考虑增加sort_buffer_size系统变量的值
    slow_queries = my_status['Slow_queries']   # 查询时间超过long_query_time秒的查询的个数。
    select_full_join = my_status['Select_full_join']   # 查询时间超过long_query_time秒的查询的个数。
    select_range_check = my_status['Select_range_check']   # 在每一行数据后对键值进行检查的不带键值的联接的数量。如果不为0，你应仔细检查表的索引。
    qcache_hits = my_status['Qcache_hits']
    qpened_table_definitions = my_status['Opened_table_definitions']   # 已经缓存的.frm文件数量
    open_table_definitions = my_status['Open_table_definitions']   # 当前缓存的.frm文件数量
    opened_tables = my_status['Opened_tables']  # 已经打开的表的数量，如果Opened_tables较大，table_cache值可能太小。
    open_tables = my_status['Open_tables']  # 当前打开的表数量
    opened_files = my_status['Opened_files']  # 文件打开的数量。不包括诸如套接字或管道其他类型的文件。也不包括存储引擎用来做自己的内部功能的文件。
    open_files = my_status['Open_files']  # 当前打开的文件的数目
    innodb_os_log_pending_writes = my_status['Innodb_os_log_pending_writes']  # 值过大，增加 log_buffer_size

    status_list['key_buffer_read_hit'] = key_buffer_read_hit
    status_list['key_buffer_write_hit'] = key_buffer_write_hit
    status_list['binlog_buffer'] = binlog_buffer
    status_list['innodb_log_waits'] = innodb_log_waits
    status_list['disk_tmp_table_per'] = disk_tmp_table_per
    status_list['thread_cache_hit'] = thread_cache_hit
    status_list['handler_read_first'] = handler_read_first
    status_list['handler_read_key'] = handler_read_key
    status_list['handler_read_next'] = handler_read_next
    status_list['handler_read_prev'] = handler_read_prev
    status_list['handler_read_rnd'] = handler_read_rnd
    status_list['handler_read_rnd_next'] = handler_read_rnd_next
    status_list['table_locks_waited'] = table_locks_waited
    status_list['sort_merge_passes'] = sort_merge_passes
    status_list['slow_queries'] = slow_queries
    status_list['select_full_join'] = select_full_join
    status_list['select_range_check'] = select_range_check
    status_list['qcache_hits'] = qcache_hits
    status_list['opened_table_definitions'] = qpened_table_definitions
    status_list['open_table_definitions'] = open_table_definitions
    status_list['opened_tables'] = opened_tables
    status_list['open_tables'] = open_tables
    status_list['opened_files'] = opened_files
    status_list['open_files'] = open_files
    status_list['innodb_os_log_pending_writes'] = innodb_os_log_pending_writes
    status_list['aborted_clients'] = my_status['Aborted_clients']
    status_list['aborted_connects'] = my_status['Aborted_connects']

    table_head = "<p>Performance Index</p>" \
                 "<table border='1' width='300'>" \
                 "<tr>" \
                 "<th class='awrbg' scope='col'>Name</th>" \
                 "<th class='awrbg' scope='col'>Value</th>" \
                 "</tr>"
    cont_html = ""

    for id, item in enumerate(status_list):
        if id % 2 == 0:
            class_style = 'awrnc'
        else:
            class_style = 'awrc'
        cont_html += "<tr><td class='{class_style}'>{name}</td>" \
                     "<td class='{class_style}'>{value}</td>" \
                     "</tr>".format(name=item,
                                    value=status_list[item],
                                    class_style=class_style)
    return table_head + cont_html + "</table>"


def get_current_connection(mysql_connected_stream):
    sql = """
    select SUBSTRING_INDEX(host,':',1) as connect_server,
    user connect_user, db connect_db,
    count(SUBSTRING_INDEX(host,':',1)) as connect_count
    from information_schema.processlist
    where db is not null and db!='information_schema' and db !='performance_schema' group by connect_server ;
    """

    ret = mysql_connected_stream.my_conn.query(sql)

    table_head = "<p>Current Connection Info</p>" \
                 "<table border='1' width='500'>" \
                 "<tr>" \
                 "<th class='awrbg' scope='col'>Connect Server</th>" \
                 "<th class='awrbg' scope='col'>Connect User</th>" \
                 "<th class='awrbg' scope='col'>Connect DB</th>" \
                 "<th class='awrbg' scope='col'>Connect Count</th>" \
                 "</tr>"
    cont_html = ""

    if ret and not isinstance(ret, str):
        for id, item in enumerate(ret):
            if id % 2 == 0:
                class_style = 'awrnc'
            else:
                class_style = 'awrc'
            cont_html += "<tr><td class='{class_style}'>{server}</td>" \
                         "<td class='{class_style}'>{user}</td>" \
                         "<td class='{class_style}'>{db}</td>" \
                         "<td class='{class_style}'>{count}</td>" \
                         "</tr>".format(server=item['connect_server'],
                                        user=item['connect_user'],
                                        db=item['connect_db'],
                                        count=item['connect_count'],
                                        class_style=class_style)
        return table_head + cont_html + "</table>"
