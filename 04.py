list1 = [1,10,20]

# 把列表包装为一个迭代器
it = iter(list1)


# 调用一次next，即获取一个元素
print(next(it))
print(next(it))
print(next(it))
# 超出索引在调用会报错
# print(next(it))

flag = 0
while True:
    if flag == 10:
        print("exit")
        break
    flag +=1
    # pass
    

# /Users/quanmou/Desktop/标书.docx
filePath = "test.txt"
# fileInfo =  open(filePath)
with open(filePath) as fileInfo:
    content = fileInfo.read()
# print(content)
    print(fileInfo.readline())
    print(fileInfo.readlines())

try:
    print("tewst")
except BaseException:
    print("BaseException类型异常")
else:
    print("没有发生异常的垫后操作")


raise Exception("这是一个常规异常父类")









