import time
import _thread
import threading

def print_time(threadName,delay):
    """
    打印时间的函数
    """
    count = 0
    while count<5:
        time.sleep(delay)
        count+=1
        print(f"threadName{threadName}:{time.ctime(time.time())}")

# # 使用_thread创建线程
# try:
#     # 第二个参数元组是传给 print_time的参数，等价于 print_time("Thread-1",2)，按顺序传入
#     _thread.start_new_thread(print_time,("Thread-1", 2, ))
#     _thread.start_new_thread(print_time,("Thread-2", 4, ))
# except:
#     pass

def print_nums():
    for i in range(5):
        time.sleep(1)
        print(i)


class MyThread(threading.Thread):
    def __init__(self,threadId,name,delay):
        threading.Thread.__init__(self)
        self.name = name
        self.threadId = threadId
        self.delay = delay

    def run(self):
        print ("开始线程：" + self.name)
        print_time(self.name, self.delay)
        print ("退出线程：" + self.name)

    
thread1 = threading.Thread(target=print_nums)
thread2 = MyThread(10,"自定义的线程",1)

thread1.start()
thread2.start()

# 等待线程执行完毕
thread1.join()
thread2.join()
print("线程执行完毕，主线程退出程序")

