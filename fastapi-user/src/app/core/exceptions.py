# 统一的返回格式：
# {
#     "code":200,
#     "msg":"xxx",
#     "data":{}
# }

from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse


# 异常处理
def registry_exception_handlers(app:FastAPI):
    @app.exception_handler(404)
    def not_found_handler(
            request:Request,
            exc
    ):
        return JSONResponse(
            status_code=404,
            content={
                "code": 404,
                "message": "资源不存在",
                "data": None
            }
        )



