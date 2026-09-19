# 类型注解，给变量标注一个具体的类型，不依赖py的动态判断

name: str = "张三"
age: int = 18
course: list[str] = ["计算机网络","操作系统","计算机组成原理"] # 声明一个list类型，内容是str的列表
print(name)
print(age)
