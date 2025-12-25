from __future__ import annotations
from dataclasses import dataclass
from importlib.metadata import metadata
from typing import Any

from pymupdf.extra import make_table_dict

from app.domain.document.entity.doc import Doc
from app.domain.document.entity.document_type import DocumentType
from app.domain.llm.prompt.prompt_registry import PromptRegistry
from langchain_core.documents import Document

@dataclass
class DocumentInfo:
    content:str
    metadata:dict[str, Any]
    documents:list[Doc]
    child_documents:list[Doc]

    @classmethod
    def from_doc_info(cls, content:str, metadata:dict[str,Any],documents:list[Doc]) -> DocumentInfo:
        return cls(content=content,metadata=metadata,documents=documents)

    def get_route_doc(self) -> str:
        """
        문단 단위 Doc 리스트(self.documents)를 기반으로 라우팅에 사용할 샘플 문단을 추출한다.

        규칙:
          - 문단 수 < 4 → 전체 문단 사용
          - 4 <= 문단 수 < 8 → 앞 3 문단 + 마지막 1 문단
          - 문단 수 >= 8 → 앞 3 문단 + 중간 1 문단
        """

        paragraphs: list[Doc] = self.documents
        total = len(paragraphs)

        # 1. 문단 수가 적으면 전체 사용
        if total < 4:
            return "\n\n".join(p.content for p in paragraphs)

        # 2. 문단 수가 4~7개면: 앞 3 + 끝 1
        if total < 8:
            selected = paragraphs[:3] + [paragraphs[-1]]
            return "\n\n".join(p.content for p in selected)

        # 3. 문단이 8개 이상이면: 앞 3 + 중간 1
        mid_index = total // 2
        selected = paragraphs[:3] + [paragraphs[mid_index]]
        return "\n\n".join(p.content for p in selected)

    def get_first_route_llm(self) -> str:
        # 1) 분류 프롬프트 body
        prompt_body: str = PromptRegistry._first_document_classification_prompt()

        # 2) 문서에서 추출된 샘플 문단
        sample_text: str = self.get_route_doc()

        # 3) 두 개 합쳐서 최종 프롬프트 생성
        final_prompt = f"{prompt_body}\n\n{sample_text}"

        return final_prompt


    def get_upsert_document(self)-> list[Document]:
         docs:list[Document] = [
             Document(
                 page_content = doc.content,
                 matadata = doc.metadata
             )
             for doc in self.document
         ]

         # docs.append(Document(
         #     page_content=self.content,
         #     metadata=self.metadata
         # ))

         return docs

    def set_child_document(self,child_doc:list[Document]) :
        self.child_documents = child_doc

