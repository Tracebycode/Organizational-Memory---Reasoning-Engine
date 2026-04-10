"""
Ingestion Layer — Entry Point.

FastAPI application that ingests raw conversation text, extracts
structured decisions via an LLM agent (Ollama / phi3), and forwards
them to the Organizational Memory backend.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import router

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    datefmt="%H:%M:%S",
)

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Ingestion Layer — Organizational Memory Engine",
    description=(
        "Accepts raw conversation text, extracts structured decisions "
        "using Ollama (phi3), and stores them via the backend API."
    ),
    version="1.0.0",
)

# CORS — allow the frontend and other local services to hit the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the ingestion routes
app.include_router(router)


@app.get("/")
def root():
    """Root endpoint — quick status check."""
    return {
        "service": "ingestion-layer",
        "status": "running",
        "docs": "/docs",
    }
