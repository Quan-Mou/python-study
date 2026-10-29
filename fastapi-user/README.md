分层与模块化

main.py 只负责组装
api 路由 只负责接收和响应请求
业务逻辑放在services
数据库操作放在repositories
core存放配置相关
models（orm实体，数据库表的映射对象）
schemas：存放模型（比如java中的dto、vo）




api/doc/test分开





