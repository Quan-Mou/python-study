

def main():

    # 推荐：with 自动关闭文件
    strs = ""
    with open('test.txt', 'r', encoding='utf-8') as f:
        for line in f:
            strs += line.rstrip()

    print(strs)

main()
