
import src.configs.config
from src.llm.custom_gemini import CustomGeminiChatModel
from src.services.llm_service import LLMService
from loguru import logger
import pytest
def test_llm_invoke():


    print("Testing CustomGeminiChatModel.invoke...")
    try:
        custom_llm = CustomGeminiChatModel()
        result = custom_llm.invoke("Hello, introduce yourself in one sentence.")
        logger.info("Model response:")
        logger.info(result.content)
    except Exception as e:
        logger.error(f"Error during invocation: {e}")




@pytest.mark.asyncio
async def test_invoke():
    logger.info("Testing LLMService with CustomGeminiChatModel...")
    try:
        custom_llm = CustomGeminiChatModel()
        llm_service = LLMService(custom_llm)
        result = await llm_service.ainvoke("你好吗?")
        logger.info("LLMService response:")
        logger.info(result.content)
        assert result.content is not None
        assert len(result.content) > 0
    except Exception as e:
        logger.error(f"Error during LLMService invocation: {e}")
        pytest.fail(f"LLMService ainvoke failed: {e}")


@pytest.mark.asyncio
async def test_astream():
    logger.info("Testing astream with CustomGeminiChatModel...")
    full_response = ""
    try:
        custom_llm = CustomGeminiChatModel()
        prompt = "Tell me a short story about a brave robot."
        
        logger.info(f"Streaming prompt: '{prompt}'")
        async for chunk in custom_llm.astream(prompt):
            # chunk is an AIMessageChunk object
            print(chunk.content, end="", flush=True)
            full_response += chunk.content
        
        print("\n--- End of Stream ---")
        logger.info(f"Full streamed response: {full_response}")

        assert full_response is not None
        assert len(full_response) > 0
        # assert "robot" in full_response.lower() # 移除关键词断言

    except Exception as e:
        logger.error(f"Error during astream: {e}")
        pytest.fail(f"LLM astream failed: {e}")


@pytest.mark.asyncio
async def test_llm_service_astream():
    logger.info("Testing LLMService.astream...")
    full_response = ""
    try:
        custom_llm = CustomGeminiChatModel()
        llm_service = LLMService(custom_llm)
        prompt = "Write a haiku about Python programming."
        
        logger.info(f"Streaming prompt from service: '{prompt}'")
        async for chunk in llm_service.astream(prompt):
            print(chunk.content, end="", flush=True)
            full_response += chunk.content

        print("\n--- End of Service Stream ---")
        logger.info(f"Full streamed response from service: {full_response}")

        assert full_response is not None
        assert len(full_response) > 0
        # assert "code" in full_response.lower() # 移除关键词断言，因为LLM的输出不确定

    except Exception as e:
        logger.error(f"Error during LLMService astream: {e}")
        pytest.fail(f"LLMService astream failed: {e}")
