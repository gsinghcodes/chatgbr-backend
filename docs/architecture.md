# Architecture Decisions

## Goal

The application indexes a GitHub repository **once**, stores its processed code and embeddings, and reuses them for future searches.

The indexing pipeline is:

```text
GitHub Repository
        │
        ▼
Clone Repository
        │
        ▼
Preprocess Files
        │
        ▼
Chunk Code
        │
        ▼
Generate Embeddings
        │
        ▼
Store Chunks + Embeddings
```

Later, when a user asks a question:

```text
User Question
       │
       ▼
Generate Query Embedding
       │
       ▼
Vector Similarity Search
       │
       ▼
Relevant Chunks
       │
       ▼
LLM Response
```

Only the **query embedding** is generated per request. Repository embeddings are generated once during indexing.

---

# Why PostgreSQL + pgvector?

Choosing PostgreSQL with pgvector because:

- Stores embeddings permanently.
- Avoids regenerating embeddings for every query.
- Supports fast vector similarity search.
- Keeps business data and indexed data together.
- No additional vector database infrastructure is required.

---

# Why SQLAlchemy Repositories?

Repositories manage our application's business entities:

- User
- Repository
- CodeChunk
- Embedding
- Plan
- UserUsage

This keeps all database operations centralized and independent of the service layer.

---

# Why LangChain?

I am **only** using LangChain for interacting with AI models.

Current usage:

- GoogleGenerativeAIEmbeddings
- ChatGoogleGenerativeAI (later)

**Not** using LangChain as our persistence layer.

---

# Why not LangChain PGVector?

I decided **not** to use LangChain's PGVector VectorStore because:

- Already have a well-designed relational schema.
- want full ownership of our data model.
- Repository status, indexing metadata, quotas, and relationships are business concepts that belong in our database.
- Our services should control the indexing workflow.

LangChain helps generate embeddings, while SQLAlchemy manages storage and retrieval.

---

# Responsibilities

## Services

Contain business logic and orchestration.

Examples:

- GitService
- ChunkingService
- EmbeddingService
- RepositoryIndexingService
- SearchService
- LLMService

---

## Repositories

Contain database operations only.

Examples:

- UserRepository
- RepositoryRepository
- CodeChunkRepository
- EmbeddingRepository
- PlanRepository
- UserUsageRepository

Repositories never call AI models.

---

# Overall Architecture

```text
GitHub URL
      │
      ▼
RepositoryIndexingService
      │
      ├── GitService
      ├── ChunkingService
      ├── EmbeddingService (LangChain)
      ├── CodeChunkRepository
      └── EmbeddingRepository
              │
              ▼
      PostgreSQL + pgvector


User Question
      │
      ▼
SearchService
      │
      ├── EmbeddingService
      ├── EmbeddingRepository
      └── LLMService
              │
              ▼
         Final Response
```

---

# Design Principles

- Generate repository embeddings only once.
- Generate query embeddings on every search.
- Keep AI logic inside services.
- Keep database logic inside repositories.
- Maintain complete ownership of the database schema.
- Keep business logic independent of LangChain.
- Use LangChain only as an interface to AI models.