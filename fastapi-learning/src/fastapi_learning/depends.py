from typing import Annotated

from fastapi import FastAPI
from fastapi.params import Query, Depends
from pydantic import BaseModel

app = FastAPI()


def pagination(page:int = Query(default=0,ge=0),
               size:int = Query(default=10,le=200)):
    return {
        "page":page,
        "size":size
    }




class PageParams(BaseModel):
    page:int = 0
    size:int = 10

def get_page_params(page: Annotated[int,Query(ge=10)] = 1,size: Annotated[int,Query(ge=0,le=200)] = 10) -> PageParams :
    return PageParams(page=page,size=size)

#  Annotated注解：Annotated[类型,元数据]

# pageDep是一个可复用的类型别名
pageDep = Annotated[PageParams,Depends(get_page_params)]

# Depends:依赖注入
@app.get("/users")
def get_users(param:dict = Depends(pagination)):
    return param


@app.get("/orders")
def get_orders(param:dict = Depends(pagination)):
    return param


# 使用Pydantic模型组织分页
# def get_products(param:PageParams): 如果是这样，那这个参数是请求体参数
@app.get("/products")
def get_products(param:pageDep):
    return {
        "page":param.page,
        "size":param.size,
    }




if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)







