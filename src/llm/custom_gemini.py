import os
from typing import Any, List, Optional
from loguru import logger

from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_google_genai import ChatGoogleGenerativeAI

class CustomGeminiChatModel(BaseChatModel):
    """
    一个集成了 LangChain BaseChatModel 的自定义 Gemini LLM 类。
    """
    client: Any = None  # 内部 LangChain Gemini 客户端
    model_name: str = "gemini-2.5-pro"
    temperature: float = 0.7

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables.")
        
        self.client = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=api_key,
            temperature=self.temperature,
            transport="rest",
            **kwargs
        )

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        同步生成聊天响应。
        """
        # LangChain 的 generate 方法期望 prompts 是一个列表的列表
        # LLMResult.generations 也是一个列表的列表，每个内部列表对应一个 prompt
        llm_result = self.client.generate(
            [messages], stop=stop, callbacks=run_manager, **kwargs
        )
        # _generate 需要返回 ChatResult，其 generations 是一个单层列表
        # 我们只处理了单个 prompt，所以取第一个结果
        generations = llm_result.generations[0]
        return ChatResult(generations=generations)

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        异步生成聊天响应。
        """
        llm_result = await self.client.agenerate(
            [messages], stop=stop, callbacks=run_manager, **kwargs
        )
        generations = llm_result.generations[0]
        return ChatResult(generations=generations)

    @property
    def _llm_type(self) -> str:
        """返回语言模型的类型。"""
        return "custom_gemini_chat_model"

# 如果需要，可以添加一个简单的测试
if __name__ == '__main__':
    # 确保 .env 文件被加载
    # 简单的测试需要项目根目录在 sys.path 中
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from src.configs.config import app_env # 这会触发 dotenv load

    print("测试自定义 Gemini Chat Model...")
    try:
        custom_llm = CustomGeminiChatModel()
        result = custom_llm.invoke("你好，用一句话介绍你自己。")
        print("模型响应:")
        print(result.content)
    except Exception as e:
        print(f"发生错误: {e}")
