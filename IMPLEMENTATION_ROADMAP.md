# 🚀 Hackathon Implementation Roadmap

## 🎯 Goal: Have a working demo that doesn't crash

---

## ⏱️ PHASE 1: CRITICAL (Next 2 hours) - Make It Not Crash

### Task 1.1: Fix ReasoningAgent.__init__ (10 min)
**File to fix:** `backend/brain/reasoning_agent.py`  
**Why:** App crashes on startup

```python
# CHANGE THIS:
def __init__(self):
    ollama.chat(...)  # ❌ Syntax error, crashes

# TO THIS:
def __init__(self):
    self.model = "phi3:mini"  # ✅ Just store config
```

---

### Task 1.2: Make Vector Store Persistent (10 min)
**File to fix:** `backend/brain/vector_store.py`  
**Why:** Data lost on app restart = demo restart loses all data

```python
# CHANGE THIS:
self.client = chromadb.Client()  # ❌ Ephemeral

# TO THIS:
self.client = chromadb.PersistentClient(path="./chroma_data")  # ✅ Persistent
```

---

### Task 1.3: Fix Thread Safety (Global Brain) (15 min)
**File to fix:** `backend/api/routes.py`  
**Why:** Multiple concurrent requests corrupt data

```python
# CHANGE THIS:
brain = BrainOrchestrator()  # ❌ Global, shared

# TO THIS:
def get_brain():
    return BrainOrchestrator()  # ✅ Fresh per request

@router.post("/store-decision")
def store(data: dict, brain = Depends(get_brain)):  # ✅ Injected
    return brain.store_decision(data)
```

---

### Task 1.4: Add Error Handling for Ollama (20 min)
**File to fix:** `backend/brain/reasoning_agent.py`  
**Why:** Ollama might be down, need graceful failure

```python
# WRAP the ollama.chat() call:
try:
    response = ollama.chat(...)
    return response["message"]["content"]
except Exception as e:
    return f"Error reaching LLM: {str(e)}"  # Graceful fallback
```

---

### Task 1.5: Add Pydantic Schemas (15 min)
**File to create:** `backend/models/schema.py`  
**File to fix:** `backend/api/routes.py`  
**Why:** Type safety, API documentation

```python
# Create models/schema.py:
from pydantic import BaseModel

class DecisionInput(BaseModel):
    decision: str
    reason: str
    source: str = "manual"

class AskInput(BaseModel):
    question: str

# Update routes.py:
@router.post("/store-decision")
def store(data: DecisionInput):  # ✅ Validated schema
    ...
```

---

### Task 1.6: Create .env Configuration (5 min)
**File to create:** `backend/.env`  
**File to create:** `backend/config/settings.py`  
**Why:** Easy to switch models without code changes

---

**PHASE 1 TOTAL: ~75 minutes**

✅ **What you get: App doesn't crash on startup, persists data, handles basic errors**

---

## ⏱️ PHASE 2: ROBUST (Next 2 hours) - Make The Demo Look Good

### Task 2.1: Add Logging (20 min)
**File to fix:** All files  
**Why:** Can debug when demo goes wrong

```python
import logging
logger = logging.getLogger(__name__)

# In every important place:
logger.info(f"Storing decision: {decision}")
logger.error(f"Error: {e}")
```

---

### Task 2.2: Add Response Timestamps (10 min)
**File to fix:** `backend/api/routes.py`  
**Why:** Show system is working in real-time

```python
from datetime import datetime

return {
    "answer": "...",
    "sources": [...],
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "success": True
}
```

---

### Task 2.3: Improve Error Messages (15 min)
**File to fix:** `backend/brain/vector_store.py`, `reasoning_agent.py`  
**Why:** Frontend needs to know what went wrong

```python
# INSTEAD OF: "Error"
# PROVIDE: "Error: Ollama server unavailable. Is it running? Try: ollama serve"
```

---

### Task 2.4: Add Health Check Endpoint (10 min)
**File to create:** Add to `backend/api/routes.py`  
**Why:** Judge can verify system is working

```python
@router.get("/health")
def health():
    return {
        "status": "healthy",
        "ollama": "connected",
        "vectordb": "ready"
    }
```

---

### Task 2.5: Return Decision IDs (10 min)
**File to fix:** `backend/brain/vector_store.py`, `orchestrator.py`  
**Why:** Users can track stored decisions

```python
decision_id = str(uuid.uuid4())
return {"status": "stored", "id": decision_id}
```

---

### Task 2.6: Cache Frequently Asked Questions (20 min)
**File to create:** `backend/services/cache.py`  
**Why:** Repeat questions answered instantly

```python
cache = {}
if question in cache:
    return cache[question]  # Instant response!
```

---

**PHASE 2 TOTAL: ~85 minutes**

✅ **What you get: Professional-looking response, traceability, fast repeat queries**

---

## ⏱️ PHASE 3: IMPRESSIVE (Remaining time) - Polish

