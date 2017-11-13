#!/bin/env python
# -*- coding:utf8 -*-

import time


def get_host_info(os_connected_stream):
    cpu_stat_dict = {}
    cpu_stat_1 = os_connected_stream.get_cpu_stat()
    time.sleep(1)
    cpu_stat_2 = os_connected_stream.get_cpu_stat()
    steal1 = guest1 = guest_nice1 = steal2 = guest2 = guest_nice2 = 0

    class_style = 'awrnc'
    for item in cpu_stat_2:
        item_info = cpu_stat_2[item]
        user2 = int(item_info['user'])
        nice2 = int(item_info['nice'])
        idle2 = int(item_info['idle'])
        iowait2 = int(item_info['iowait'])
        irq2 = int(item_info['irq'])
        softirq2 = int(item_info['softirq'])
        system2 = int(item_info['system'])

        # sleep
        user1 = int(cpu_stat_1[item]['user'])
        nice1 = int(cpu_stat_1[item]['nice'])
        idle1 = int(cpu_stat_1[item]['idle'])
        iowait1 = int(cpu_stat_1[item]['iowait'])
        irq1 = int(cpu_stat_1[item]['irq'])
        softirq1 = int(cpu_stat_1[item]['softirq'])
        system1 = int(cpu_stat_1[item]['system'])

        if int(os_connected_stream.a) == 2 and int(os_connected_stream.c) >= 11:
            steal2 = int(item_info['steal'])
            steal1 = int(cpu_stat_1[item]['steal'])
        if int(os_connected_stream.a) == 2 and int(os_connected_stream.c) >= 24:
            guest2 = int(item_info['guest'])
            guest1 = int(cpu_stat_1[item]['guest'])
        if int(os_connected_stream.a) == 3 and int(os_connected_stream.b) >= 2:
            guest_nice2 = int(item_info['guest_nice'])
            guest_nice1 = int(cpu_stat_1[item]['guest_nice'])

        total_1 = user1 + nice1 + idle1 + iowait1 + irq1 + softirq1 + system1 + steal1 + guest1 + guest_nice1
        total_2 = user2 + nice2 + idle2 + iowait2 + irq2 + softirq2 + system2 + steal2 + guest2 + guest_nice2
        total = total_2 - total_1
        idle = (idle2 - idle1)/total * 100
        system = (system2 - system1)/total * 100
        user = (user2 - user1)/total * 100
        nice = (nice1 - nice2)/total * 100
        iowait = (iowait2 - iowait1)/total * 100

        hi = (irq2-irq1)/total * 100
        si = (softirq2-softirq1)/total * 100
        st = (steal2-steal1)/total * 100

        cpu_stat_dict[item] = {}
        cpu_stat_dict[item]['idle'] = idle
        cpu_stat_dict[item]['system'] = system
        cpu_stat_dict[item]['user'] = user
        cpu_stat_dict[item]['nice'] = nice
        cpu_stat_dict[item]['iowait'] = iowait
        cpu_stat_dict[item]['hi'] = hi
        cpu_stat_dict[item]['si'] = si
        cpu_stat_dict[item]['st'] = st

    os_version = os_connected_stream.get_os_version()
    cpu = os_connected_stream.get_cpu_info()
    memory = os_connected_stream.get_mem_info()

    base_info = "<p><table border='1' width='500'><tr>" \
                "<th class='awrbg' scope='col'>HostName</th>" \
                "<th class='awrbg' scope='col'>Platform</th>" \
                "<th class='awrbg' scope='col'>Kernel Release</th>" \
                "<th class='awrbg' scope='col'>Cores</th>" \
                "<th class='awrbg' scope='col'>Memory (MB)</th>" \
                "</tr>" \
                "<tr>" \
                "<td scope='row' class='awrnc'>{hostname}</td>" \
                "<td class='awrnc'>{os_version}</td>" \
                "<td class='awrnc'>{kernel}</td>" \
                "<td align='right' class='awrnc'>{cores}</td>" \
                "<td align='right' class='awrnc'>{memtotal}</td>" \
                "</tr></table></p>".format(hostname=os_version['hostname'],
                                           os_version=os_version['os_version'],
                                           cores=cpu['core'],
                                           kernel=os_version['kernel_release'],
                                           memtotal=memory['MemTotal'])

    cpu_info = "<p>CPU</p><p><table border='1' width='500'><tr>" \
               "<th class='awrbg' scope='col'>Uptime</th>" \
               "<th class='awrbg' scope='col'>Load 1</th>" \
               "<th class='awrbg' scope='col'>Load 5</th>" \
               "<th class='awrbg' scope='col'>load 15</th>" \
               "</tr>" \
               "<tr>" \
               "<td scope='row' class='awrnc'>{uptime}</td>" \
               "<td class='awrnc'>{load_1}</td>" \
               "<td align='right' class='awrnc'>{load_5}</td>" \
               "<td align='right' class='awrnc'>{load_15}</td>" \
               "</tr></table></p>".format(uptime=cpu['uptime'],
                                          load_1=cpu['load_1'],
                                          load_5=cpu['load_5'],
                                          load_15=cpu['load_15'])
    mem_use_per = int(memory['mem_use_per'])
    if mem_use_per >= 80 and mem_use_per < 90:
        class_style = 'awrwaring'
    elif mem_use_per >= 90:
        class_style = 'awrcritical'

    mem_info = "<p>Memory</p><p><table border='1' width='800'><tr>" \
               "<th class='awrbg' scope='col'>MemToal (MB)</th>" \
               "<th class='awrbg' scope='col'>MemFree (MB)</th>" \
               "<th class='awrbg' scope='col'>MemUsePer (%)</th>" \
               "<th class='awrbg' scope='col'>Buffers (MB)</th>" \
               "<th class='awrbg' scope='col'>Cached (MB)</th>" \
               "<th class='awrbg' scope='col'>SwapTotal (MB)</th>" \
               "<th class='awrbg' scope='col'>SwapFree (MB)</th>" \
               "<th class='awrbg' scope='col'>SwapCached (MB)</th>" \
               "</tr>" \
               "<tr>" \
               "<td align='right' class='awrnc'>{MemTotal}</td>" \
               "<td align='right' class='awrnc'>{MemFree}</td>" \
               "<td align='right' class='{class_style}'>{MemUsePer}</td>" \
               "<td align='right' class='awrnc'>{Buffers}</td>" \
               "<td align='right' class='awrnc'>{Cached}</td>" \
               "<td align='right' class='awrnc'>{SwapTotal}</td>" \
               "<td align='right' class='awrnc'>{SwapFree}</td>" \
               "<td align='right' class='awrnc'>{SwapCached}</td>" \
               "</tr></table></p>".format(MemTotal=memory['MemTotal'],
                                          MemFree=memory['MemFree'],
                                          MemUsePer=memory['mem_use_per'],
                                          Buffers=memory['Buffers'],
                                          Cached=memory['Cached'],
                                          SwapTotal=memory['SwapTotal'],
                                          SwapFree=memory['SwapFree'],
                                          SwapCached=memory['SwapCached'],
                                          class_style=class_style)

    cpu_stat = "<p><table border='1' width='500'><tr>" \
               "<th class='awrbg' scope='col'>CPUs</th>" \
               "<th class='awrbg' scope='col'>Sys</th>" \
               "<th class='awrbg' scope='col'>User</th>" \
               "<th class='awrbg' scope='col'>Nice</th>" \
               "<th class='awrbg' scope='col'>Iowait</th>" \
               "<th class='awrbg' scope='col'>Idle</th>" \
               "<th class='awrbg' scope='col'>Hi</th>" \
               "<th class='awrbg' scope='col'>Si</th>" \
               "<th class='awrbg' scope='col'>St</th>" \
               "</tr>"

    for id, item in enumerate(cpu_stat_dict):
        if id % 2 == 1:
            class_style = 'awrc'
        else:
            class_style = 'awrnc'
        cpu = 'cpu'+str(id)
        tem_str = "<tr>" \
                  "<td scope='row' class='{class_style}'>{cpu}</td>" \
                  "<td scope='row' class='{class_style}'>{sys}</td>" \
                  "<td scope='row' class='{class_style}'>{user}</td>" \
                  "<td scope='row' class='{class_style}'>{nice}</td>" \
                  "<td scope='row' class='{class_style}'>{iowait}</td>" \
                  "<td scope='row' class='{class_style}'>{idle}</td>" \
                  "<td scope='row' class='{class_style}'>{hi}</td>" \
                  "<td scope='row' class='{class_style}'>{si}</td>" \
                  "<td scope='row' class='{class_style}'>{st}</td>" \
                  "</tr>".format(cpu=cpu,
                                 sys='{:.2f}%'.format(cpu_stat_dict[cpu]['system']),
                                 user='{:.2f}%'.format(cpu_stat_dict[cpu]['user']),
                                 nice='{:.2f}%'.format(cpu_stat_dict[cpu]['nice']),
                                 iowait='{:.2f}%'.format(cpu_stat_dict[cpu]['iowait']),
                                 idle='{:.2f}%'.format(cpu_stat_dict[cpu]['idle']),
                                 hi='{:.2f}%'.format(cpu_stat_dict[cpu]['hi']),
                                 si='{:.2f}%'.format(cpu_stat_dict[cpu]['si']),
                                 st='{:.2f}%'.format(cpu_stat_dict[cpu]['st']),
                                 class_style=class_style
                                 )
        cpu_stat += tem_str
    info = base_info + cpu_info + cpu_stat + "</table></p>" + mem_info
    return info


