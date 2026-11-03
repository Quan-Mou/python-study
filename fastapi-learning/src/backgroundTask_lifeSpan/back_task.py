

from fastapi import FastAPI, BackgroundTasks

app = FastAPI()



def send_email(email:str):
    print(f"正在向 {email} 发送邮件")
    import time
    time.sleep(2)
    print("邮箱发送完成")



@app.post("/register")
def register(email:str, background_tasks:BackgroundTasks): # BackgroundTasks 依赖注入自动完成
    background_tasks.add_task(send_email, email)

    return {
        "msg":"注册成功"
    }






