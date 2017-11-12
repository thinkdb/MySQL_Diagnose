此工具主要是用来 __远程__ 收集 MySQL 实例及所在机器的相关信息。

目标机器信息可以由两种方式存放：
1. 使用 json 格式
2. 使用数据库存放

__** 注意：__
  当 `innodb_stats_on_metadata` 打开时，收集参数时会触发收集统计信息的动作， 所以在收集实例信息之前会判断这个参数是否打开，打开就不收集实例信息

#### 目录结构：
```
    MySQL_Diagnose/
    ├── AWR_report                        ----- 存放已经在生成的 awr 报告
    ├── README                            ----- 使用说明
    ├── conf
    │  ├── diagnose.cnf                   ----- 配置文件，用来配置从哪获取被监控机的账号信息
    │  └── account_info.json              ----- 目标机器信息以 json 格式存放
    ├── imgs
    │  └── favicon.ico                    ----- 浏览器头部使用的小图片
    ├── lib
    │  ├── __init__.py
    │  └── funcs.py                       ----- 公共函数部分
    ├── logs
    │  └── mysql_diagnose.log             ----- 日志文件
    ├── machine
    │  └── machine_html_result.py         ----- 收集机器信息的逻辑代码, 并生成 html 文本
    ├── monitor.py                        ----- 决定要收集的内容, 可以在里面添加和删除要收集的内容
    ├── mysql
    │  ├── mysql_html_result.py           ----- 收集 MySQL 相关信息的逻辑代码, 并生成 html 文本
    │  └── sys_variables_status.py        ----- 收集的当前库的比较重要的参数信息
    ├── mysql_diagnose.py                 ----- 主文件, 直接运行即可收集信息
    ├── requestment.txt                   ----- 依赖包文件
    └── t.py
```

#### 准备工作：
- 使用 json 格式时，修改 conf/account_info.json 文件，按下面模板修改
```
{
  "192.168.200.3": {
    "host": "1.1.2.3",
    "ssh_account": "root",
    "ssh_passwd": "123456",
    "ssh_port": 22,
    "mysql_account": "root",
    "mysql_port": 3306,
    "mysql_passwd": "123456"
  },
  "192.168.200.4": {
    "host": "1.4.3.4",
    "ssh_account": "root",
    "ssh_passwd": "123456",
    "ssh_port": 22,
    "mysql_account": "root",
    "mysql_port": 3306,
    "mysql_passwd": "123456"
  }
}
```
- 使用数据库方式
  - 需要在临时库中创建一个表，用于存放要收集的机器信息，类似下面语句
  ```
    create table diagnose_account_info(
    id int auto_increment primary key,
    host varchar(60),
    mysql_account varchar(100),
    mysql_passwd varchar(100),
    mysql_port smallint,
    ssh_account varchar(100),
    ssh_passwd varchar(100),
    ssh_port smallint
     );
  ```

  - 添加要收集的主机信息
  ```
  insert into diagnose_account_info(host, mysql_account, mysql_passwd, mysql_port, ssh_account, ssh_passwd, ssh_port)
  values
  ('192.168.1.4', 'root', '123456', 3306, 'root', 'root', 22),
  ('192.168.1.5', 'root', '123456', 3306, 'root', 'root', 22)
  ```
  __注意:__ mysql 实例账号需要使用 super 权限


- 安装依赖包
` pip3 install requirements.txt`

- 修改配置文件中的内容
```
[default]
processing=2               # 并发进程数
host=192.168.200.3         # 库地址
user=hotdb_cloud           # 数据库账号
password=hotdb_cloud       # 数据库密码
port=3306                  # 数据库端口
database=test              # 库名
log_level=10               # 日志级别， 10=debug, 20=info, 30=waring, 40=error, 50=critical
type=1                     # 目标机器信息存放格式， 1为json, 非1 表示从库表中获取目标机器信息
```