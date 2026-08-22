from enum import Enum


class RepositoryStatus(str, Enum):
    PENDING = "PENDING"
    CLONING = "CLONING"
    CHUNKING = "CHUNKING"
    EMBEDDING = "EMBEDDING"
    READY = "READY"
    FAILED = "FAILED"
