
import os
import time
import datetime
import sys
import math
import re
import json
import urllib
import random

"""
    标准库
"""

# 获取当前的工作目录
current_dir = os.getcwd()
print(current_dir)

# 列出当前目录的所有文件
files = os.listdir()
print(files)

# 返回一个随机数
r = random.choice(["a","c","b"])
print(r)


# 获取当前时间日期
current_datetime = datetime.datetime.now()
print(current_datetime)

today = datetime.date.today()
print(today)


current_hour = datetime.time.hour()
print(current_hour)

datetime.datetime.now().

