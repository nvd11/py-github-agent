import pytest
from loguru import logger
from src.agents.code_review_agent import create_code_review_agent

@pytest.mark.asyncio
async def test_code_review_agent_e2e():
    """
    Test the Code Review Agent end-to-end with a real (closed) PR.
    Verifies that it outputs a Markdown report.
    """
    logger.info("--- Testing Code Review Agent ---")
    
    try:
        agent_executor = create_code_review_agent()
    except Exception as e:
        pytest.fail(f"Failed to setup test: {e}")

    # Target: nvd11/py-github-agent PR #2
    input_text = "Please review pull request #2 in repository nvd11/py-github-agent."

    try:
        logger.info(f"Invoking agent with input: {input_text}")
        # 使用正确的消息格式
        from langchain_core.messages import HumanMessage
        result = await agent_executor.ainvoke({
            "messages": [HumanMessage(content=input_text)]
        })

        logger.info(f"Full Agent Result: {result}")

        # 新的 agent 架构返回消息列表，而不是直接的 output
        messages = result.get("messages", [])
        if messages:
            # 获取最后一个 AI 消息的内容
            last_message = messages[-1]
            if hasattr(last_message, 'content'):
                # 如果内容是字典，提取文本部分
                if isinstance(last_message.content, list) and len(last_message.content) > 0:
                    # 提取第一个文本块的内容
                    output = last_message.content[0].get('text', '') if isinstance(last_message.content[0], dict) else str(last_message.content[0])
                else:
                    output = str(last_message.content)
            else:
                output = str(last_message)
        else:
            output = ""

        logger.info(f"Agent raw output:\n{output}")

        if not output:
            pytest.fail("Agent returned empty output.")

        # 验证输出是否符合 Markdown 格式要求
        assert "## Code Review Report" in output
        assert "### Summary" in output
        assert "### Detailed Findings" in output

        # 验证表格是否存在 (检查列名)
        assert "| Filename | Line Number | Issue | Suggestion |" in output

        logger.success("Successfully verified Code Review Markdown output!")

    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        pytest.fail(f"Agent execution failed: {e}")
