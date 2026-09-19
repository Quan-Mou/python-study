class Person:
    def __init__(self, age):
        self._age = age

    @property
    def age(self):              # getter
        return self._age

    @age.setter
    def age(self, value):       # setter
        if value < 0:
            raise ValueError("年龄不能为负")
        self._age = value

p = Person(25)
print(p.age)      # 25（看起来像访问属性，实际调用了 getter）
p.age = 30        # 看起来像赋值，实际调用了 setter
print(p.age)      # 30
# p.age = -5      # ❌ 抛 ValueError

# 使用@property标注的方法，在调用时直接 .名字，就会执行 .名字()这个方法对吗？
# @age.setter 这个是什么意思？就是一个setter方法？，那我直接 对象.属性 = 值，直接赋值不行吗？