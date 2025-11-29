import src.configs.config
from loguru import logger

from langchain_core.language_models.chat_models import BaseChatModel
from src.configs.config import yaml_configs


def get_llm() -> BaseChatModel:
    """
    LLM 工厂函数。
    根据配置文件中的 `llm.provider` 决定实例化哪个 LLM。
    """
    provider = yaml_configs.get("llm", {}).get("provider", "gemini") # 默认为 gemini
    logger.info(f"LLM provider selected: {provider}")

    if provider == "deepseek":
        from .custom_deepseek import CustomDeepSeekChatModel
        return CustomDeepSeekChatModel()
    elif provider == "gemini":
        from .custom_gemini import CustomGeminiChatModel
        return CustomGeminiChatModel()
    else:
        logger.error(f"Unknown LLM provider: {provider}. Defaulting to Gemini.")
        from .custom_gemini import CustomGeminiChatModel
        return CustomGeminiChatModel()