### Task 3.1: Add Response Ranking (20 min)
**Why:** Show confidence score

```python
{
    "answer": "...",
    "confidence": 0.87,  # How sure are we?
    "sources": [...]
}
```

---

### Task 3.2: Batch Store Decisions (15 min)
**Why:** Support bulk import of past decisions

```python
@router.post("/store-decisions-batch")
def store_batch(decisions: List[DecisionInput]):
    ...
```

---

### Task 3.3: Add Query History (15 min)
**Why:** Show examples in UI

```python
@router.get("/query-history")
def get_history():
    return [
        {"question": "...", "answer": "..."},
        {"question": "...", "answer": "..."}
    ]
```

---

### Task 3.4: Export Decisions CSV (15 min)
**Why:** Impressive data export feature

```python
@router.get("/export")
def export():
    return decisions_as_csv()
```

---

**PHASE 3 TOTAL: ~65 minutes**

✅ **What you get: Impressive features that wow judges**

---

## 📋 Detailed Implementation Steps

### STEP 1: Fix ReasoningAgent (Copy these changes)

**File:** `backend/brain/reasoning_agent.py`

Replace entire file with:
```python
import ollama
import logging

logger = logging.getLogger(__name__)


class ReasoningAgent:
    
    def __init__(self):
        self.model = "phi3:mini"
        self.max_tokens = 80
        self.temperature = 0.2
        logger.info(f"ReasoningAgent initialized with model: {self.model}")

    def reason(self, question, context):
        """Generate reasoning for a decision based on context"""
        prompt = f"""You are an organizational decision reasoning AI.

A user asked:
{question}

Here is the past decision context:
{context}

Explain briefly why the decision was made.
Answer clearly."""

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                options={
                    "num_predict": self.max_tokens,   
                    "temperature": self.temperature
                },
                timeout=30
            )
            answer = response["message"]["content"]
            logger.info("Reasoning generated successfully")
            return answer
        except ollama.ResponseError as e:
            logger.error(f"Ollama error: {e}")
            return "Unable to reach reasoning engine. Please ensure Ollama is running."
        except Exception as e:
            logger.error(f"Unexpected error in reasoning: {e}")
            return f"Error: {str(e)}"
```

---

### STEP 2: Fix Vector Store Persistence

**File:** `backend/brain/vector_store.py`

Replace entire file with:
```python
import chromadb
from sentence_transformers import SentenceTransformer
import uuid
import logging

logger = logging.getLogger(__name__)


class VectorStore:

    def __init__(self, persist_dir="./chroma_data"):
        try:
            self.persist_dir = persist_dir
            self.client = chromadb.PersistentClient(path=persist_dir)
            self.collection = self.client.get_or_create_collection(
                name="decisions"
            )
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info(f"VectorStore initialized with persistence at {persist_dir}")
        except Exception as e:
            logger.error(f"Error initializing VectorStore: {e}")
            raise

    def store(self, text, metadata):
        """Store text with metadata and return unique ID"""
        try:
            embedding = self.embedding_model.encode(text).tolist()
            decision_id = str(uuid.uuid4())
            
            self.collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata],
                ids=[decision_id]
            )
            logger.info(f"Stored decision with ID: {decision_id}")
            return decision_id
        except Exception as e:
            logger.error(f"Error storing decision: {e}")
            return None

    def search(self, query, num_results=3):
        """Search for similar decisions"""
        try:
            embedding = self.embedding_model.encode(query).tolist()
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=num_results
            )
            logger.info(f"Search query returned {len(results['documents'][0])} results")
            return results
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return {"documents": [[]], "metadatas": [[]]}
```

---

### STEP 3: Fix Routes with Schemas

**File:** `backend/models/schema.py`

Create new file:
```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class DecisionInput(BaseModel):
    decision: str = Field(..., description="The decision made", min_length=1)
    reason: str = Field(..., description="Why this decision was made", min_length=1)
    source: str = Field(default="manual", description="Source of decision")


class AskInput(BaseModel):
    question: str = Field(..., description="Question to ask", min_length=1)


class DecisionResponse(BaseModel):
    status: str
    id: Optional[str] = None
    message: Optional[str] = None


class AskResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    timestamp: str
    success: bool
```

---

**File:** `backend/api/routes.py`

Replace with:
```python
from fastapi import APIRouter, HTTPException, Depends
from brain.orchestrator import BrainOrchestrator
from models.schema import DecisionInput, AskInput, DecisionResponse, AskResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def get_brain():
    """Dependency: Create fresh brain instance per request"""
    return BrainOrchestrator()


@router.post("/store-decision", response_model=DecisionResponse)
def store(data: DecisionInput, brain: BrainOrchestrator = Depends(get_brain)):
    """Store a decision in organizational memory"""
    try:
        result = brain.store_decision({
            "decision": data.decision,
            "reason": data.reason,
            "source": data.source
        })
        return DecisionResponse(
            status=result.get("status", "error"),
            id=result.get("id"),
            message=result.get("message")
        )
    except Exception as e:
        logger.error(f"Error storing decision: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask", response_model=AskResponse)
def ask(data: AskInput, brain: BrainOrchestrator = Depends(get_brain)):
    """Ask a question about stored decisions"""
    if not data.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = brain.ask_question(data.question)
        return AskResponse(
            answer=result.get("answer", "No answer found"),
            sources=result.get("sources", []),
            timestamp=datetime.utcnow().isoformat() + "Z",
            success=True
        )
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def health(brain: BrainOrchestrator = Depends(get_brain)):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
```

