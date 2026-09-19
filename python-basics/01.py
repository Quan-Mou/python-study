print("Hello World!")
print("你好，世界！")

"""
这都是多行注释
"""

'''
这也是多行注释
'''

# 这是单行注释

if True:
    print("this is true")
else:
    print("this is false")


text = """
    故事
    这是一个悲伤的故事
"""
print(text)

name = "权"
age = 18
address = "江西"

print(name)
print(age)
print(address)


# a  = b = c = 1
a = 1
b = a
a = 2
print(a)
print(b)
# print(c)

list1 = "abcde"

print(list1[0:-1]) # 左闭右开，从第一个索引取到最后一个

print(list1[0:4:2]) # 第三个参数设置步长，用于跳过几个元素

print("------------------------------------------")
lst = [1,2,4,5,6,7] # 这是list，内容可以修改
print(lst[3])
lst[3] = 100

# for 循环，遍历
for item in lst:
    print(item)


t = ("a",1,"hahaha",200)
print(t[2])
# t[2] = 300 ，元组是不可修改的，会报错

userInfo = {name:"权某",age:18,address:"江西"}

temp = userInfo.get("name")

print(temp)








 








