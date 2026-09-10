print(f"【main.py】我的 __name__ 是：{__name__}")

import utils  # 导入 utils

print(">>> main.py 正在运行")
result = utils.add(10, 20)
print(f"调用 utils.add 结果：{result}")