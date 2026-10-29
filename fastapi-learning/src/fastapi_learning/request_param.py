from fastapi import FastAPI, UploadFile
from fastapi.params import Query, Form
from pydantic import BaseModel, Field

from fastapi_learning.restful_request import UPLOAD_DIR

app = FastAPI(title="FastAPI-learning",summary="学习学习啦~",description="这是一个很严肃的-FastAPI学习")


"""
FastAPI 常见的返回类型包括 JSON 对象（dict）、JSON 数组（list）、Pydantic 模型、纯文本（PlainTextResponse）、HTML 页面（HTMLResponse）、文件（FileResponse）、流式响应（StreamingResponse）和空响应（204 No Content）。
"""

@app.get("/")
def read_root():
    return {
        "name":"quanmou",
        "age":18
    }


# 路径参数
@app.get("/users/{user_id}")
def get_user(user_id:int):
    print(f"路径参数：{user_id}")
    return {
        "status":200,
        "msg":"ok",
        "data":user_id
    }

# 查询参数
@app.get("/users")
def get_users(page:int=1,size:int= Query(default=1,ge=0,le=200)): # 对类型做校验
    limit = {
        "page":page,
        "size":size
    }
    return {
        "status":200,
        "msg":"ok",
        "data": limit
    }



class User(BaseModel):
    name: str = Field(min_length=1,max_length=20)
    age: int
    email:str



users:list[User] = []




# 解析请求体参数
@app.post("/users")
def create_user(user: User):
    users.append(user)
    return {
        "status":200,
        "msg":"ok",
        "data":users
    }


@app.get("/allUser")
def get_all_users():
    return users


@app.delete("/deleteUser/{userId}")
def delete_user(userId:int):
    users.remove(userId)
    return {
        "status":200,
        "msg":f"删除用户{userId}成功" ,
        "data":users
    }


# ==================== 表单与文件上传 ====================

@app.post("/submitForm")
def submit_form(username: str = Form(), age: int = Form()):
    """纯表单：参数和以前一样声明，只是换成 Form() 走请求体而不是 URL"""
    print(f"表单提交：{username}，{age} 岁")
    return {
        "status": 200,
        "msg": "ok",
        "data": {"username": username, "age": age},
    }


@app.post("/uploadFile")
def upload_file(file: UploadFile):
    """纯文件上传：单个文件"""
    # file.filename 原始文件名；file.content_type 文件类型如 image/png
    save_path = UPLOAD_DIR / file.filename
    save_path.write_bytes(file.file.read())   # 读取文件内容并落盘
    print(f"收到文件：{file.filename}（{file.content_type}），已保存到 {save_path}")
    return {
        "status": 200,
        "msg": "ok",
        "data": {
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": save_path.stat().st_size,
        },
    }


@app.post("/uploadWithForm")
def upload_with_form(
    title: str = Form(),            # 表单字段：普通文本
    file: UploadFile = ...,         # 文件字段
):
    """表单 + 文件混合提交——真实项目里最常见的形式（如带封面的文章）"""
    save_path = UPLOAD_DIR / file.filename
    save_path.write_bytes(file.file.read())
    print(f"文章《{title}》发布，附件 {file.filename} 已保存")
    return {
        "status": 200,
        "msg": "ok",
        "data": {"title": title, "attachment": file.filename},
    }





if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)



