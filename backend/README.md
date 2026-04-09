# Backend - Organizational Memory Engine

The backend service that powers the multi-agent AI decision reasoning system.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────┐
│          FastAPI Application            │
├─────────────────────────────────────────┤
│         API Routes (routes.py)          │
├─────────────────────────────────────────┤
│    BrainOrchestrator (orchestrator.py)  │
├──────────┬──────────┬──────────────┐────┤
│          │          │              │    │
│ Retrieval│ Reasoning│ Answer       │    │
│ Agent    │ Agent    │ Agent        │    │
└──────────┴──────────┴──────────────┘    │
          │                                │
          ▼                                │
   ┌────────────────┐                     │
   │  VectorStore   │                     │
   │  (ChromaDB)    │                     │
   │  (Embeddings)  │                     │
   └────────────────┘                     │
          │                                │
          ▼                                │
   ┌────────────────────┐                 │
   │  chroma_data/      │                 │
   │  (Persistent DB)   │                 │
   └────────────────────┘                 │
```

## 📂 File Structure

```
backend/
├── main.py                     # FastAPI app initialization & startup
├── requirement.txt             # Python dependencies (pinned versions)
├── .env                        # Environment configuration (create this)
├── .env.example               # Template for .env file
├── chroma_data/               # ChromaDB persistence directory (auto-created)
│
├── api/
│   └── routes.py              # All FastAPI endpoints
│       ├── POST /store-decision
│       ├── POST /ask
│       └── GET  /health
│
├── brain/
│   ├── orchestrator.py        # Main BrainOrchestrator class
│   │   ├── store_decision()   # Controller for storing
│   │   └── ask_question()     # Controller for querying
│   │
│   ├── retrieval_agent.py     # Semantic search agent
│   │   └── retrieve()         # Query vector store
│   │
│   ├── reasoning_agent.py     # LLM reasoning agent
│   │   └── reason()           # Generate reasoning via Ollama
│   │
│   ├── answer_agent.py        # Response building agent
│   │   └── build()            # Format final response
│   │
│   ├── vector_store.py        # ChromaDB wrapper
│   │   ├── store()            # Add decision to DB
│   │   └── search()           # Semantic search
│   │
│   └── memory_manager.py      # (Reserved for future use)
│
├── models/
│   └── schema.py              # Pydantic models
│       ├── DecisionInput      # Request schema
│       ├── AskInput           # Request schema
│       ├── DecisionResponse   # Response schema
│       ├── AskResponse        # Response schema
│       └── ErrorResponse      # Error schema
│
└── config/
    └── settings.py            # Configuration management
        ├── OLLAMA_*           # LLM settings
        ├── CHROMA_*           # Vector DB settings
        └── LOG_LEVEL          # Logging configuration
```

## 🚀 Setup & Run

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirement.txt
```

**Dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `chromadb` - Vector database
- `sentence-transformers` - Embeddings
- `ollama` - LLM integration
- `pydantic` - Data validation
- `python-dotenv` - Config management

### 3. Configure Environment

Create `.env` file:

```env
# Ollama LLM Configuration
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

### 4. Start Ollama (separate terminal)

```bash
ollama serve
```

This starts Ollama on `http://localhost:11434`

### 5. Run Backend Server

```bash
uvicorn main:app --reload
```

- `--reload` enables auto-restart on code changes
- API available at `http://localhost:8000`
- Swagger docs at `http://localhost:8000/docs`
- ReDoc at `http://localhost:8000/redoc`

## 📡 API Endpoints Reference

### POST /store-decision
Store a decision in organizational memory.

**Request:**
```json
{
  "decision": "Use PostgreSQL",
  "reason": "Better ACID compliance",
  "source": "tech-meeting-2024"
}
```

