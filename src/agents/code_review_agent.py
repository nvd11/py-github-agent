from typing import List
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate

from src.llm.factory import get_llm
from src.tools.github_tools import get_pr_review_context_tool

# System prompt for the agent
SYSTEM_PROMPT = """You are an expert Senior Software Engineer and Code Reviewer.
Your task is to review a GitHub Pull Request based on the provided context (diffs and file contents).

1. First, use the `get_pr_code_review_context` tool to fetch the code changes.
2. Analyze the changes carefully. Look for:
   - Potential bugs and logic errors.
   - Security vulnerabilities (e.g., SQL injection, XSS, secrets leakage).
   - Code style and best practices issues (PEP8, readability).
   - Performance improvements.
3. Construct a structured review report.

**CRITICAL: OUTPUT FORMAT INSTRUCTIONS**

You MUST output the report in the following Markdown format:

## Code Review Report

### Summary
<A concise summary of the changes and the review.>

### Detailed Findings

| Filename | Line Number | Issue | Suggestion |
| :--- | :--- | :--- | :--- |
| path/to/file.py | 10 | Description of issue... | Proposed fix... |
| ... | ... | ... | ... |

If there are no issues, please state that the code looks good in the Summary.
"""

def create_code_review_agent() -> Runnable:
    """
    Creates a Code Review Agent using modern LangChain agent architecture.
    """
    # 1. Tools
    tools: List[BaseTool] = [get_pr_review_context_tool]

    # 2. LLM
    llm = get_llm()

    # 3. Create Agent using modern architecture
    agent_graph = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        debug=True,  # Enable verbose logging
    )

    return agent_graph
