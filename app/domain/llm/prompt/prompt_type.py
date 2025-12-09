from enum import Enum

class PromptType(Enum):
    DOCUMENT_CLASSIFICATION = "document_classification"
    SUMMARIZATION = "summarization"
    CHUNK_STRATEGY = "chunk_strategy"
    METADATA_EXTRACTION = "metadata_extraction"
    # 필요한 만큼 계속 확장
