# 列表 （有序，值可变）
print("-------------列表--------------")
lst = [10,20,100,10]
for item in lst:
    print(item)
lst[0] = 100    
print(lst[0])

# 元组 (有序，值不可变)
print("-------------元组--------------")
data1 = (1,2,3,4,5)
for item in data1:
    print(item)
# data1[0] = 100 报错！！，值不可变

print("-------------字典--------------")
# 字典 key必须是不可变类型
# userInfo = {name:"权某",age:18,address:"江西"} 错误的写法，name这些key会被解析为变量
userInfo = {"name":"权某","age":18,"address":"江西"} 
print(userInfo.get("name"))
userInfo["heigth"] = 1.88 # 添加一个k，v
print(userInfo.get("heigth",0)) # 获取 heigth 这个key，如果不存在则返回 0 

print("-------------set--------------")
# set 无序，不可重复
setData = {10,20,30,40,50,100,20}
for item in setData:
    print(item)
setData.add(17000)
setData.remove(20)

print("-------------值传递--------------")
# 变量和java一样是值传递？ Python和Java一样都是一样的机制
a = [10,11,22,398,29]
b = a
b[0] = 100
print(a[0])

print("-------------判断类型--------------")
aType = type(a) # 获取变量的类型 <class 'list'>
print(aType)
aStr = type("abc")
print(aStr)
isIntType = isinstance(aStr,int) # False
print(isIntType)


