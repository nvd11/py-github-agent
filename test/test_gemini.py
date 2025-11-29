import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.llm.factory import get_llm
from loguru import logger

def test_llm_factory():
    """
    Tests that the LLM factory can correctly instantiate a model.
    """
    logger.info("--- Testing LLM Factory ---")
    try:
        llm = get_llm()
        logger.info(f"LLM factory returned instance of: {type(llm).__name__}")
        
        prompt = "Hello, introduce yourself in one sentence."
        result = llm.invoke(prompt)

        assert result is not None
        assert result.content is not None
        assert len(result.content) > 0

        logger.success("LLM factory test passed.")
        print(f"Response from {type(llm).__name__}: {result.content}")

    except Exception as e:
        pytest.fail(f"LLM factory test failed: {e}")

if __name__ == "__main__":
    test_llm_factory()
