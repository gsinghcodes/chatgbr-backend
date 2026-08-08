from enum import Enum


class UserOperation(str, Enum):
    SEARCH = "SEARCH"
    CHAT = "CHAT"
    INDEX_REPOSITORY = "INDEX_REPOSITORY"
    EMBEDDING = "EMBEDDING"


class AIModel(str, Enum):
    GPT_OSS = "openai/gpt-oss-120b"
    GEMINI_EMBEDDING = "gemini-embedding-001"
