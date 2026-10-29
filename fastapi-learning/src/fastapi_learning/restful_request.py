from pathlib import Path

from fastapi import FastAPI, Form, UploadFile


app = FastAPI(title="FastAPI-learning",summary="学习学习啦~",description="这是一个很严肃的-FastAPI学习")

# 上传文件的保存目录（相对启动命令所在目录）
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def read_root():
    return {
        "name":"quanmou",
        "age":18
    }


@app.post("/savePersonInfo")
def insert_person_nfo(name:str):
    print(f"新增用户：{name}的信息！")
    return {
        "status": 200,
        "msg":"ok"
    }

@app.put("/updatePersonInfo")
def update_person_info(name:str,target:str):
    person_info = {
        "name":name,
        "age":109
    }

    # person_info.update()

    print(f"修改用户：{name}的信息成功")
    return {
        "status": 200,
        "msg": "ok"
    }

@app.delete("/deletePersonInfo")
def delete_person_info(name:str):
    print(f"删除用户为：{name}的信息失败！")
    return {
        "status": 401,
        "msg": "删除失败，你的权限不够！"
    }


# delete_person_info = app.delete("deletePersonInfo")delete_person_info(name:str)

