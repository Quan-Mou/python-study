# vo/dto
import datetime

from pydantic import BaseModel, ConfigDict


# 创建用户dto
class UserCreate(BaseModel):
    name:str
    email:str


# 返回用户信息vo
class UserResponse(BaseModel):
    # from_attributes：允许直接从 ORM 对象（User）按字段名取值，相当于 v1 的 orm_mode
    model_config = ConfigDict(from_attributes=True)

    id:int
    name:str
    email:str
    create_at:datetime.datetime

    

