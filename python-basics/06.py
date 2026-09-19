class Person:

#   类变量，等价于Java中的static 静态变量
    school = "北京大学"

    # 构造函数，self必须指定，放在第一个参数位置，固定写法，代表this
    def __init__(self,name,age):
        self.name = name # 成员方法，必须通过构造函数定义吗？
        self.age = age

    # 定义实例方法，通过创建对象调用的普通方法,第一个参数是this
    def say_hello(self):
        print(f"Hi，I'm {self.name},我的年龄是：{self.age}")

#   类方法，第一个参数类本身
    @classmethod
    def instruction_init(cls):
        print(f"类方法:{cls}")

# 静态方法
    @staticmethod
    def static_init():
        print("静态方法")    

# 不用new对象，像调方法一样创建对象
p1 = Person("张三",18)
p1.say_hello() # 实例方法
Person.instruction_init() # 类方法
Person.static_init() # 静态方法


class XiaoMing(Person):
    def __init__(self):
        print("执行构造函数")

    def say_hi(self): # 为什么是实例方法必须传入self？
        print("1")
        # super.__init__().
        # print(self.name)    
p2 = XiaoMing()
p2.say_hi()