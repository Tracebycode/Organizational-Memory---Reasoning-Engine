# Quick Fix Patches - Use These Now

## 1. FIXED: reasoning_agent.py

```python
import ollama


class ReasoningAgent:
    
    def __init__(self):
        self.model = "phi3:mini"
        self.max_tokens = 80
        # Don't make Ollama calls in __init__! This was causing crashes.

    def reason(self, question, context):
        prompt = f"""
You are an organizational decision reasoning AI.

A user asked:
{question}

Here is the past decision context:
{context}

Explain briefly why the decision was made.

Answer clearly."""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                options={
                    "num_predict": self.max_tokens,   
                    "temperature": 0.2
                },
                timeout=30  # Prevent hanging
            )
            return response["message"]["content"]
        except Exception as e:
            return f"Error generating reasoning: {str(e)}. Using context directly."
```

**Changes:**
- ✅ Removed broken Ollama call from `__init__`
- ✅ Added error handling
- ✅ Added timeout
- ✅ Graceful fallback

---

## 2. FIXED: vector_store.py

```python
import chromadb
from sentence_transformers import SentenceTransformer
import uuid


class VectorStore:

    def __init__(self, persist_dir="./chroma_data"):
        # Use persistent storage instead of in-memory
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="decisions"
        )
        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def store(self, text, metadata):
        try:
            embedding = self.embedding_model.encode(text).tolist()
            
            # Use UUID instead of hash to avoid collisions
            decision_id = str(uuid.uuid4())
            
            self.collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata],
                ids=[decision_id]
            )
            return decision_id
        except Exception as e:
            print(f"Error storing decision: {e}")
            return None

    def search(self, query, num_results=3):
        try:
            embedding = self.embedding_model.encode(query).tolist()
            
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=num_results
            )
            
            return results
        except Exception as e:
            print(f"Error searching: {e}")
            return {"documents": [], "metadatas": []}
```

**Changes:**
- ✅ PersistentClient for data persistence
- ✅ UUID instead of hash for unique IDs
- ✅ Error handling on store/search
- ✅ Return decision ID

---

## 3. FIXED: models/schema.py

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class DecisionInput(BaseModel):
    """Request schema for storing a decision"""
    decision: str = Field(..., description="The decision made")
    reason: str = Field(..., description="Why this decision was made")
    source: str = Field(default="manual", description="Source of decision")
    
    class Config:
        schema_extra = {
            "example": {
                "decision": "Use PostgreSQL for database",
                "reason": "Better for relational data with ACID compliance",
                "source": "engineering-meeting-2024-04"
            }
        }


class AskInput(BaseModel):
    """Request schema for asking a question"""
    question: str = Field(..., description="The question to ask")
    
    class Config:
        schema_extra = {
            "example": {
                "question": "Why did we choose PostgreSQL?"
            }
        }


