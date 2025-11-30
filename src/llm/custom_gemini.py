import os
from typing import Any, List, Optional
from loguru import logger

from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForLLMRun,
    CallbackManagerForLLMRun,
)
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration, ChatGenerationChunk
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import AsyncIterator

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
        
        from langchain_google_genai import HarmBlockThreshold, HarmCategory
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        self.client = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=api_key,
            temperature=self.temperature,
            transport="rest",
            safety_settings=safety_settings,
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
        # 调试日志：记录输入
        # logger.info(f"Gemini Request Messages: {messages}")

        llm_result = self.client.generate(
            [messages], stop=stop, callbacks=run_manager, **kwargs
        )
        
        generations = llm_result.generations[0]
        
        # 调试日志：记录输出
        if generations:
            logger.info(f"Gemini Response: {generations[0].text[:200]}...")
        
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

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """流式生成聊天响应。"""
        # 直接将调用委托给内部客户端的 astream 方法，
        # 并将返回的 AIMessageChunk 包装在 ChatGenerationChunk 中。
        async for chunk in self.client.astream(
            messages, stop=stop, callbacks=run_manager, **kwargs
        ):
            yield ChatGenerationChunk(message=chunk)

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
