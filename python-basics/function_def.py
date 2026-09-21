def sum(a,b):
    return a+b


result = sum(10,20)
print(result)


# print(__name__)
# print(__main__)


#  定义函数的的默认参数：

def print_person_info(name,addr,age=18):
    """ 默认参数必须放在非默认参数后面

    """
    print(name,age,addr)
    # print(age)
    # print(addr)


# 调用时根据参数多种调用方式
print_person_info("权","北京")
print_person_info("权","北京",188)


# 关键字参数：
def greet(name, age):
    print(f"{name} 今年 {age} 岁")

# 位置参数：按顺序传
greet("张三", 25)

# 关键字参数：明确写出参数名
greet(name="张三", age=25)

# 关键字参数可以颠倒顺序（位置参数不行！）
greet(age=25, name="张三")

# **kwagrs 收集所有未匹配的关键字参数，打包成字典 dict
def show_info(**kwargs):
    """
        kwargs 是一个字典
    """
    for k,v in kwargs.items():
        print(f"k = {k}, v = {v}")

show_info(name="张三",age=18,addr="上海")


# 在参数列表中加一个 * , 强制后面的参数必须使用 关键字参数传递
def create_user(name,*,age,addr):
    print(f"{name},{age},{addr}")
# 
# create_user("张三",19,"shengz")  报错，必须使用关键字传递
create_user("张三",age = 19,addr = "shengz")       

# *args 这种参数相当于java中可变参数，把多个参数打包成元组，接收的是所有未匹配的位置参数
def sum2(*args):
    print(f"收到{len(args)} 个参数，值为：{args}")

sum2(10,20,30,40)

# 更直观
nums = (1,2,3)
print(*nums)
print(nums)

# 完整的一个函数参数顺序规则：
def func(位置参数, *args, 关键字参数, **kwargs):
    pass

# 示例：
def fun(a,b,*args,name="张三",**kwargs):
    print(f"a={a}, b={b}")
    print(f"args={args}")
    print(f"name={name}")
    print(f"kwargs={kwargs}")

fun(1,2,3,4,5,age=18,addr="深圳")
fun(1,2,3,4,5,name="李四",age=18,addr="深圳")
