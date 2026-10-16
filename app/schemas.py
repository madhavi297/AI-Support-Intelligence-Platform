"""
Pydantic schemas for request validation and response serialization.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Citation(BaseModel):
    """Represents a retrieved source passage from the knowledge base."""
    source: str = Field(..., description="Document source filename")
    section: str = Field(..., description="Section header or title")
    score: float = Field(..., description="Similarity confidence score (0 to 1)")
    text: str = Field(..., description="Snippet of retrieved knowledge text")


class TicketCreate(BaseModel):
    """Schema for submitting a new customer support ticket."""
    title: str = Field(..., min_length=3, max_length=200, description="Brief summary of the issue")
    description: str = Field(..., min_length=5, max_length=4000, description="Full details of the customer issue")


class TicketUpdate(BaseModel):
    """Schema for human agents to update ticket status, category, or priority."""
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class TicketResponse(BaseModel):
    """Complete ticket representation returned to clients."""
    id: int
    ticket_code: str
    title: str
    description: str
    category: Optional[str] = None
    confidence: Optional[float] = None
    priority: str = "Medium"
    priority_reason: Optional[str] = None
    status: str = "open"
    suggested_response: Optional[str] = None
    citations: List[Citation] = []
    created_at: str
    updated_at: str


class TicketAnalysisResult(BaseModel):
    """Output of ML classification, priority heuristic, and RAG retrieval."""
    ticket_code: str
    predicted_category: str
    confidence: float
    probabilities: Dict[str, float]
    priority: str
    priority_reason: str
    relevant_knowledge: List[Citation]


class DraftResponseRequest(BaseModel):
    """Request payload to trigger LLM response generation."""
    custom_instructions: Optional[str] = Field(None, description="Optional extra instructions for tone or policy")


class DraftResponseResult(BaseModel):
    """Generated response draft with citations and generation metadata."""
    ticket_code: str
    draft_response: str
    citations: List[Citation]
    provider_used: str
    is_fallback: bool


class KnowledgeSearchRequest(BaseModel):
    """Query schema for vector knowledge search."""
    query: str = Field(..., min_length=2, description="Search query string")
    top_k: Optional[int] = Field(3, ge=1, le=10, description="Number of results to retrieve")


class HealthResponse(BaseModel):
    """System health and operational status schema."""
    status: str
    app_name: str
    environment: str
    classifier_ready: bool
    knowledge_base_chunks: int
    llm_provider: str
