from typing import List
from langchain_core.runnables import Runnable
from langchain_classic.agents import initialize_agent, AgentType
from langchain_core.tools import BaseTool

from src.llm.factory import get_llm
from src.tools.github_tools import list_repo_files_tool

def create_github_agent() -> Runnable:
    """
    组装并创建一个 GitHub Agent Executor。
    使用 langchain-classic 的 initialize_agent API 以确保兼容性。
    """
    tools: List[BaseTool] = [list_repo_files_tool]
    
    # 使用工厂获取 LLM，支持动态切换 DeepSeek/Gemini
    llm = get_llm()

    # initialize_agent 是一个稳定但较旧的 API，位于 langchain-classic 中
    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
    )

    return agent_executor
