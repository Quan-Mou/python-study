from mcp.server import FastMCP


# 创建MCP服务实例，company-server是服务名称
mcp = FastMCP("company-server")




# 使用装饰器定义mcp工具
@mcp.tool() # @mcp.tool 会将普通python函数注册为MCP tool
def query_company(company_name:str) ->dict:
    """
    根据企业名称查询企业信息
    :param company_name: 企业名称
    :return: 企业基本信息
    """

    # 模拟从数据库中获取数据
    company_data = {
        "company_name":company_name,
        "industry":"人工智能",
        "registered_capital": "1000万元",
        "location":"杭州",
        "employee_count":100
    }
    return company_data


@mcp.tool()
def calculate_registered_capital(
    capital: float,
    unit: str = "万元"
) -> str:
    """
    格式化企业注册资本。

    Args:
        capital: 注册资本数值
        unit: 注册资本单位
    """
    return f"{capital}{unit}"



if __name__ == '__main__':
    # 启动MCP 服务
    mcp.run(transport="stdio") # 传输模式有stdio、streamable
#   MCP Client 启动MCP Server子进程，双方通过标准输入和标准输出进行通信












