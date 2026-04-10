"""
Ingestion Layer Routes.

Defines the POST /ingest endpoint that:
  1. Accepts raw conversation text
  2. Extracts a structured decision via the LLM agent
  3. Forwards the decision to the backend /store-decision API
  4. Returns the stored result
"""

import logging

from fastapi import APIRouter, HTTPException

from schema import IngestRequest, IngestResponse, ErrorResponse
from decision_extractor import DecisionExtractor, ExtractionError
from backend_client import BackendClient, BackendError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Ingestion"])

# ---------------------------------------------------------------------------
# Shared instances (created once, reused across requests)
# ---------------------------------------------------------------------------
extractor = DecisionExtractor()
backend = BackendClient()


@router.post(
    "/ingest",
    response_model=IngestResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Extraction failed"},
        502: {"model": ErrorResponse, "description": "Backend communication error"},
    },
    summary="Ingest raw conversation text",
    description=(
        "Accepts raw conversation text, extracts a structured decision "
        "using an LLM agent (Ollama / phi3), and forwards it to the "
        "backend /store-decision API."
    ),
)
async def ingest(request: IngestRequest):
    """
    Main ingestion endpoint.

    Flow:
        raw text → LLM extraction → structured decision → backend storage → response
    """

    # ── Step 1: Extract decision from conversation text ──────────────
    logger.info("Received ingestion request (%d chars)", len(request.text))

    try:
        decision = await extractor.extract(request.text)
        logger.info("Extracted decision: %s", decision.decision)
    except ExtractionError as exc:
        logger.error("Extraction failed: %s", exc)
        raise HTTPException(
            status_code=422,
            detail=f"Decision extraction failed: {exc}",
        )

    # ── Step 2: Forward to backend /store-decision ───────────────────
    try:
        backend_result = await backend.store_decision(decision)
        logger.info("Backend storage result: %s", backend_result)
    except BackendError as exc:
        logger.error("Backend error: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"Backend communication error: {exc}",
        )

    # ── Step 3: Return combined response ─────────────────────────────
    return IngestResponse(
        status=backend_result.get("status", "stored"),
        extracted=decision,
    )


@router.get(
    "/health",
    summary="Health check",
    description="Verifies connectivity to Ollama and the backend.",
)
async def health():
    """Check that external dependencies are reachable."""
    backend_ok = await backend.health_check()
    return {
        "ingestion_layer": "ok",
        "backend_reachable": backend_ok,
        "ollama_model": extractor.model,
    }
