from enum import Enum
class DocumentType(str,Enum):
    PROCEDURE = "procedure",
    POLICY = "policy",
    MANUAL = "manual",
    REPORT = "report",
    UNKNOWN = "unknown"