import src.configs.config
from langchain_core.runnables import Runnable
from loguru import logger

class LLMService:
    def __init__(self, runnable: Runnable):
        logger.info("Initializing LLMService...")
        self.runnable = runnable
        logger.info("LLMService initialized.")

    async def ainvoke(self, prompt: str):
        logger.info(f"LLMService ainvoking with prompt: {prompt}")
        response = await self.runnable.ainvoke(prompt)
        logger.info("LLMService ainvocation complete.")
        return response

    async def astream(self, prompt: str):
        """Streams the response from the Runnable (LLM or Agent)."""
        logger.info(f"LLMService astreaming with prompt: {prompt}")
        async for chunk in self.runnable.astream(prompt):
            yield chunk
