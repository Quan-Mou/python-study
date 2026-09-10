print(f"【utils.py】我的 __name__ 是：{__name__}")

def add(a, b):
    return a + b

# 这里的代码只有当 utils.py 被直接运行时才执行
if __name__ == "__main__":
    print(">>> utils.py 自己被运行了，执行测试代码...")
    print(f"测试结果：1+2 = {add(1, 2)}")