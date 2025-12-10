from dataclasses import dataclass


@dataclass
class DocumentClassification:
    document_type:str
    confidence:float
    reason:str

