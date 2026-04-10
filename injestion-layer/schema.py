"""
Pydantic schemas for the ingestion layer.

Defines request/response models for the /ingest endpoint
and the structured decision payload sent to the backend.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class IngestRequest(BaseModel):
    """Raw conversation text submitted for decision extraction."""
    text: str = Field(
        ...,
        min_length=1,
        description="Raw conversation text containing a decision to extract",
        examples=[
            "Dev1: Redis or Memcached?\nDev2: Redis reduces DB load\nLead: Let's use Redis"
        ],
    )


class DecisionPayload(BaseModel):
    """Structured decision data to be sent to the backend /store-decision API."""
    decision: str = Field(..., description="The decision that was made")
    reason: str = Field(..., description="The rationale behind the decision")
    alternatives: List[str] = Field(
        default_factory=list,
        description="Alternative options that were considered",
    )
    impacts: List[str] = Field(
        default_factory=list,
        description="Areas impacted by this decision",
    )
    source: str = Field(
        default="conversation",
        description="Origin of the decision (e.g. conversation, meeting, document)",
    )


class IngestResponse(BaseModel):
    """Response returned after successful ingestion."""
    status: str = Field(..., description="Result status from the backend")
    extracted: DecisionPayload = Field(
        ..., description="The structured decision that was extracted and stored"
    )


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_type: Optional[str] = None
