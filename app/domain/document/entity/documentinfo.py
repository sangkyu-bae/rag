from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from app.domain.document.entity.doc import Doc


@dataclass
class DocumentInfo:
    content:str
    metadata:dict[str, Any]
    documents:list[Doc]

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