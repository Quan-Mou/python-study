
"""
    lambda表达式： 参数可以有多个，表达式只能有一个，定义完用变量接收
    lambda 参数1,参数2,参数3， ...: 表达式
"""

add_one = lambda x : x + 1
add = lambda a,b : a+b


print(add_one(10)) # 11

names = ["Alice", "Bob", "Charlie"]
# 按字符串长度排序，key表示按照什么排序，len()返回的是每个列表元素中的长度
sorted_names = sorted(names, key=lambda x: len(x))
print(sorted_names)   # ['Bob', 'Alice', 'Charlie']

print("-------------------------------")

nums = [1, 2, 3, 4, 5]
# 每个元素平方
squared = list(map(lambda x: x ** 2, nums))
print(squared)   # [1, 4, 9, 16, 25]

