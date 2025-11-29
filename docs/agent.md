
# LangChain Agent 完全指南

## 目录
- [概述](#概述)
- [Agent 类型详解](#agent类型详解)
- [创建自定义 Agent](#创建自定义-agent)
- [完整示例](#完整示例)
- [最佳实践](#最佳实践)

## 概述

在 LangChain 1.0.0 之后，Agent 的架构发生了重大变化。`AgentExecutor` 仍然存在，但推荐使用新的创建方式和架构模式。

### 主要变化
- **新的导入路径**和创建方式
- **模块化的 Agent 创建**方法
- **LangGraph** 用于复杂工作流
- **预定义 Agent 类型**替代通用 Agent

## Agent 类型详解

### 预定义 Agent 类型

LangChain 提供了多种预定义的 Agent 类型，每种都有不同的推理策略：

```python
from langchain.agents import AgentType

# 常见的 Agent 类型：
# - ZERO_SHOT_REACT_DESCRIPTION: 零样本 ReAct 模式
# - STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION: 结构化聊天格式
# - OPENAI_FUNCTIONS: 专为 OpenAI 函数调用设计
# - JSON_CHAT: 使用 JSON 格式进行通信
# - CONVERSATIONAL_REACT_DESCRIPTION: 对话式 ReAct
不同类型的特点
Agent 类型	适用场景	特点
ZERO_SHOT_REACT_DESCRIPTION	通用任务	经典的 ReAct 模式，无需示例
STRUCTURED_CHAT_ZERO_SHOT	复杂工具调用	结构化输出，适合多参数工具
OPENAI_FUNCTIONS	OpenAI 模型	利用原生函数调用能力
JSON_CHAT	标准化通信	使用 JSON 格式
创建自定义 Agent
方式 1：使用 initialize_agent（推荐用于简单场景）
python
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

def search_tool(query: str) -> str:
    """搜索工具示例"""
    return f"搜索结果: {query}"

# 定义工具列表
tools = [
    Tool(
        name="Search",
        func=search_tool,
        description="用于搜索信息"
    )
]

# 创建 Agent
llm = ChatOpenAI(model="gpt-3.5-turbo")
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

# 使用 Agent
result = agent.run("搜索LangChain的最新版本")
方式 2：使用 create_react_agent（推荐用于中等复杂度）
python
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

# 从 LangChain Hub 获取 prompt 或自定义
prompt = hub.pull("hwchase17/react")

# 或者自定义 prompt
from langchain_core.prompts import ChatPromptTemplate

custom_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有用的助手，可以使用工具来回答问题。"),
    ("human", "{input}"),
    ("assistant", "{agent_scratchpad}")
])

# 定义工具
tools = [
    Tool(
        name="Calculator",
        func=lambda x: str(eval(x)),
        description="计算数学表达式"
    )
]

# 创建 Agent
llm = ChatOpenAI(model="gpt-3.5-turbo")
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True, 
    handle_parsing_errors=True
)

# 使用
result = agent_executor.invoke({"input": "计算 (15 + 25) * 2"})
方式 3：从头开始创建自定义 Agent（高级用法）
python
from langchain.agents import BaseSingleActionAgent, AgentExecutor
from langchain.schema import AgentAction, AgentFinish
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from typing import List, Tuple, Any, Optional, Dict

class CustomAgent(BaseSingleActionAgent):
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
    
    @property
    def input_keys(self):
        return ["input"]
    
    def plan(
        self, 
        intermediate_steps: List[Tuple[AgentAction, str]], 
        **kwargs: Any
    ) -> AgentAction | AgentFinish:
        user_input = kwargs["input"]
        
        # 自定义逻辑：根据关键词选择工具
        if any(keyword in user_input for keyword in ["计算", "算", "calculate"]):
            return AgentAction(
                tool="Calculator",
                tool_input={"expression": user_input},
                log=f"使用计算工具处理: {user_input}"
            )
        elif any(keyword in user_input for keyword in ["搜索", "查找", "search"]):
            return AgentAction(
                tool="Search",
                tool_input={"query": user_input},
                log=f"使用搜索工具查询: {user_input}"
            )
        else:
            # 直接回答
            return AgentFinish(
                return_values={"output": f"我收到了你的消息: {user_input}"},
                log="直接回复用户"
            )

# 使用自定义 Agent
tools = [
    Tool(name="Calculator", func=lambda x: str(eval(x)), description="计算器"),
    Tool(name="Search", func=lambda x: f"搜索结果: {x}", description="搜索引擎")
]

llm = ChatOpenAI(model="gpt-3.5-turbo")
custom_agent = CustomAgent(llm=llm, tools=tools)
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=custom_agent,
    tools=tools,
    verbose=True,
    max_iterations=5
)
方式 4：使用 LangGraph（用于复杂工作流）
python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

# 定义工具
tools = [
    Tool(
        name="Weather",
        func=lambda city: f"{city}的天气：晴朗，25°C",
        description="获取城市天气"
    )
]

# 创建带有状态的 Agent
llm = ChatOpenAI(model="gpt-3.5-turbo")
agent = create_react_agent(llm, tools)

# 使用 SQLite 保存状态
agent_executor = agent.compile(
    checkpointer=SqliteSaver.from_conn_string(":memory:")
)

# 使用
result = agent_executor.invoke(
    {"input": "北京的天气怎么样？"},
    config={"configurable": {"thread_id": "thread1"}}
)
完整示例
多功能 Agent 示例
python
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
import requests
import json

# 自定义工具函数
def weather_tool(city: str) -> str:
    """获取城市天气信息（模拟）"""
    weather_data = {
        "北京": "晴朗，25°C",
        "上海": "多云，23°C", 
        "广州": "阵雨，28°C",
        "深圳": "晴朗，27°C"
    }
    return weather_data.get(city, f"未找到{city}的天气信息")

def calculator_tool(expression: str) -> str:
    """计算数学表达式"""
    try:
        # 安全计算
        allowed_chars = set('0123456789+-*/.() ')
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return f"{expression} = {result}"
        else:
            return "表达式包含不安全字符"
    except Exception as e:
        return f"计算错误: {str(e)}"

def time_tool(timezone: str = "UTC") -> str:
    """获取当前时间"""
    from datetime import datetime
    import pytz
    
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        return f"{timezone}时间: {current_time}"
    except:
        return "时区信息错误"

# 工具列表
tools = [
    Tool(
        name="Weather",
        func=weather_tool,
        description="获取城市天气信息，输入城市名称"
    ),
    Tool(
        name="Calculator", 
        func=calculator_tool,
        description="计算数学表达式，例如：'2 + 3 * 4'"
    ),
    Tool(
        name="Time",
        func=time_tool,
        description="获取指定时区的当前时间，输入时区如：'Asia/Shanghai'"
    )
]

# 创建 Agent
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5
)

# 测试 Agent
test_queries = [
    "计算 (15 + 25) * 2 的结果",
    "北京的天气怎么样？",
    "现在上海的时间是多少？",
    "先计算 100 / 4，然后告诉我广州的天气"
]

for query in test_queries:
    print(f"\n=== 查询: {query} ===")
    try:
        result = agent_executor.invoke({"input": query})
        print(f"结果: {result['output']}")
    except Exception as e:
        print(f"错误: {e}")
错误处理和配置
python
# 健壮的 Agent 配置
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,  # 处理解析错误
    max_iterations=5,  # 最大迭代次数
    early_stopping_method="generate",  # 早停策略
    return_intermediate_steps=True  # 返回中间步骤
)

# 使用 try-except 包装
try:
    result = agent_executor.invoke({
        "input": "你的问题在这里"
    })
    print("成功:", result["output"])
    
    # 如果需要中间步骤
    if "intermediate_steps" in result:
        for step in result["intermediate_steps"]:
            print("步骤:", step)
            
except Exception as e:
    print(f"执行出错: {e}")
最佳实践
1. 工具设计原则
python
# 好的工具设计
good_tool = Tool(
    name="SpecificTool",
    func=specific_function,
    description="清晰描述工具功能、输入格式和输出格式"
)

# 避免的工具设计
bad_tool = Tool(
    name="VagueTool", 
    func=vague_function,
    description="做很多事情"  # 太模糊
)
2. Prompt 优化
python
# 优化的 prompt 模板
optimized_prompt = ChatPromptTemplate.from_messages([
    ("system", """
你是一个专业的助手，可以使用的工具有：
{tools}

请按照以下步骤思考：
1. 分析用户问题
2. 选择合适的工具
3. 执行工具
4. 基于结果回答

工具描述: {tool_descriptions}
    """),
    ("human", "{input}"),
    ("assistant", "{agent_scratchpad}")
])
3. 性能优化
python
# 并行工具执行
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=3,  # 限制迭代次数
    parallelize_tools=True  # 并行执行工具（如果支持）
)
4. 选择指南
场景	推荐方案	理由
简单任务	initialize_agent + 预定义类型	快速上手，配置简单
中等复杂度	create_react_agent + 自定义 prompt	平衡灵活性和易用性
高度定制	继承 BaseSingleActionAgent	完全控制 Agent 逻辑
复杂工作流	LangGraph	支持状态管理和复杂流程
生产环境	自定义 Agent + 错误处理	健壮性和可维护性
5. 常见问题解决
python
# 处理解析错误
def handle_parsing_error(error) -> str:
    return f"抱歉，我遇到了理解错误: {str(error)}。请重新表述您的问题。"

# 配置 Agent 时添加
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=lambda e: handle_parsing_error(e)
)
这个指南涵盖了 LangChain Agent 的各个方面，从基础使用到高级定制，帮助你根据具体需求选择合适的 Agent 实现方案。