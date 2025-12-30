from pydantic import BaseModel, Field

class CodeReviewRequest(BaseModel):
    """
    Request model for triggering a code review.
    """
    pull_request_url: str = Field(..., description="The full URL of the GitHub Pull Request to review.")

class CodeReviewResponse(BaseModel):
    """
    Response model containing the code review report.
    """
    review_report: str = Field(..., description="The markdown formatted code review report.")
