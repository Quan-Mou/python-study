


def add(a,b):
    return a + b


# test开头的函数会被pytest自动发现
def test_add():
    # assert判断结果是否符合预期
    assert add(1,2) == 3