**Response (200):**
```json
{
  "status": "stored",
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Response (400):**
```json
{
  "error": "decision and reason fields are required"
}
```

---

### POST /ask
Query organizational memory with a question.

**Request:**
```json
{
  "question": "Why PostgreSQL?"
}
```

**Response (200):**
```json
{
  "answer": "PostgreSQL was chosen for its superior ACID compliance...",
  "sources": [
    {
      "decision": "Use PostgreSQL",
      "reason": "Better ACID compliance",
      "source": "tech-meeting-2024"
    }
  ],
  "timestamp": "2024-04-10T15:30:00Z",
  "success": true
}
```

---

### GET /health
Check system health.

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-04-10T15:30:00Z"
}
```

## 🔍 Code Walkthrough

### main.py - Application Entry Point

```python
from fastapi import FastAPI
from api.routes import router
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Organizational Memory Engine",
    version="0.1.0"
)

# Include API routes
app.include_router(router)

# Root endpoint
@app.get("/")
def root():
    return {"status": "running"}
```

### routes.py - API Endpoints

```python
from fastapi import APIRouter, HTTPException, Depends
from brain.orchestrator import BrainOrchestrator
from models.schema import DecisionInput, AskInput

router = APIRouter()

# Dependency: Fresh brain instance per request (thread-safe)
def get_brain():
    return BrainOrchestrator()

@router.post("/store-decision")
def store(data: DecisionInput, brain = Depends(get_brain)):
    # Pydantic validates request schema
    # FastAPI dependency injection creates per-request instance
    result = brain.store_decision(data.dict())
    return result
```

### orchestrator.py - Main Controller

```python
class BrainOrchestrator:
    def __init__(self):
        # Initialize all agents
        self.memory = VectorStore()
        self.retriever = RetrievalAgent()
        self.reasoner = ReasoningAgent()
        self.answer_agent = AnswerAgent()
    
    def ask_question(self, question):
        # Coordinate agents
        context, metadata = self.retriever.retrieve(self.memory, question)
        reasoning = self.reasoner.reason(question, context)
        return self.answer_agent.build(reasoning, metadata)
```

### retrieval_agent.py - Vector Search

```python
class RetrievalAgent:
    def retrieve(self, memory, question):
        # Query vector database
        results = memory.search(question)
        # Extract documents and metadata
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        return "\n\n".join(docs), metas
```

### reasoning_agent.py - LLM Interaction

```python
class ReasoningAgent:
    def __init__(self):
        self.model = "phi3:mini"
    
    def reason(self, question, context):
        # Build prompt with context
        prompt = f"Question: {question}\nContext: {context}"
        # Call Ollama LLM with error handling
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]
```

### vector_store.py - Embeddings & Search

```python
class VectorStore:
    def __init__(self):
        # Persistent ChromaDB
        self.client = chromadb.PersistentClient(path="./chroma_data")
        self.collection = self.client.get_or_create_collection("decisions")
        # Sentence embeddings model
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    def store(self, text, metadata):
        # Encode text to embedding
        embedding = self.embedding_model.encode(text)
        # Store in ChromaDB
        self.collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata],
            ids=[str(uuid.uuid4())]
        )
    
    def search(self, query):
        # Encode query
        embedding = self.embedding_model.encode(query)
        # Semantic search
        return self.collection.query(
            query_embeddings=[embedding],
            n_results=3
        )
```

## 🧪 Testing

### Manual Testing with curl

```bash
# Store a decision
curl -X POST "http://localhost:8000/store-decision" \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "Use FastAPI",
    "reason": "Fast, modern, built-in validation",
    "source": "tech-stack-meeting"
  }'

# Ask a question
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Why do we use FastAPI?"}'

# Health check
curl "http://localhost:8000/health"
```

### Swagger Interactive Testing

1. Run: `uvicorn main:app --reload`
2. Visit: `http://localhost:8000/docs`
3. Test endpoints directly in browser with "Try it out"

### Debugging with Logs

```python
# Log level in .env
LOG_LEVEL=DEBUG

# View logs in terminal output
# Each agent logs its activities
```

## ⚡ Performance Tips

### Reduce Latency

1. **Cache frequent queries:**
   - ChromaDB caches embeddings (first query slower, rest faster)

2. **Reduce token count:**
   - Adjust `OLLAMA_MAX_TOKENS` in `.env` (lower = faster)