def get_disk_info(os_connected_stream):
    disk = os_connected_stream.get_disk_info()
    table_head = "<p>DISK</p><p><table border='1' width='800'><tr>" \
                 "<th class='awrbg' scope='col'>FileSystem</th>" \
                 "<th class='awrbg' scope='col'>Mounted On</th>" \
                 "<th class='awrbg' scope='col'>FileSystemType</th>" \
                 "<th class='awrbg' scope='col'>Total (MB)</th>" \
                 "<th class='awrbg' scope='col'>Used (MB)</th>" \
                 "<th class='awrbg' scope='col'>Avail (MB)</th>" \
                 "<th class='awrbg' scope='col'>Use Per (%)</th>" \
                 "</tr>"
    disk_str = ""
    for id, item in enumerate(disk):
        if id % 2 == 1:
            class_style = 'awrc'
        else:
            class_style = 'awrnc'

        if int(disk[item]['use_per']) >= 80 and int(disk[item]['use_per']) < 90:
            class_style = 'awrwaring'
        elif int(disk[item]['use_per']) >= 90:
            class_style = 'awrcritical'

        file_system = item.split('/')[-1]

        disk_info = "<tr>" \
                    "<td class='{class_style}'>{FileSystem}</td>" \
                    "<td class='{class_style}'>{mounted}</td>" \
                    "<td class='{class_style}'>{FileSystemType}</td>" \
                    "<td align='right' class='{class_style}'>{Total}</td>" \
                    "<td align='right' class='{class_style}'>{Used}</td>" \
                    "<td align='right' class='{class_style}'>{Avail}</td>" \
                    "<td align='right' class='{class_style}'>{Use}</td>" \
                    "</tr>".format(FileSystem=file_system,
                                   mounted=disk[item]['mount_on'],
                                   FileSystemType=disk[item]['file_system_type'],
                                   Total=disk[item]['total_mb'],
                                   Used=disk[item]['used_mb'],
                                   Avail=disk[item]['avail_mb'],
                                   Use=disk[item]['use_per'],
                                   class_style=class_style
                                   )
        disk_str += disk_info
    return table_head+disk_str+"</table></p>"


