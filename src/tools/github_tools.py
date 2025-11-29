import asyncio
from typing import List, Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from src.services.github_service import GitHubService
from loguru import logger

# 实例化 GitHub 服务，可以在模块级别共享
github_service = GitHubService()

class ListRepoFilesInput(BaseModel):
    """Input for the list_repository_files tool."""
    repo_owner: str = Field(description="The owner of the GitHub repository.")
    repo_name: str = Field(description="The name of the GitHub repository.")
    branch: str = Field(description="The branch to list files from.", default="main")

class ListRepoFilesTool(BaseTool):
    name: str = "list_repository_files"
    description: str = "Useful for listing all file paths in a specific branch of a GitHub repository."
    args_schema: Type[BaseModel] = ListRepoFilesInput

    def _run(self, repo_owner: str, repo_name: str, branch: str = "main") -> List[str]:
        # LangChain 的 BaseTool.run 是同步的，但我们的 service 方法是异步的
        # 在这里，我们使用 asyncio.run() 来桥接同步和异步
        # 注意：这在已经有运行的事件循环（如 FastAPI）中可能会有问题
        # 但对于 LangChain Agent 的同步执行流程是可行的
        logger.info("Running ListRepoFilesTool synchronously...")
        return asyncio.run(self._arun(repo_owner, repo_name, branch))

    async def _arun(self, repo_owner: str, repo_name: str, branch: str = "main") -> List[str]:
        # 异步执行，这是 Agent 在异步模式下会调用的方法
        logger.info("Running ListRepoFilesTool asynchronously...")
        return await github_service.get_all_files_list(repo_owner, repo_name, branch)

# 实例化工具，以便在别处导入和使用
list_repo_files_tool = ListRepoFilesTool()

class GetPrReviewContextInput(BaseModel):
    """Input for the get_pr_code_review_context tool."""
    repo_owner: str = Field(description="The owner of the GitHub repository.")
    repo_name: str = Field(description="The name of the GitHub repository.")
    pull_number: int = Field(description="The pull request number.")

class GetPrReviewContextTool(BaseTool):
    name: str = "get_pr_code_review_context"
    description: str = "Useful for getting full context (diff, original and updated code) of a pull request for code review."
    args_schema: Type[BaseModel] = GetPrReviewContextInput

    def _run(self, repo_owner: str, repo_name: str, pull_number: int) -> dict:
        logger.info("Running GetPrReviewContextTool synchronously...")
        return asyncio.run(self._arun(repo_owner, repo_name, pull_number))

    async def _arun(self, repo_owner: str, repo_name: str, pull_number: int) -> dict:
        logger.info("Running GetPrReviewContextTool asynchronously...")
        return await github_service.get_pr_code_review_info(repo_owner, repo_name, pull_number)

get_pr_review_context_tool = GetPrReviewContextTool()
