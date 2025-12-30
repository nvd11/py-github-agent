from typing import List
from pydantic import BaseModel, Field

class AskRequest(BaseModel):
    """Request model for the /chat/ask endpoint."""
    query: str

class AskResponse(BaseModel):
    """Response model for the /chat/ask endpoint."""
    answer: str

class ReviewFinding(BaseModel):
    """Represents a single finding in a code review."""
    filename: str = Field(description="The path of the file where the issue was found.")
    line_number: int = Field(description="The line number where the issue is located.")
    issue: str = Field(description="A concise description of the issue.")
    suggestion: str = Field(description="A suggestion for how to fix the issue.")

class CodeReviewResult(BaseModel):
    """Represents the full result of a code review."""
    summary: str = Field(description="A markdown summary of the changes and the review.")
    findings: List[ReviewFinding] = Field(description="A list of specific findings.")