3. **Optimize temperature:**
   - Low temperature (0.2) = more deterministic = sometimes faster

4. **Keep Ollama warm:**
   - Don't stop Ollama between requests
   - First request loads model (~2s), rest are faster

### Monitor Performance

```bash
# Check memory usage
# Check Ollama load: http://localhost:11434/api/tags

# Watch request logs
tail -f output.log
```

## 🐛 Debugging

### Issue: Ollama connection refused

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve
```

### Issue: "No decision found"

```bash
# Store some test data first
curl -X POST "http://localhost:8000/store-decision" \
  -H "Content-Type: application/json" \
  -d '{"decision":"Test","reason":"Testing","source":"test"}'
```

### Issue: ChromaDB persistence not working

```bash
# Check chroma_data directory exists
ls -la ./chroma_data/

# If missing, restart app to auto-create
uvicorn main:app --reload
```

### Issue: Slow responses

```bash
# Check OLLAMA_MAX_TOKENS in .env - reduce if high
# Check vector DB size: du -sh ./chroma_data/

# Enable debug logging
LOG_LEVEL=DEBUG
```

### Enable Debug Logging

```python
# In main.py
import logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 📊 Data Persistence

**ChromaDB Storage:**
- Location: `./chroma_data/`
- Format: SQLite + vector data
- Persists between app restarts
- Safe to backup/restore

**In Memory:**
- Orchestrator instance per request (fresh)
- Agent instances (fresh per request)
- Embedding model (loaded once, cached)

**Important:** Don't delete `./chroma_data/` or data will be lost!

## 🔐 Security Notes

**Current Limitations:**
- No authentication (open API)
- No rate limiting
- No input sanitization beyond Pydantic validation
- Running on localhost only

**For Production:**
- Add JWT authentication
- Add rate limiting (FastAPI-limiter)
- Input validation & XSS prevention
- HTTPS/SSL
- CORS configuration
- SQL injection protection (ChromaDB safe by default)

## 📚 Dependencies Deep Dive

| Package | Purpose | Version |
|---------|---------|---------|
| fastapi | Web framework | 0.104.1 |
| uvicorn | ASGI server | 0.24.0 |
| chromadb | Vector database | 0.4.0 |
| sentence-transformers | Embeddings | 2.2.2 |
| ollama | LLM SDK | 0.1.12 |
| pydantic | Data validation | 2.4.2 |
| python-dotenv | Config loading | 1.0.0 |

## 🎯 Common Tasks

### Add a new endpoint

```python
# In api/routes.py
@router.get("/my-new-endpoint")
def my_endpoint():
    return {"message": "Hello"}
```

### Change LLM model

```bash
# In .env
OLLAMA_MODEL=mistral
# Or: phi3:medium, llama2, neural-chat, etc.
```

### Clear all stored decisions

```bash
# Stop the app
# Delete the database
rm -rf ./chroma_data/

# Restart app (will recreate empty DB)
uvicorn main:app --reload
```

### Export all decisions

```bash
# Add endpoint to routes.py
@router.get("/export")
def export_all(brain = Depends(get_brain)):
    results = brain.memory.collection.get()
    return results
```

## 📖 References

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Ollama Models](https://ollama.ai/library)
- [Sentence Transformers](https://www.sbert.net/)
- [Pydantic Docs](https://docs.pydantic.dev/)

## 🤝 Contributing

### Code Style
- Use PEP 8 naming conventions
- Add docstrings to functions
- Use type hints
- Keep functions focused (single responsibility)

### Adding Features
1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes with tests
3. Update README if needed
4. Commit with clear messages
5. Push and create PR

## 📝 Changelog

### v0.1.0 (April 10, 2026)
- Initial multi-agent system
- Store/retrieve decisions
- LLM-powered reasoning
- Vector semantic search
- ChromaDB persistence
- FastAPI routes with validation
- Comprehensive error handling

---

**Last Updated:** April 10, 2026  
**Project:** Sunhacks 2024 Hackathon
