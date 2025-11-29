import os
from typing import Any
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

# 这是一个很好的问题！答案是：我们不需要，因为我们采用了更简洁的“继承”模式。
#
# - 对于 Gemini:
#   我们创建 `CustomGeminiChatModel(BaseChatModel)`，它是一个“包装器”。
#   它内部持有一个 `ChatGoogleGenerativeAI` 实例 (`self.client`)。
#   因为我们是从最基础的 `BaseChatModel` 开始的，所以我们必须自己实现 `_generate`，
#   并将调用“委托”给我们内部的 `self.client`。
#
# - 对于 DeepSeek:
#   因为 DeepSeek 的 API 与 OpenAI 兼容，我们可以利用 LangChain 已有的 `ChatOpenAI` 类。
#   `ChatOpenAI` 已经为您实现了所有必需的方法（包括 `_generate`）。
#   我们可以直接“继承” `ChatOpenAI`，然后在初始化 (`__init__`) 时，
#   通过 `super().__init__(...)` 传入 DeepSeek 特有的参数（如 `base_url` 和 `api_key`）。
#
# 这种继承的方式代码更少，更直接，因为它重用了 `ChatOpenAI` 已经写好的所有功能。

class CustomDeepSeekChatModel(ChatOpenAI):
    """
    一个集成了 DeepSeek 模型的自定义 LLM 类。
    通过继承 ChatOpenAI 并覆盖 API 地址和密钥来实现。
    """
    def __init__(self, model_name: str = "deepseek-chat", temperature: float = 0.7, **kwargs: Any):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables.")
        
        # DeepSeek 的 API base URL
        base_url = "https://api.deepseek.com/v1"

        # 调用父类 (ChatOpenAI) 的构造函数，并传入 DeepSeek 的特定参数
        super().__init__(
            model=model_name,
            temperature=temperature,
            api_key=api_key,
            base_url=base_url,
            **kwargs
        )

# 如果需要，可以添加一个简单的测试
if __name__ == '__main__':
    # 动态添加项目根目录到 sys.path
    import sys
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.append(project_root)

    # 导入 config 会触发 dotenv load
    from src.configs import config

    print("测试自定义 DeepSeek Chat Model...")
    try:
        llm = CustomDeepSeekChatModel()
        result = llm.invoke("你好，用一句话介绍你自己，并说明你是谁开发的。")
        print("模型响应:")
        print(result.content)
    except Exception as e:
        print(f"发生错误: {e}")
