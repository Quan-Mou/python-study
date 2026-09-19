class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # 1. __str__：print(obj) 时调用（等价 Java 的 toString()）
    def __str__(self):
        return f"Vector({self.x}, {self.y})"

    # 2. __repr__：调试时显示（类似 str，但更精确）
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

    # 3. __add__：支持 v1 + v2
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    # 4. __eq__：支持 v1 == v2（等价 Java 的 equals()）
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # 5. __len__：支持 len(obj)
    def __len__(self):
        return 2   # 假设向量长度固定为2

v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1)          # Vector(1, 2)      ← __str__
print(v1 + v2)     # Vector(4, 6)      ← __add__
print(v1 == Vector(1, 2))  # True       ← __eq__
print(len(v1))     # 2                 ← __len__


# 1.__xxx__是特殊的方法，当在对象上使用特定语法，由python自动触发，python解释器自动执行，比如 对象(a+b)就会去执行 对象.__add__方法
# 2.每个方法的第一个参数都必须传入self【this】，名字随便叫，静态方法没有self
# 3. _xxx是私有方法（约定）

