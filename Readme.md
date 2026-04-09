# 🤖 Organizational Memory Engine - Multi-Agent AI System

A FastAPI-based multi-agent AI system for organizational decision reasoning and memory management using local LLMs (Ollama), vector embeddings (ChromaDB), and semantic search.

## 🎯 Project Overview

This system enables organizations to:
- **Store** decisions with reasoning context
- **Retrieve** relevant past decisions using semantic search
- **Reason** about decisions using a local LLM
- **Build** structured responses with source attribution

### Architecture

```
Frontend
  ↓
API Routes (/store-decision, /ask, /health)
  ↓
BrainOrchestrator (Controller)
  ├── RetrievalAgent (Vector search via ChromaDB)
  ├── ReasoningAgent (LLM reasoning via Ollama)
  ├── AnswerAgent (Response formatting)
  └── VectorStore (Persistent embeddings)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Ollama installed and running (`ollama serve`)
- Virtual environment (recommended)

### Installation

1. **Clone and navigate:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

3. **Install dependencies:**
```bash
pip install -r requirement.txt
```

4. **Configure environment:**
```bash
# Copy the .env file template and customize if needed
cp .env.example .env  # Or create your own
```

5. **Start Ollama** (in another terminal):
```bash
ollama serve
```

6. **Run the API server:**
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger documentation.

## 📚 API Endpoints

### Store Decision
```bash
POST /store-decision
Content-Type: application/json

{
  "decision": "Use PostgreSQL for database",
  "reason": "Better for relational data with ACID compliance",
  "source": "engineering-meeting-2024-04"
}

Response:
{
  "status": "stored",
  "id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Ask Question
```bash
POST /ask
Content-Type: application/json

{
  "question": "Why did we choose PostgreSQL?"
}

Response:
{
  "answer": "PostgreSQL was chosen because...",
  "sources": [{"decision": "Use PostgreSQL", "source": "engineering-meeting"}],
  "timestamp": "2024-04-10T15:30:00Z",
  "success": true
}
```

### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2024-04-10T15:30:00Z"
}
```

## 📁 Project Structure

```
├── backend/                      # Backend services
│   ├── main.py                   # FastAPI app entry point
│   ├── requirement.txt           # Python dependencies
│   ├── .env                      # Environment configuration
│   ├── api/
│   │   └── routes.py            # API endpoints
│   ├── brain/                    # AI agents
│   │   ├── orchestrator.py      # Main orchestrator
│   │   ├── reasoning_agent.py   # LLM reasoning
│   │   ├── retrieval_agent.py   # Vector search
│   │   ├── answer_agent.py      # Response builder
│   │   ├── vector_store.py      # ChromaDB wrapper
│   │   └── memory_manager.py    # Memory utilities
│   ├── models/
│   │   └── schema.py            # Pydantic request/response models
│   ├── config/
│   │   └── settings.py          # Configuration management
│   └── chroma_data/             # ChromaDB persistence
├── frontend/                     # Frontend UI (if applicable)
└── README.md                     # This file
```

## 🧠 Multi-Agent System

### Agents

1. **RetrievalAgent**
   - Searches vector database for relevant past decisions
   - Uses semantic similarity matching
   - Returns top-3 most relevant decisions

2. **ReasoningAgent**
   - Takes question + context
   - Uses Ollama (phi3:mini) for reasoning
   - Generates explanation for decisions

3. **AnswerAgent**
   - Formats reasoning output
   - Attaches source metadata
   - Builds final response

4. **VectorStore**
   - Persistent ChromaDB storage
   - Sentence Transformer embeddings
   - Semantically searchable decision database

## ⚙️ Configuration

Edit `backend/.env` to customize:

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

## 📊 Testing

### Manual Testing with curl

```bash
# Store a decision
curl -X POST "http://localhost:8000/store-decision" \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "Use FastAPI",
    "reason": "Lightweight and fast modern framework",
    "source": "tech-stack-2024"
  }'

# Ask a question
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "Why FastAPI?"}'

# Check health
curl "http://localhost:8000/health"
```

### Interactive Swagger UI

1. Start the server: `uvicorn main:app --reload`
2. Open: `http://localhost:8000/docs`
3. Try out endpoints directly in the browser

## 🔧 Troubleshooting

### Error: "Connection refused" when calling Ollama
**Solution:** Ensure Ollama is running:
```bash
ollama serve
```

### Error: "No decision found" 
**Solution:** Store some decisions first using `/store-decision` endpoint.

### Data loss after restart
**Solution:** Ensure `./chroma_data` directory exists and isn't deleted. ChomraDB persists to disk.

### Slow responses
**Solution:** First request is slowest (model loading). Subsequent requests are faster. Check `OLLAMA_MAX_TOKENS` in `.env` - reduce if too high.

## 📝 Development Notes

- See [CODE_REVIEW.md](../CODE_REVIEW.md) for architecture analysis and improvements
- See [IMPLEMENTATION_ROADMAP.md](../IMPLEMENTATION_ROADMAP.md) for detailed implementation guide
- See [QUICK_FIXES.md](../QUICK_FIXES.md) for code patches and fixes

## 🚨 Known Limitations

- Single-threaded Ollama inference (one query at a time)
- Limited context window (~2048 tokens for phi3:mini)
- No real-time streaming responses
- Vector search limited to semantic similarity (no keyword search)
- No user authentication or authorization

## 🎯 Future Enhancements

- [ ] Async/parallel agent execution
- [ ] Redis caching for frequent queries
- [ ] Query history and analytics
- [ ] Batch decision import/export
- [ ] User feedback loop for model improvement
- [ ] Multiple LLM backends (GPT-4, Claude, etc.)
- [ ] Advanced retrieval with BM25 + semantic hybrid search
- [ ] Confidence scoring on answers
- [ ] Decision reasoning chains (step-by-step reasoning)
- [ ] Web UI dashboard

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [Sentence Transformers](https://www.sbert.net/)

## 📄 License

Sunhacks 2024 Hackathon Project

## 👥 Team

Built for Sunhacks 2024 Hackathon

---

**Last Updated:** April 10, 2026