---

### STEP 4: Update Orchestrator

**File:** `backend/brain/orchestrator.py`

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
            logger.info("BrainOrchestrator initialized")
        except Exception as e:
            logger.error(f"Error initializing BrainOrchestrator: {e}")
            raise

    def store_decision(self, data):
        """Store a decision in memory"""
        try:
            decision = data.get("decision", "").strip()
            reason = data.get("reason", "").strip()
            source = data.get("source", "manual")
            
            if not decision or not reason:
                return {
                    "status": "error",
                    "message": "decision and reason fields are required"
                }

            text = f"""Decision: {decision}
Reason: {reason}
Source: {source}"""

            metadata = {
                "decision": decision,
                "reason": reason,
                "source": source
            }

            decision_id = self.memory.store(text, metadata)
            
            if not decision_id:
                return {"status": "error", "message": "Failed to store decision"}
            
            return {"status": "stored", "id": decision_id}
        except Exception as e:
            logger.error(f"Error in store_decision: {e}")
            return {"status": "error", "message": str(e)}

    def ask_question(self, question):
        """Answer a question using stored decisions"""
        try:
            context, metadata = self.retriever.retrieve(self.memory, question)

            if not context:
                return {
                    "answer": "No relevant past decisions found in memory.",
                    "sources": []
                }

            reasoning = self.reasoner.reason(question, context)

            return self.answer_agent.build(reasoning, metadata or [])
        except Exception as e:
            logger.error(f"Error in ask_question: {e}")
            return {
                "answer": f"Error processing question: {str(e)}",
                "sources": []
            }
```

---

### STEP 5: Update Main with Logging

**File:** `backend/main.py`

```python
from fastapi import FastAPI
from api.routes import router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Organizational Memory Engine",
    version="0.1.0",
    description="Multi-agent AI decision reasoning system"
)

app.include_router(router)


@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {"status": "running", "message": "Organizational Memory Engine v0.1"}


logger.info("FastAPI app initialized")
```

---

### STEP 6: Create .env File

**File:** `backend/.env`

```env
# Ollama Configuration
OLLAMA_MODEL=phi3:mini
OLLAMA_TIMEOUT=30
OLLAMA_MAX_TOKENS=80
OLLAMA_TEMPERATURE=0.2

# Vector Store Configuration
CHROMA_PERSIST_DIR=./chroma_data
CHROMA_NUM_RESULTS=3

# Logging
LOG_LEVEL=INFO
```

---

### STEP 7: Update requirements.txt

**File:** `backend/requirement.txt`

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
chromadb==0.4.0
sentence-transformers==2.2.2
ollama==0.1.12
pydantic==2.4.2
python-dotenv==1.0.0
```

---

## ✅ Testing Checklist

Before demo, verify:

```bash
# 1. Start Ollama
ollama serve

# 2. In another terminal, in backend folder:
python -m pip install -r requirement.txt

# 3. Start API server
uvicorn main:app --reload

# 4. Test endpoints:

# Store a decision
curl -X POST "http://localhost:8000/store-decision" \
  -H "Content-Type: application/json" \
  -d '{"decision": "Use FastAPI", "reason": "Fast and modern"}'

# Ask a question
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Why are we using FastAPI?"}'

# Health check
curl "http://localhost:8000/health"
```

---

## 🎯 Priority for Time-Starved Hackathon

If you only have 1 hour:
1. ✅ MUST DO: Fix ReasoningAgent.__init__ (10 min)
2. ✅ MUST DO: Add error handling for Ollama (10 min)
3. ✅ MUST DO: Fix thread safety (10 min)
4. ✅ MUST DO: Make vector store persistent (10 min)
5. ✅ MUST DO: Add Pydantic schemas (15 min)

**Total: 55 minutes**

Then spend remaining time:
- Testing with actual data
- Fixing any runtime bugs  
- Making UI smooth

---

## 🚨 Demo Day Anti-Patterns

❌ **DON'T:**
- Start from scratch day-of
- Demo without killing/restarting first
- Skip health checks  
- Leave exceptions unhandled
- Use in-memory persistence
- Share state between requests

✅ **DO:**
- Have a clean startup script
- Test cold restarts
- Log everything
- Have graceful fallbacks
- Use persistent storage
- Test concurrent requests
- Have a demo script ready

