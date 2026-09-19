import mysql.connector
import json
from datetime import datetime, date, time
from decimal import Decimal
"""
    mysql-connector

"""


def json_default(obj):
    if isinstance(obj, (datetime, date, time)):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, bytes):
        return obj.decode("utf-8")
    raise TypeError(f"无法序列化 {type(obj)}")


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="zqh123123123",
    database="blog" # 指定数据库
)

my_cursor = mydb.cursor(dictionary=True)

# 查看所有数据库,返回的结果还在游标里
my_cursor.execute("SHOW DATABASES")
for db in my_cursor.fetchall():
    print(db)


print("-------------------")

#  查询数据
my_cursor.execute("SELECT * FROM tags")

rows = my_cursor.fetchall()

json_str = json.dumps(rows, ensure_ascii=False, default=json_default)
print(json_str)

for item in rows:
    print(item)


print("----------------------")

insertDataSql = "insert into tags(name) values('记录')"

my_cursor.execute(insertDataSql)

mydb.commit() # 提交事务




# 用完关闭（好习惯）
my_cursor.close()
mydb.close()