
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
        result = await llm_service.ainvoke("Hello, introduce yourself in one sentence.")
        logger.info("LLMService response:")
        logger.info(result.content)
    except Exception as e:
        logger.error(f"Error during LLMService invocation: {e}")