from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from llama_index.core.schema import Document


from app.service.chunk.parser.text_parseprocessor import TextParseProcessor


@dataclass
class Doc:
    content:str
    metadata:dict[str, Any]


    @classmethod
    def from_document(cls,document:Document)->Doc:
        text_parser = TextParseProcessor()
        # parse_content = text_parser.preprocess_text(document.text)
        # parse_content = text_parser.preprocess_text(document.text)
        return cls(content=document.text,metadata=document.metadata)