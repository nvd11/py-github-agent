from fastapi import APIRouter, Depends
from loguru import logger

from src.services.llm_service import LLMService
from src.schemas.chat_schemas import AskRequest, AskResponse
from src.llm.factory import get_llm

# 1. 创建 Router
router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

# --- 依赖注入 ---
# 这是一个简单的实现，在应用启动时创建一个单例
# 更复杂的应用可能会使用更高级的依赖注入容器
llm_model = get_llm()
llm_service_instance = LLMService(llm_model)

def get_llm_service() -> LLMService:
    return llm_service_instance
# --- 依赖注入结束 ---


# 编写端点
@router.post("/ask", response_model=AskResponse)
async def ask(
    request: AskRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    接收一个问题，调用 LLMService 的 ainvoke 方法，并返回答案。
    """
    logger.info(f"Received ask request with query: {request.query}")
    try:
        response = await llm_service.ainvoke(request.query)
        # response 是一个 AIMessage 对象，我们需要提取其内容
        answer_content = response.content if response else "No response from model."
        return AskResponse(answer=answer_content)
    except Exception as e:
        logger.error(f"Error calling LLM service: {e}")
        # 在实际应用中，这里应该返回一个 HTTP 500 错误
        return AskResponse(answer=f"An error occurred: {e}")
