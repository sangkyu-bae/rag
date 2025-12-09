from prompt_type import PromptType
from typing import Dict

class PromptRegistry:
    """
    모든 LLM System Prompt / Template을 중앙에서 관리하는 Registry.
    이후 DB나 Feature Store로 교체해도 interface 유지됨.
    """

    _PROMPTS: Dict[PromptType, str] = {}

    @classmethod
    def init(cls):
        """초기 로딩 — POC에서는 코드에 넣고, 운영 단계에서는 DB 로딩 가능"""
        cls._PROMPTS = {
            PromptType.DOCUMENT_CLASSIFICATION: cls._document_classification_prompt(),
            PromptType.SUMMARIZATION: cls._summarization_prompt(),
            PromptType.CHUNK_STRATEGY: cls._chunk_strategy_prompt(),
            PromptType.METADATA_EXTRACTION: cls._metadata_extraction_prompt(),
        }

    @classmethod
    def get(cls, prompt_type: PromptType) -> str:
        """프롬프트 조회"""
        if not cls._PROMPTS:
            cls.init()
        return cls._PROMPTS.get(prompt_type)

    # ============================
    # 개별 프롬프트 템플릿 정의부
    # ============================

    @staticmethod
    def _document_classification_prompt() -> str:
        return """
        You are a document classification expert.
        Your task is to determine whether a document is a FORM (a template requiring user input)
        or a NORMAL document (descriptive, policy, guideline, natural-language based).

        FORM Document characteristics:
        - Contains tables, placeholders like ( ), ○ marks
        - Fields such as 성명, 주소, 생년월일, 년 월 일
        - Instructional language: 기입, 작성, 체크
        - Titled as 서식, 별지, 신청서, 요구서
        - Signature blocks / 직인 / 귀중

        NORMAL Document characteristics:
        - Natural language explanation
        - Policies, rules, guidelines, procedures
        - No fields to fill in
        - No table-driven layout

        Respond strictly in JSON:
        {
          "document_type": "FORM" or "NORMAL",
          "reason": "short explanation"
        }
        """

    @staticmethod
    def _summarization_prompt() -> str:
        return """
        You are a summarization assistant.
        Summarize the following document in a concise and factual way...
        """

    @staticmethod
    def _chunk_strategy_prompt() -> str:
        return """
        You are a chunking strategy generator...
        Based on the document type and structure, propose optimal chunking rules...
        """

    @staticmethod
    def _metadata_extraction_prompt() -> str:
        return """
        Extract metadata fields such as title, date, category, responsible department...
        Return in JSON format.
        """


# 초기화 호출
PromptRegistry.init()