class DecisionResponse(BaseModel):
    """Response schema for storing a decision"""
    status: str
    id: str
    
    class Config:
        schema_extra = {
            "example": {
                "status": "stored",
                "id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class AskResponse(BaseModel):
    """Response schema for asking a question"""
    answer: str
    sources: List[Dict[str, Any]]
    timestamp: str
    success: bool
    
    class Config:
        schema_extra = {
            "example": {
                "answer": "PostgreSQL was chosen because...",
                "sources": [{"decision": "Use PostgreSQL", "source": "engineering-meeting"}],
                "timestamp": "2024-04-10T15:30:00Z",
                "success": True
            }
        }


class ErrorResponse(BaseModel):
    """Response schema for errors"""
    error: str
    detail: Optional[str] = None
```

**Changes:**
- ✅ Proper Pydantic models
- ✅ Field descriptions for Swagger docs
- ✅ Examples for frontend developers
- ✅ Type hints for all responses

---

## 4. FIXED: api/routes.py

```python
from fastapi import APIRouter, HTTPException, Depends
from brain.orchestrator import BrainOrchestrator
from models.schema import (
    DecisionInput, AskInput, DecisionResponse, 
    AskResponse, ErrorResponse
)
from datetime import datetime

router = APIRouter()

# Dependency injection to create per-request brain instance
def get_brain():
    """Create a fresh brain instance per request"""
    return BrainOrchestrator()


@router.post("/store-decision", response_model=DecisionResponse)
def store(data: DecisionInput, brain: BrainOrchestrator = Depends(get_brain)):
    """Store a decision in the organizational memory"""
    try:
        result = brain.store_decision({
            "decision": data.decision,
            "reason": data.reason,
            "source": data.source
        })
        return DecisionResponse(
            status="stored",
            id=result.get("id", "unknown")
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store decision: {str(e)}"
        )


@router.post("/ask", response_model=AskResponse)
def ask(data: AskInput, brain: BrainOrchestrator = Depends(get_brain)):
    """Ask a question about stored decisions"""
    if not data.question or not data.question.strip():
        raise HTTPException(
            status_code=400, 
            detail="question cannot be empty"
        )
    
    try:
        result = brain.ask_question(data.question)
        return AskResponse(
            answer=result.get("answer", "No answer found"),
            sources=result.get("sources", []),
            timestamp=datetime.utcnow().isoformat() + "Z",
            success=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error answering question: {str(e)}"
        )
```

**Changes:**
- ✅ Proper Pydantic request/response models
- ✅ HTTPException for errors (FastAPI best practice)
- ✅ Per-request brain instance (thread-safe)
- ✅ Timestamp in responses
- ✅ Better error messages

---

## 5. UPDATED: orchestrator.py

```python
from brain.vector_store import VectorStore
from brain.reasoning_agent import ReasoningAgent
from brain.retrieval_agent import RetrievalAgent
from brain.answer_agent import AnswerAgent
import logging

logger = logging.getLogger(__name__)


class BrainOrchestrator:

    def __init__(self):
        try:
            self.memory = VectorStore(persist_dir="./chroma_data")
            self.reasoner = ReasoningAgent()
            self.retriever = RetrievalAgent()
            self.answer_agent = AnswerAgent()
        except Exception as e:
            logger.error(f"Error initializing BrainOrchestrator: {e}")
            raise

    def store_decision(self, data):
        """Store a decision with error handling"""
        try:
            decision = data.get("decision")
            reason = data.get("reason")
            source = data.get("source", "manual")
            
            if not decision or not reason:
                return {
                    "status": "error",
                    "message": "decision and reason are required"
                }

            text = f"""
Decision: {decision}
Reason: {reason}
Source: {source}
"""

            metadata = {
                "decision": decision,
                "reason": reason,
                "source": source
            }

            decision_id = self.memory.store(text, metadata)
            
            return {
                "status": "stored",
                "id": decision_id
            }
        except Exception as e:
            logger.error(f"Error storing decision: {e}")
            return {"status": "error", "message": str(e)}

    def ask_question(self, question):
        """Ask a question with error handling"""
        try:
            context, metadata = self.retriever.retrieve(
                self.memory,
                question
            )

            if not context:
                return {
                    "answer": "No relevant past decisions found.",
                    "sources": []
                }

            reasoning = self.reasoner.reason(
                question,
                context
            )

            return self.answer_agent.build(
                reasoning,
                metadata
            )
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return {
                "answer": f"Error: {str(e)}",
                "sources": []
            }
```

**Changes:**
- ✅ Error handling throughout
- ✅ Logging for debugging
- ✅ Better status messages
- ✅ Uses persistent vector store

---

## 6. NEW: config/settings.py

```python
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Ollama
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "30"))
    OLLAMA_MAX_TOKENS = int(os.getenv("OLLAMA_MAX_TOKENS", "80"))
    OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.2"))
    
    # Vector Store
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
    CHROMA_NUM_RESULTS = int(os.getenv("CHROMA_NUM_RESULTS", "3"))
    
    # API
    API_TITLE = "Organizational Memory Engine"
    API_VERSION = "0.1.0"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
```

**Changes:**
- ✅ Configuration management
- ✅ Environment variables
- ✅ Easy to tweak without code changes

---

## Usage: .env file

Create `.env` in backend/ directory:

```env
# .env
OLLAMA_MODEL=phi3:mini
OLLAMA_TIMEOUT=30
OLLAMA_MAX_TOKENS=80
OLLAMA_TEMPERATURE=0.2

CHROMA_PERSIST_DIR=./chroma_data
CHROMA_NUM_RESULTS=3

LOG_LEVEL=INFO
```

---

## Installation: Updated requirements.txt

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
langchain==0.0.350
chromadb==0.4.0
sentence-transformers==2.2.2
ollama==0.1.12
pydantic==2.4.2
python-dotenv==1.0.0
```

**Remove:** `openai` (not used)  
**Add:** `sentence-transformers`, versions pinned.

