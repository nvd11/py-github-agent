# Gemini 模型流式输出（打字机效果）问题诊断全过程

本文档详细记录了在 `py-github-agent` 项目中，诊断和解决 Google Gemini 模型 `astream` 方法无法产生预期“打字机”效果问题的全过程。

---

## 问题描述

在实现了对 Gemini 和 DeepSeek 模型的动态切换后，我们观察到一个现象：
-   当使用 **DeepSeek** 模型时，调用 `astream` 方法可以获得流畅的、逐词返回的“打字机”效果。
-   当切换到 **Gemini** 模型时，调用相同的 `astream` 方法，响应内容却是“一次性”地完整输出，没有打字机效果。

我们的目标是搞清楚问题原因，并尽可能让 Gemini 也实现流畅的流式输出。

---

## 诊断与修复过程

### 步骤 1：初步诊断 - 缺失 `_astream` 实现

**假设**：问题可能出在我们自定义的 `CustomGeminiChatModel` 封装类上。

**检查**：
我们检查了 `src/llm/custom_gemini.py` 文件，发现它继承自 LangChain 的 `BaseChatModel`，并实现了 `_generate` 和 `_agenerate` 方法，但**没有**实现 `_astream` 方法。

**原因分析**：
根据 LangChain 的工作机制，如果一个 `BaseChatModel` 的子类没有实现 `_astream`，框架会自动提供一个“回退”（fallback）实现。这个回退方案会先调用 `_agenerate` 来获取**完整的**响应内容，然后将整个内容作为一个**单独的数据块 (chunk)** `yield` 出来。这完美地解释了为什么我们会看到一次性输出。

---

### 步骤 2：第一次修复与新问题 (`AttributeError`)

**解决方案**：
我们在 `CustomGeminiChatModel` 中添加 `_astream` 方法的实现，将调用直接委托给其内部持有的 `ChatGoogleGenerativeAI` 客户端。

**代码实现** (`src/llm/custom_gemini.py`):
```python
    async def _astream(self, messages, stop=None, run_manager=None, **kwargs):
        # 直接将调用委托给内部客户端的 astream 方法
        async for chunk in self.client.astream(
            messages, stop=stop, callbacks=run_manager, **kwargs
        ):
            yield chunk
```

**新问题**:
再次运行测试后，程序抛出了一个新的错误：`AttributeError: 'AIMessageChunk' object has no attribute 'message'`。
这个错误发生在 LangChain 的核心代码 `chat_models.py` 中，它表明 `_astream` `yield` 出的数据块类型不符合上层方法的期望。

---

### 步骤 3：第二次修复 - 包装返回值

**诊断**：
`_astream` 方法的类型注解要求返回 `AsyncIterator[ChatGenerationChunk]`。`self.client.astream` 返回的是 `AIMessageChunk`。我们需要将后者包装成前者。

**解决方案**：
修改 `_astream` 方法，将每个 `AIMessageChunk` 包装在 `ChatGenerationChunk` 中再 `yield`。

**代码实现** (`src/llm/custom_gemini.py`):
```python
from langchain_core.outputs import ChatGenerationChunk

# ...

    async def _astream(self, messages, stop=None, run_manager=None, **kwargs):
        async for chunk in self.client.astream(
            messages, stop=stop, callbacks=run_manager, **kwargs
        ):
            yield ChatGenerationChunk(message=chunk)
```

**结果**：
再次运行测试，`AttributeError` 消失，测试成功通过。**但是**，Gemini 的输出**仍然**是一次性的。

---

### 步骤 4：最终诊断 - 隔离变量法

**假设**：既然我们的封装代码在逻辑上已经完全正确，问题可能出在 `ChatGoogleGenerativeAI` 这个底层库本身。

**解决方案**：
为了验证这个假设，我们采用**隔离变量法**。在 `test/services/test_llm_service.py` 中添加一个名为 `test_native_gemini_astream` 的新测试用例。这个测试**完全绕过**我们自己写的 `CustomGeminiChatModel` 和 `LLMService`，**直接**实例化并调用 LangChain 官方的 `ChatGoogleGenerativeAI`。

**代码实现** (`test/services/test_llm_service.py`):
```python
@pytest.mark.asyncio
async def test_native_gemini_astream():
    from langchain_google_genai import ChatGoogleGenerativeAI
    import os

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        transport="rest"
    )
    prompt = "Tell me a long story..."
    
    async for chunk in llm.astream(prompt):
        print(chunk.content, end="", flush=True)
```

**结果**：
运行这个原生测试后，我们发现其行为与通过我们封装类调用时完全一致——对于简短的回答，它仍然是一次性输出。

---

### 步骤 5：用户的关键发现与最终结论

在我们的诊断基础上，您进行了一个关键测试：将提示词换成一个需要很长回答的问题 (`"Tell me a long story..."`)。

**您的发现**：当回答足够长时，Gemini **确实**表现出了流式效果，但它的分块粒度是**逐句（或逐段）**的，而不是像 DeepSeek 那样**逐词**的。

**最终结论**:
-   **问题根源**：Gemini 没有出现预期“打字机”效果的原因，并非我们的代码有 bug，而是 `langchain-google-genai` 库及其依赖的 Google Gemini API 在 REST 模式下的**固有行为**。
-   **行为差异**：不同 LLM 服务商对流式传输的实现策略不同。DeepSeek/OpenAI 实现了细粒度的“逐词”流，而 Gemini 实现了粗粒度的“逐句”流。
-   **代码正确性**：我们编写的所有封装代码，包括 `CustomGeminiChatModel` 和 `LLMService`，都是正确无误的，它们只是忠实地反映了底层库的行为。
