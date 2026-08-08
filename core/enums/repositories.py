from enum import Enum


class RepositoryStatus(str, Enum):
    PENDING = "PENDING"
    INDEXING = "INDEXING"
    INGESTING = "INGESTING"
    READY = "READY"
    FAILED = "FAILED"
