# GKE Gateway API: 统一入口下的前后端路由策略

在使用 GKE Gateway API 对外暴露服务时，我们常常需要在一个统一的域名下，通过不同的路径（如 `/app`, `/api`）来访问不同的后端服务。本文档旨在解释为什么前端 UI 应用和后端 API 服务在 `HTTPRoute` 资源中的路由规则有所不同。

## 核心问题

为什么同样是基于路径的路由，前端应用的规则通常需要 `URLRewrite` 过滤器，而后端 API 服务则不需要？

## 前端路由策略: `URLRewrite` 路径剥离

对于单页面应用（SPA）等前端项目，我们通常采用“路径剥离”（Path Stripping）的策略。

### 示例规则

```yaml
# httproute.yaml
...
rules:
  - backendRefs:
    - name: chat-ui-frontend-service # 前端服务
      port: 80
    filters:
    - type: URLRewrite
      urlRewrite:
        path:
          replacePrefixMatch: / # 将匹配到的前缀替换为 "/"
          type: ReplacePrefixMatch
    matches:
    - path:
        type: PathPrefix
        value: /chat # 匹配此前缀
```

### 工作流程

1.  **匹配 (Match)**: 当用户访问 `https://example.com/chat/profile` 时，Gateway 会因为路径以 `/chat` 开头而匹配到此规则。
2.  **重写 (Rewrite)**: 在将请求转发到后端服务 **之前**，`URLRewrite` 过滤器会生效。它将路径中匹配到的前缀 `/chat` **替换**成 `/`。
3.  **转发 (Forward)**: 最终，后端的前端服务 (`chat-ui-frontend-service`) 收到的请求路径是 `/profile`。

### 为什么需要这样做？

这是为了**解耦外部路径和内部路径**。

-   **简化前端开发**: 前端应用（如 React, Vue）在开发时，其内部路由系统通常假设应用运行在网站的根目录 (`/`)。例如，页面链接被编写为 `/profile` 或 `/settings`。
-   **无需修改代码**: `URLRewrite` 过滤器就像一个“翻译官”，它把外部的 `/chat/profile` 翻译成了前端应用能理解的 `/profile`。这样，前端应用就无需为了部署在子目录下而修改任何路由代码，大大简化了部署和维护。

## 后端路由策略: 框架自适应 `root_path`

对于后端 API 服务，我们通常将完整的路径直接转发给它，由其自身框架来处理。

### 示例规则

```yaml
# httproute.yaml
...
rules:
  - backendRefs:
    - name: clusterip-chat-api-svc # 后端服务
      port: 8000
    matches:
    - path:
        type: PathPrefix
        value: /chat-api-svc # 匹配此前缀 (无 Rewrite 过滤器)
```

### 工作流程

1.  **匹配 (Match)**: 当用户访问 `https://example.com/chat-api-svc/users/123` 时，Gateway 匹配到此规则。
2.  **转发 (Forward)**: 因为**没有** `URLRewrite` 过滤器，Gateway 将**完整的路径** `/chat-api-svc/users/123` 直接转发给后端服务。

### 为什么可以这样做？—— 框架的“路径感知”能力

后端服务不需要 `URLRewrite` 的核心原因是：**现代后端框架被设计为能够“感知”并适应它们被部署在哪个URL子路径下。**

我们用一个具体的 FastAPI 代码示例来说明：

假设后端开发者编写了一个简单的 API 端点：
```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

**场景1：没有 `root_path` 配置**
*   此代码只能匹配发送到服务根目录的请求，如 `http://<service-ip>:<port>/users/123`。
*   如果 Gateway 将 `https://example.com/api/users/123` 的请求**原封不动**地转发过来（路径为 `/api/users/123`），FastAPI 会因为找不到匹配的路由而返回 `404 Not Found`。

**场景2：配置了 `root_path`**
现在，我们在启动 FastAPI 时进行配置：
```python
# server.py
# 假设环境变量 ROOT_PATH 的值是 "/api"
app = FastAPI(root_path=os.getenv("ROOT_PATH")) 
```
*   后端开发者的路由代码 `@app.get("/users/{user_id}")` **一行都不需要改**。
*   当 Gateway 再次将路径为 `/api/users/123` 的请求转发过来时，FastAPI 框架会自动识别到 `root_path` 是 `/api`。
*   它会智能地从请求路径中“剥离”掉 `/api` 前缀，用剩下的 `/users/123` 去匹配内部的路由。匹配成功！
*   更妙的是，当生成 API 文档时，FastAPI 会自动把 `root_path` 加回去，告诉前端开发者完整的 API 地址是 `/api/users/123`。

**核心优势**
这种模式让后端开发者可以完全不关心他们的应用最终会被部署在哪个复杂的 URL 路径下。他们只需要像在本地开发一样，专注于编写相对于服务根目录的业务逻辑代码。所有的路径适配工作都由框架在运行时自动处理，这比依赖外部（Gateway）的重写规则更加健壮和清晰。

相比之下，编译好的前端静态应用（HTML/JS/CSS）没有这种运行时的动态适应能力，因此更依赖 Gateway 的 `URLRewrite` 功能来为它们“翻译”路径。

## 总结对比

| 特性 | 前端应用 (UI) | 后端应用 (API) |
| :--- | :--- | :--- |
| **自身路径感知** | 通常假设自己运行在根目录 `/` | **可以被配置**成知道自己运行在子路径下 |
| **解决方案**| 依赖 **Gateway** 使用 `URLRewrite` 剥离前缀 | 依赖 **自身框架** 使用 `root_path` 等配置处理完整路径 |
| **优点** | 无需修改前端代码，部署灵活 | 服务自身逻辑清晰，能明确知道自己的完整 URL 结构 |

通过为不同类型的服务选择合适的路由策略，我们可以构建一个既结构清晰又易于维护的统一入口系统。
