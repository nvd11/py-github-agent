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
    input_text = "Please review pull request #5 in repository nvd11/py-webhook-svc"
    
    try:
        logger.info(f"Invoking agent with input: {input_text}")
        # 使用 invoke 获取更多调试信息
        result = await agent_executor.ainvoke({"input": input_text})
        
        logger.info(f"Full Agent Result: {result}")
        
        output = result.get("output", "")
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
