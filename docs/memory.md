# ChatGBR Chat Memory Architecture

## 1. Objective

Design a multi-user chat memory architecture for ChatGBR that provides low-latency conversation context during active chatting while retaining complete historical conversation data for persistence, analytics, and session resumption.

## 2. Architecture

ChatGBR will use a two-layer memory architecture:

| Layer | Technology | Responsibility |
|---|---|---|
| Active memory | Redis | Recent messages for low-latency reads/writes during live chat |
| Persistent memory | PostgreSQL | Full conversation and message history linked to the user and repository |

Conceptually:

```text
User
  ↓
ChatGBR API
  ├── Redis → active context
  └── PostgreSQL → persistent history
```

## 3. Why Redis + PostgreSQL?

### Redis: Active Context

- Provides very fast reads and writes for messages actively participating in the current conversation.
- Stores only the recent context required for live LLM calls, such as the latest 20 messages.
- Avoids repeatedly querying PostgreSQL for short-lived conversational context.
- Redis is treated as a cache of active context, not the permanent source of truth.

### PostgreSQL: Persistent History

- Stores the complete conversation history.
- Associates conversations with the authenticated ChatGBR user and repository.
- Allows conversations to survive backend restarts and Redis eviction.
- Supports analytics, auditing, conversation listing, and session resumption.

## 4. Database Model

### Conversations

| Column | Type | Purpose |
|---|---|---|
| `id` | UUID | Unique conversation identifier |
| `user_id` | UUID | Owner of the conversation |
| `repository_id` | UUID | Repository associated with the conversation |
| `created_at` | TIMESTAMPTZ | Conversation creation time |
| `updated_at` | TIMESTAMPTZ | Last conversation update time |

### Messages

| Column | Type | Purpose |
|---|---|---|
| `id` | UUID | Unique message identifier |
| `conversation_id` | UUID | Conversation containing the message |
| `user_id` | UUID | User associated with the message |
| `role` | VARCHAR | Message role, such as `user` or `assistant` |
| `content` | TEXT | Message content |
| `created_at` | TIMESTAMPTZ | Message creation time |

Relationship:

```text
Conversation
    ↓
Messages
    ├── user
    ├── assistant
    ├── user
    └── assistant
```

## 5. Redis Model

Redis will store active context using the conversation identifier:

```text
chat:conversation:{conversation_id}
```

Example value:

```json
[
  {
    "role": "user",
    "content": "Where is authentication handled?"
  },
  {
    "role": "assistant",
    "content": "Authentication is handled in..."
  }
]
```

The active history should be bounded, for example to the latest 20 messages, so the Redis cache does not grow indefinitely.

## 6. Request Lifecycle

When a user sends a chat message:

```text
1. Authenticate request
       ↓
2. Get user_id from JWT
       ↓
3. Validate repository ownership
       ↓
4. Resolve conversation_id
       ↓
5. Load recent context from Redis
       ↓
6. Retrieve relevant repository chunks
       ↓
7. Build RAG prompt
       ↓
8. Generate LLM response
       ↓
9. Update Redis active context
       ↓
10. Persist messages in PostgreSQL
       ↓
11. Return answer + conversation_id
```

### Detailed Flow

1. Authenticate the request using the ChatGBR JWT.
2. Obtain `user_id` from the authenticated user.
3. Validate that the requested repository belongs to that user.
4. Resolve the conversation. If no `conversation_id` is supplied, create a new conversation.
5. Load recent conversation context from Redis.
6. Run RAG retrieval against the repository using the user's question.
7. Build the LLM prompt using:
   - conversation history
   - retrieved repository context
   - current question
8. Generate the assistant response.
9. Append the user and assistant messages to Redis.
10. Persist both messages in PostgreSQL.
11. Return the assistant response and `conversation_id`.

## 7. Example

User asks:

> Where is the JWT generated?

Flow:

```text
JWT authentication
       ↓
identify user_id
       ↓
resolve conversation_id
       ↓
Redis → recent messages
       ↓
RAG retrieval → authentication-related code
       ↓
Prompt:
  conversation history
  +
  retrieved code
  +
  question
       ↓
LLM
       ↓
assistant answer
       ↓
Redis → update active context
       ↓
PostgreSQL → persist messages
```

## 8. Source of Truth

PostgreSQL is the source of truth for conversation history.

Redis is the active-context cache optimized for live chat.

If Redis data is lost or evicted, active context can be reconstructed from PostgreSQL.

```text
PostgreSQL
    ↓
Permanent history

Redis
    ↓
Fast active context
```

## 9. Future Extensions

Potential future additions:

- Multiple conversations per repository.
- Conversation titles and renaming.
- Conversation history pagination.
- Conversation deletion and retention policies.
- Redis TTL for inactive conversations.
- Streaming LLM responses.
- Message metadata.
- Retrieved chunk IDs.
- Model and token usage tracking.
- LLM latency tracking.
- RAG evaluation metrics.
- Conversation analytics.


## Core Design Principle

> **Redis accelerates active conversations; PostgreSQL preserves them.**
