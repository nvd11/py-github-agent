# 解决 Gemini API 连接卡住问题的方案

本文档详细记录了在 `py-github-agent` 项目中，调用 Google Gemini API 时程序卡住（Hang）问题的诊断过程和解决方案。

---

## 问题现象

在通过 `langchain-google-genai` 库调用 Gemini 模型时，程序执行到调用 API 的代码行后便卡住，长时间没有响应，既不返回结果，也不抛出超时或网络错误。

测试代码片段如下：
```python
# test/test_gemini.py
...
response = client.generate_response(prompt) # 程序在此处卡住
...
```

同时，通过日志确认，程序运行时已加载并设置了 `HTTP_PROXY` 和 `HTTPS_PROXY` 环境变量，指向一个本地代理服务器。

## 诊断过程与根本原因

1.  **初步分析**：程序卡住通常与网络连接问题有关。既然已经设置了代理，直接的网络不通应该不是原因。问题很可能出在 **客户端使用的网络协议** 与 **代理服务器** 的兼容性上。

2.  **协议推测**：Google 的现代 API（包括 Gemini）及其客户端库（SDK）为了追求高性能，会优先使用 **gRPC** 作为底层通信协议。gRPC 是一种基于 HTTP/2 的高性能远程过程调用（RPC）框架。

3.  **定位根因**：虽然 gRPC 性能优越，但它对网络中间件（如代理服务器）的要求比传统的 HTTP/1.1 更高。许多标准的 HTTP 代理服务器无法正确处理 gRPC 的长连接和二进制帧，或者需要特殊配置。当 gRPC 连接尝试穿透一个不完全兼容的 HTTP 代理时，可能会导致连接握手失败或协议协商陷入僵局，从而使客户端表现为无限等待（即“卡住”）。

## 解决方案

解决方案是强制客户端库放弃使用 gRPC，转而使用兼容性更好的标准 **REST (HTTP/1.1) API** 进行通信。

具体操作如下：

1.  **编辑文件**：
    `src/llm/gemini_client.py`

2.  **修改代码**：
    在初始化 `ChatGoogleGenerativeAI` 类时，添加 `transport="rest"` 参数。

    **修改前**:
    ```python
    self.llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=self.api_key,
        temperature=temperature
    )
    ```

    **修改后**:
    ```python
    self.llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=self.api_key,
        temperature=temperature,
        transport="rest"  # <--- 强制使用 REST API
    )
    ```

3.  **验证结果**：
    修改后重新运行测试脚本，程序不再卡住，能够正常通过代理与 Gemini API 通信并返回结果。这证明切换到 REST API 成功解决了与代理的兼容性问题。
