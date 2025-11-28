from pydantic import BaseModel

class AskRequest(BaseModel):
    """Request model for the /chat/ask endpoint."""
    query: str

class AskResponse(BaseModel):
    """Response model for the /chat/ask endpoint."""
    answer: str
