"""
    业务需求
    处理一笔报销申请，自动完成三步：

    接收申请：拿到申请人、金额、部门。

    预审子流程：

    分析这笔申请（生成一段分析文字）；

    检查该部门剩余预算，判断金额是否超预算；

    给出审核建议（“预算充足，建议进入人工审批”或“预算不足，建议暂缓审批”）。

    输出结果：打印分析、剩余预算、审核建议。

    例子：张三、技术部、1200 元 → 技术部预算 10000，预算充足 → 建议进入人工审批。

"""
from typing import TypedDict

from langgraph.constants import START,END
from langgraph.graph import StateGraph

# 难点：
# 1. 子图状态和主图状态如何设计
# 2. 子图和父图的节点如何设计
# 3. 选择何种子图的集成方式


# 主图任务：
# 子图任务：


"""
    状态：
    1.声请人
    2.金额
    3.部门
    4.预算
    5.分析结果
    6.审批结果
"""

# 分析报销申请，
# 查预算
# 根据预算分析报销情况
# 给出最终的结果

# 子图状态
class SubState(TypedDict):
    applicant:str
    amount:float
    department:str
    budget:float
    analyse:str
    review:str


# 分析报销申请子图节点

def analyse_node(state:SubState):
    print(f"[子图节点 analyse_node] 分析：{state['applicant']} 申请的报销，报销金额：{state['amount']}")
    analyse_res = f"{state['applicant']} 申请的报销，报销金额：{state['amount']}"

    return {
        "analyse":analyse_res,
    }

def check_budget_node(state:SubState):
    print("[子图节点 check_budget_node] 检查部门预算")
    # 模拟的数据
    budget_department = {
        "技术部":12000.0,
        "市场部":8700.0,
        "人事部":200.0
    }

    budget = budget_department.get(state["department"],0.0)

    if state["budget"] <= budget:
        review = "预算充足，建议进入人工审批。"
    else:
        review = "预算不足，建议暂缓审批。"

    return {
        "budget": budget,
        "review": review,
    }


#     构建子图并编译
preCheck_graph= StateGraph(state_schema=SubState)

preCheck_graph.add_node("analyse_node",analyse_node)
preCheck_graph.add_node("check_budget_node",check_budget_node)

preCheck_graph.add_edge(START,"analyse_node")
preCheck_graph.add_edge("analyse_node","check_budget_node")
preCheck_graph.add_edge("check_budget_node",END)

sub_graph = preCheck_graph.compile()


class ParentState(TypedDict):
    applicant: str
    amount: float
    department: str
    budget: float
    analyse: str
    review: str




def receive_node(state:ParentState):
    print(f"[父图节点 receive_node] 进入报销主节点:receive_node")
    return{}

def output_node(state:ParentState):
    print("xxxxxxxxxxxxxxxxxxxxxxxx")
    print(f"申请人：{state['applicant']}")
    print(f"报销金额：{state['amount']}")
    print(f"申请部门{state['department']}")
    print(f"预算：{state['budget']}")

    return {}

graph = StateGraph(state_schema=ParentState)
graph.add_node("sub_graph",sub_graph)
graph.add_node("receive_node",receive_node)
graph.add_node("output_node",output_node)

graph.add_edge(START,"receive_node")
graph.add_edge("receive_node","sub_graph")
graph.add_edge("sub_graph","output_node")
graph.add_edge("output_node",END)

parent_graph = graph.compile()


#  执行主图
if __name__ == "__main__":

    init_status = {
        "applicant": "张三",
        "amount": 1200.0,
        "department": "技术部",
        "analysis": "",
        "budget": 0.0,
        "review": "",
    }

    result = parent_graph.invoke(init_status)
    print("最终结果：")
    print(result)












