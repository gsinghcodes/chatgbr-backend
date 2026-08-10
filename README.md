# Semantic Git Commit Search

This mini-project adds a LangChain-powered semantic search layer over git history.
It indexes commit hunks into Postgres with `pgvector`, rewrites natural-language
questions into diff-shaped queries, retrieves the best matching hunks, and
returns an answer with commit citations.

## What is included

- `semantic_git_search/ingest.py`: CLI that extracts commit hunks, embeds them,
  and stores them in Postgres.
- `semantic_git_search/storage.py`: schema management plus hybrid
  vector-and-keyword retrieval.
- `semantic_git_search/retrieval.py`: query rewriting and embedding-based lookup.
- `semantic_git_search/service.py`: answer synthesis with commit citations.
- `semantic_git_search/api.py`: FastAPI entrypoint exposing `/query`.

## Environment

Set these variables before running the app:

```powershell
$env:SGCS_POSTGRES_DSN="postgresql://postgres:postgres@localhost:5432/gitsearch"
$env:SGCS_REPOSITORY_NAME="langchain"
$env:OPENAI_API_KEY="your-key"
```

Optional switches:

- `SGCS_EMBEDDING_PROVIDER=openai|local`
- `SGCS_LOCAL_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2`
- `SGCS_QUERY_REWRITE=true|false`
- `SGCS_USE_LLM_ANSWERS=true|false`
- `SGCS_TOP_K=8`

## 1. Index a repository

```powershell
.venv\Scripts\python.exe -m semantic_git_search.ingest `
  --repo-path D:\Gyanendra\AI\Langchain `
  --repo-name langchain `
  --max-commits 500
```

This stores one row per diff hunk, not one row per whole commit, which keeps
matches precise when a single commit touches multiple files.

## 2. Run the API

```powershell
.venv\Scripts\python.exe -m uvicorn semantic_git_search.api:app --reload
```

## 3. Query it

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"Where did we implement semantic retrieval?\"}"
```

Example response shape:

```json
{
  "answer": "Semantic retrieval was added in retrievers/vector_store_retriever.py [abc1234].",
  "rewritten_query": "implement semantic retrieval vector store retriever",
  "sources": [
    {
      "commit_hash": "abc1234...",
      "file_path": "retrievers/vector_store_retriever.py",
      "author": "Example Dev",
      "commit_date": "2026-08-03T13:05:00Z",
      "commit_message": "Add vector retriever example",
      "hunk_header": "@@ -1,3 +1,18 @@",
      "score": 0.031
    }
  ]
}
```

## Minimal frontend contract

If you want the Next.js UI from the original build guide, point it at the
FastAPI service with a simple POST:

```typescript
export async function askGitHistory(question: string) {
  const response = await fetch("http://127.0.0.1:8000/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error("Git history query failed");
  }

  return response.json();
}
```

## Notes

- OpenAI embeddings use 1536 dimensions by default.
- Local embeddings use `sentence-transformers` and default to 384 dimensions.
- If OpenAI is unavailable, query rewriting falls back to the original question
  and answer generation falls back to a citation list.

