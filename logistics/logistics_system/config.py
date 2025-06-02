# db_config.py

import pymysql

def connection():
    return pymysql.connect(
        host='localhost',       # 主机地址
        user='root',            # 用户名
        password='Jianghuweizhi100',     # 数据库密码
        database='logistics', 
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor # 返回字典形式
    )