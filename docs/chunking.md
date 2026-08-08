# Chunking Strategy

## MVP

The first version of the application will use LangChain's language-aware code splitters.

Reasons:

- Faster to implement.
- Supports multiple programming languages.
- Well-tested.
- Produces high-quality chunks suitable for semantic search.
- Lets us focus on completing the end-to-end indexing and search pipeline.

The MVP goal is:

```text
GitHub Repository
→ Clone
→ Chunk
→ Generate Embeddings
→ Store
→ Search
→ Answer
```

---

## Future Improvement

If benchmarking shows that chunk quality is limiting retrieval performance, I will replace the internal chunking implementation with Tree-sitter.

The public interface of `ChunkingService` will remain unchanged.

```text
Current:

ChunkingService
    ↓
LangChain Code Splitters

Future:

ChunkingService
    ↓
Tree-sitter AST Parser
```

Since the rest of the application only depends on `ChunkingService`, no other service will need to change.

---

## Design Principle

All services should depend on the `ChunkingService` interface, never on a specific chunking implementation.

This allows us to improve the internal implementation without affecting:

- RepositoryIndexingService
- EmbeddingService
- SearchService