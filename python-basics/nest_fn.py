
# 嵌套函数
def make_addr(x):
    def add(n):
        return x + n
    # 返回的函数本身，注意不是函数调用的返回值
    return add



# 返回的是add函数
add10 = make_addr(10)

# 这里调用的是add函数 add(5)
print(add10(5))

# 嵌套函数的关键是闭包，闭包（函数内部保存了函数外部的状态）




