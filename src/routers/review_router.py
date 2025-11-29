from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from src.schemas.review_schemas import CodeReviewRequest, CodeReviewResponse
from src.services.code_review_service import CodeReviewService
from src.agents.code_review_agent import create_code_review_agent

# 1. Create Router
router = APIRouter(
    prefix="/review",
    tags=["review"],
)

# --- Dependency Injection ---
# Create a singleton instance of CodeReviewService
# We create the agent executor once and reuse it
try:
    agent_executor = create_code_review_agent()
    review_service_instance = CodeReviewService(agent_executor)
except Exception as e:
    logger.error(f"Failed to initialize CodeReviewService: {e}")
    # In a real app, this might prevent startup, but for now we log it
    review_service_instance = None

def get_review_service() -> CodeReviewService:
    if review_service_instance is None:
        raise HTTPException(status_code=500, detail="CodeReviewService is not initialized")
    return review_service_instance
# --- End Dependency Injection ---


# 2. Define Endpoint
@router.post("", response_model=CodeReviewResponse)
async def create_code_review(
    request: CodeReviewRequest,
    service: CodeReviewService = Depends(get_review_service)
):
    """
    Triggers an AI code review for the given GitHub Pull Request URL.
    """
    logger.info(f"Received code review request for: {request.pull_request_url}")
    
    result = await service.perform_code_review(request.pull_request_url)
    
    if result.startswith("Error:") or result.startswith("An error occurred"):
         # You might want to return 400 or 500 depending on the error type
         # For now, we return 200 with the error message in the report, or we could raise HTTPException
         # Let's wrap it in the response
         pass
    
    return CodeReviewResponse(review_report=result)
