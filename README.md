# Python Documentation RAG Telegram Bot

A scalable, asynchronous Retrieval-Augmented Generation system that answers Python programming questions via Telegram, powered by local LLM and vector search.

## 📁 Project Structure

```
async-rag-system/
├── bot.py                      # Telegram bot (Aiogram)
├── gateway.py                  # FastAPI task gateway
├── worker.py                   # Async task worker
├── rag/
│   ├── __init__.py
│   ├── rag.py                  # RAG engine core
│   ├── vector_db.py            # ChromaDB operations
│   └── python_document_parser.py  # Doc scraper
├── data/
│   ├── docs/
│   │   └── python_docs.json    # Scraped documentation
│   └── chroma_db/              # Vector database
├── Dockerfile                  # Container definition
├── compose.yaml                # Docker Compose setup
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```
## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Ollama running locally (port 11434)
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))


### Running Without Docker

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Gateway
uvicorn gateway:app --host 0.0.0.0 --port 8000

# Terminal 3: Worker(s)
python worker.py worker-1

# Terminal 4: Bot
python bot.py
```
### Set up

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd async-rag-system
   ```

2. **Install Ollama and pull the model**
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama pull llama3.2
   ollama serve
   ```

3. **Set up environment variables**
   ```bash
   export BOT_TOKEN="your_telegram_bot_token"
   export REDIS_URL="redis://redis:6379"
   export GATEWAY_URL="http://gateway:8000"
   export CHROMA_PATH="data/chroma_db"
   ```

4. **Scrape and index Python documentation** (one-time setup)
   ```bash
   python -m rag.python_document_parser
   python -m rag.vector_db
   ```

5. **Start services with Docker Compose**
   ```bash
   docker-compose up --build
   ```


## 🏗️ Architecture Overview

![ach diagram](diagrams/architecture.png)

## 📊 System Flow Diagram

![ach diagram](diagrams/system_flow.png)

## 🔄 Data Flow

![ach diagram](diagrams/data_flow.png)

## 🏛️ System Components

### 1. Bot Service (`bot.py`)

**Technology**: Aiogram (async Telegram bot framework)

**Responsibilities**:
- Handle incoming Telegram messages
- Send tasks to Gateway via HTTP
- Listen to Redis Pub/Sub for results
- Send formatted answers back to users

**Key Features**:
- Non-blocking message handling
- Automatic Markdown parsing with fallback
- Resilient Redis connection with auto-reconnect

### 2. Gateway Service (`gateway.py`)

**Technology**: FastAPI

**Responsibilities**:
- RESTful API for task creation
- Task status tracking
- Health check endpoint

**Endpoints**:
- `POST /tasks` - Create new task
- `GET /tasks/{id}` - Get task status
- `GET /health` - Service health check

### 3. Worker Service (`worker.py`)

**Technology**: Asyncio with Redis Streams

**Responsibilities**:
- Consumer group-based task processing
- RAG query execution
- Result publishing to Pub/Sub

**Scaling**: Multiple workers can run simultaneously using consumer groups

### 4. RAG Engine (`rag/rag.py`)

**Components**:
- **Retriever**: Semantic search using ChromaDB
- **Relevance Checker**: Distance threshold validation
- **Prompt Builder**: Context-aware prompt construction
- **Generator**: Ollama LLM integration

**Workflow**:
1. Query → Retrieve top 5 relevant chunks
2. Check relevance (distance < 0.5)
3. Build system prompt with context
4. Generate answer via Ollama
5. Format with source citations

### 5. Vector Database (`rag/vector_db.py`)

**Technology**: ChromaDB with SentenceTransformer embeddings

**Features**:
- Document chunking (500 words, 50 word overlap)
- Semantic search using `all-MiniLM-L6-v2`
- Metadata tracking (title, URL, chunk index)

### 6. Document Parser (`rag/python_document_parser.py`)

**Technology**: BeautifulSoup4 + Requests

**Coverage**: 300+ pages from official Python 3 docs including:
- Tutorial
- Standard Library
- Language Reference
- HOWTOs and FAQs

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BOT_TOKEN` | *(required)* | Telegram bot token |
| `REDIS_URL` | `redis://redis:6379` | Redis connection URL |
| `GATEWAY_URL` | `http://gateway:8000` | Gateway service URL |
| `CHROMA_PATH` | `data/chroma_db` | Vector DB storage path |

### RAG Parameters

```python
# In rag.py
n_top_results = 5           # Number of chunks to retrieve
relevance_threshold = 0.5   # Distance threshold for relevance
temperature = 0.1           # LLM temperature (lower = more focused)
max_tokens = 500           # Maximum response length
```

## 🧪 Testing

```bash
# Test RAG system directly
python -m rag.rag

# Test vector retrieval
python -m rag.vector_db

# Test document parsing
python -m rag.python_document_parser
```

## 📝 Example Interactions

**User**: "What is a list comprehension?"

**Bot Response**:

**List Comprehensions**

A list comprehension is a compact way to create lists in Python. It consists of an expression followed by a "for" clause, then zero or more "if" clauses.

According to the Python documentation, [SOURCE 1], a list comprehension is defined as:

"A compact way to create lists. It consists of an expression followed by a 'for' clause, then zero or more 'if' clauses."

The syntax for a list comprehension is:
```python
[expression for variable in iterable if condition]
```
For example:
```python
numbers = [1, 2, 3, 4, 5]
squared_numbers = [x**2 for x in numbers]
print(squared_numbers)  # [1, 4, 9, 16, 25]
```
In this example, the expression `x**2` is evaluated for each element `x` in the `numbers` list, and the resulting values are collected into a new list.

List comprehensions can also include multiple "for" clauses and "if" clauses:
```python
numbers = [1, 2, 3, 4, 5]
even_numbers = [x for x in numbers if x % 2 == 0]
odd_numbers = [x for x in numbers if x % 2 != 0]
print(even_numbers)  # [2, 4]
print(odd_numbers)   # [1, 3, 5]
```
List comprehensions are a concise and expressive way to create lists in Python. They can be used to perform complex data transformations and filtering operations.

**References**

[SOURCE 1]: Python documentation, "List Comprehensions"

Sources:
- https://docs.python.org/3/reference/expressions.html
- https://docs.python.org/3/library/stdtypes.html


## 🛡️ Error Handling

- **Ollama Connection**: Returns error message if Ollama is down
- **Irrelevant Queries**: Detects and rejects non-Python questions
- **Redis Failures**: Auto-reconnection with exponential backoff
- **Telegram Errors**: Markdown parsing fallback to plain text

## 🚧 Limitations

- Only answers questions from indexed Python documentation
- Requires Ollama running on `host.docker.internal:11434`
- English language only
- Maximum context window depends on LLM model

---

**Built with ❤️ using Python, ChromaDB, Ollama, and Aiogram**