def get_disk_io(os_connected_stream):
    io = os_connected_stream.get_iops(10)
    flag = 1
    table_head = "<p>IO and Flow Info</p><table border='1' width='1200'><tr>" \
                 "<th class='awrbg'>Time</th>"
    th_head = "<th class='awrbg'></th><th class='awrbg'>Input</th><th class='awrbg'>Onput</th>"
    td_body = "<td class='{style}'>{item}</td><td class='{style}'>{v1}</td><td class='{style}'>{v2}</td>"
    td_str = "<tr>"
    time_str = "<td class='{style}'>{time}</td>"
    for drivce in io:
        class_style = drivce['class_style']
        td_str += time_str.format(style=class_style, time=drivce['time'])
        if flag:
            th_head *= len(drivce) - 2
            flag = 0
            th_head += "</tr>"
        for item in drivce:
            # td
            # network
            if item.startswith('net'):
                td_str += td_body.format(item=item, v1=drivce[item]['Receive'],
                                         v2=drivce[item]['Transmit'], style=class_style)
            elif item == 'class_style' or item == 'time':
                pass
            # disk
            else:
                td_str += td_body.format(item=item, v1=drivce[item]['write_io'],
                                         v2=drivce[item]['read_io'], style=class_style)

        td_str += '</tr>'
    table_body = table_head + th_head + td_str + "</table>"
    return table_body
