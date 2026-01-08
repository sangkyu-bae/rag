from app.domain.llm.prompt.prompt_type import PromptType
from typing import Dict
import json
from langchain_core.output_parsers import JsonOutputParser

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
    # 1차 문서 분류 템플릿
    # ============================
    @staticmethod
    def _first_document_classification_prompt()-> str:
        return """
            당신은 문서 분석 및 분류 전문가입니다.
            아래 제공되는 3~5개의 문단은 해당 문서 전체 내용의 '샘플'입니다.
            이 샘플을 기반으로 문서의 전체 유형(Document Type)을 판단하세요.
            
            문서 유형 정의는 다음과 같습니다:
            
            1. PROCEDURE (절차/매뉴얼/운영 문서)
            - Step 1, 2, 3 형태의 단계 기반 설명
            - 설치/실행/빌드/등록/적용 같은 동사 중심 절차 설명
            - UI 화면, 버튼, 경로, 메뉴 구조 설명이 포함될 수 있음
            - 예: 개발 배포 매뉴얼, 운영 절차서, 설치 가이드
            
            2. POLICY (정책/내규/규정/안내)
            - 법적/내부 규정 설명, 조건, 조항, 절차 정의
            - 문어체, 조항 구조, 정책적 표현
            - 예: 인사 규정, 대출 지침, 보안 정책
            
            3. MANUAL (기술 매뉴얼/개발 가이드)
            - 개발자용 설명, 코드 예시, 설정 값, 옵션 설명
            - 소스코드/스크립트/명령어 포함
            - 예: API 문서, 개발자 매뉴얼, 설정 가이드
            
            4. REPORT (보고서/분석/결과문서)
            - 분석, 결과, 보고 중심
            - 표, 구조화된 섹션, 설명 중심
            - 정책이나 절차보다 분석/요약 성격
            
            5. UNKNOWN
            - 위 범주에 해당하지 않는 경우
            
            ---
            
            판단 규칙:
            - 샘플 문단만 보고 전체 문서의 성격을 추론하십시오.
            - OCR 잡음, 기사 조각, UI 캡쳐 텍스트 등이 있을 수 있으나,
              문서의 '기능적 목적'에 기반해 문서 유형을 판별하십시오.
            - 반드시 가장 적합한 단 하나의 유형만 선택하세요.
            
            출력은 반드시 아래 JSON 형식으로만 응답하세요:
            
            {
              "document_type": "procedure | policy | manual | report | unknown",
              "confidence": 0 ~ 1 사이 숫자 (판단 확신도),
              "reason": "문서를 그렇게 판단한 간단한 이유"
            }
            
            이해했다면 이제 아래 문단 샘플을 분석하고 문서 타입을 분류하세요.
            
            ----- 문단 샘플 -----
        """
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

    @staticmethod
    def basic_prompt(x:dict[str,any])->dict[str,str]:
        parser = JsonOutputParser()
        """
          x = {
            "question": str,
            "tool_outputs": list[dict]
          }
          """
        payload = {
            "assistant_task": {
                "instruction": {
                    "role": (
                        "당신은 회사 내부 문서, 정형 데이터, SQL 결과, 웹 검색 결과를 종합하여 "
                        "정확하고 근거 기반의 답변을 생성하는 AI Assistant 입니다."
                    ),
                    "rules": [
                        "반드시 제공된 정보(tool_outputs) 안에서만 답변할 것",
                        "문서 조각은 반드시 [출처: 파일명, 페이지] 형태로 표기할 것",
                        "tool_outputs 외의 새로운 사실은 생성하지 말 것",
                        "여러 근거가 있을 경우 중요도 순서대로 정리",
                        "정보가 부족하면 \"해당 문서에는 정보가 없음\"으로 답변"
                    ],
                },
                "user_query": x["question"],
                "tool_outputs": x["tool_outputs"],
                "output_format": {
                    "type": "json",
                    "schema": {
                        "answer": [
                            {
                                "text": "string",
                                "source": {
                                    "file_name": "string",
                                    "page": "number"
                                }
                            }
                        ]
                    }
                }
            }
        }

        return {
            "payload_json": json.dumps(payload, ensure_ascii=False),
            "format_instructions": parser.get_format_instructions()
        }

    @staticmethod
    def question_router_prompt() ->  dict[str, str]:
        return {
            "system" :"""
                당신은 "Tool Router" 역할을 하는 AI입니다.
                
                당신의 임무는 사용자의 질문을 분석하여
                답변에 필요한 도구들을 선택하는 것입니다.
                
                반드시 아래 JSON 형식으로만 출력해야 하며,
                JSON 이외의 텍스트는 절대 출력하지 마세요.
                
                출력 형식:
                {{
                  "tools": ["VECTOR_DB", "EXCEL_DB", "WEB_SEARCH", "NONE"],
                  "reason": "선택한 이유를 한 문장으로 설명"
                }}
                
                규칙:
                - tools 필드는 반드시 배열이어야 합니다.
                - tool 이름은 반드시 대문자로 정확히 일치해야 합니다.
            """,
            "human":"""
                [사용 가능한 도구 목록 및 선택 기준]
                
                1) VECTOR_DB
                - 회사 내부 문서에서 찾을 수 있는 정보
                - 규정, 정책, 내부 서비스, 내부 앱, 지침서
                - 특정 서비스명, 프로젝트명, 약어, 로컬 규정 등
                - 내부에서만 존재하는 내용
                
                2) EXCEL_DB
                - 정형 데이터 기반 질문
                - 숫자, 표, 재무제표, 통계, 지표, 수치 기반 분석
                - 예: “2023년 자산총계”
                
                3) WEB_SEARCH
                - 외부 시사, 시장, 일반 지식
                - 최신 정책, 최신 금리, 플랫폼 가이드, 일반 기술지식
                - 회사 내부 문서에 없을 가능성이 높은 정보
                
                4) NONE
                - 내부 도구나 외부 검색 없이
                - LLM 자체로 답변 가능한 단순 질문
                
                ---
                
                [내부 전용 용어 규칙 – 매우 중요]
                
                아래 단어(또는 유사 표현)가 포함된 경우
                반드시 VECTOR_DB를 포함해야 합니다.
                
                ["크크크앱", "크크크 앱", "DX포털", "DX 포털", "우리회사앱", "내부서비스", "사내전용", "DX"]
                
                - 내부 용어가 포함되었더라도
                  외부 기술/정책이 함께 요구되면
                  VECTOR_DB + WEB_SEARCH 조합을 선택하세요.
                
                예:
                “크크크앱 배포법과 안드로이드 사전지식”
                → ["VECTOR_DB", "WEB_SEARCH"]
                
                ---
                
                [복수 도구 선택 규칙]
                
                다음 상황에서는 여러 도구를 동시에 선택할 수 있습니다:
                
                - 내부 정보 + 외부 지식
                - 내부 문서 기반 절차 + 외부 정책
                - 정형 데이터 + 내부 규정
                - 단순 검색 + 문서 기반 상세 정보
                
                ---
                
                [도구 선택 금지 규칙]
                
                1) 내부 전용 용어가 포함된 경우
                   → WEB_SEARCH만 단독 선택 금지
                
                2) JSON 이외의 출력 금지
                3) 불필요한 설명 금지
                
                ---
                
                [Few-shot 예시]
                
                Q: 직원 근태 규정에서 지각 기준이 어떻게 돼?
                A:
                {{
                  "tools": ["VECTOR_DB"],
                  "reason": "내부 규정 문서에 존재하는 정보"
                }}
                
                Q: 2023년 자산총계가 얼마야?
                A:
                {{
                  "tools": ["EXCEL_DB"],
                  "reason": "정형 재무 데이터 기반 질문"
                }}
                
                Q: 요즘 기준금리 왜 올라?
                A:
                {{
                  "tools": ["WEB_SEARCH"],
                  "reason": "외부 시장 정보 기반 질문"
                }}
                
                Q: 크크크앱 안드로이드 배포 방법 알려줘
                A:
                {{
                  "tools": ["VECTOR_DB"],
                  "reason": "내부 서비스 용어가 포함된 질문"
                }}
                
                Q: 크크크앱 배포법과 안드로이드 사전지식도 알려줘
                A:
                {{
                  "tools": ["VECTOR_DB", "WEB_SEARCH"],
                  "reason": "내부 문서와 외부 플랫폼 지식이 모두 필요"
                }}
                아래질문을 보고 답변하세요
                =========================================
                {question}
            """
        }
        # return """
        #        당신은 "Tool Router" 역할을 하는 AI입니다. s
        #          사용자의 질문을 분석하여 어떤 도구들을 사용해야 답변할 수 있는지 결정합니다.
        #
        #          이때 하나 이상의 도구가 필요할 수 있으며, s
        #          반드시 아래 JSON 형식을 엄격히 준수해야 합니다.
        #
        #          출력 형식 (절대 벗어나지 마세요):
        #
        #          {
        #            "tools": ["VECTOR_DB", "EXCEL_DB", "WEB_SEARCH", ...],
        #            "reason": "선택한 이유를 한 문장으로 설명"
        #          }
        #
        #          ---
        #
        #          [사용 가능한 도구 목록 및 선택 기준]
        #
        #          1) VECTOR_DB s
        #          - 회사 내부 문서에서 찾을 수 있는 정보 s
        #          - 규정/정책/내부 서비스/내부 앱/지침서 s
        #          - 특정 서비스명, 프로젝트명, 약어, 로컬 규정 등 s
        #          - 내부에서만 존재하는 내용
        #
        #          2) EXCEL_DB s
        #          - 정형 데이터 기반 질문 s
        #          - 숫자, 표, 재무제표, 통계, 지표, 수치 기반 분석이 필요한 경우 s
        #          - “2023년 자산총계” 등
        #
        #          3) WEB_SEARCH s
        #          - 외부 시사/시장/일반 지식/OS 정책/Google 정책 s
        #          - 최신 정책, 최신 금리, 플랫폼 가이드, 일반 기술지식 s
        #          - 회사 내부 문서에 없을 법한 지식
        #
        #          4) NONE s
        #          - 내부 도구나 외부 검색 없이 LLM 자체로 답변 가능한 단순 질문
        #
        #          ---
        #
        #          [내부 전용 용어 규칙 – 매우 중요]
        #
        #          아래 단어(또는 이와 유사한 표현)가 포함되어 있다면 s
        #          해당 질문은 회사 내부 문서(VECTOR_DB)를 반드시 포함해야 합니다.
        #
        #          ["크크크앱", "크크크 앱", "DX포털", "DX 포털", "우리회사앱", "내부서비스", "사내전용", "DX"]
        #
        #          ※ 내부 용어가 포함되어 있어도, 질문이 외부 기술/정책까지 요구하면 s
        #          VECTOR_DB + WEB_SEARCH 조합처럼 복합 도구를 선택하세요.
        #
        #          예: “크크크앱 배포법과, 그 과정에 필요한 안드로이드 사전지식도 알려줘” s
        #          → VECTOR_DB + WEB_SEARCH
        #
        #          ---
        #
        #          [복수 도구 선택 규칙]
        #
        #          다음과 같은 상황에서는 여러 도구를 동시에 선택해야 합니다:
        #
        #          - 질문이 내부 정보 + 외부 지식을 요구함 s
        #          - 내부 문서 기반 절차 + 외부 정책 필요 s
        #          - 정형 데이터 + 내부 규정 동시 필요 s
        #          - 단순 검색 + 문서 기반 상세 정보 조합
        #
        #          복수 선택 예:
        #          ["VECTOR_DB", "WEB_SEARCH"]
        #          ["VECTOR_DB", "EXCEL_DB"]
        #          ["EXCEL_DB", "WEB_SEARCH"]
        #
        #          ---
        #
        #          [도구 선택 금지 규칙]
        #
        #          1) 내부 전용 용어가 질문에 포함되어 있을 경우 s
        #          → WEB_SEARCH만 선택하는 것은 금지 (항상 VECTOR_DB 포함)
        #
        #          2) JSON 이외의 출력 금지 s
        #          3) 불필요한 설명, 텍스트 출력 금지 s
        #          4) tool 필드는 반드시 배열 형태여야 함 s
        #          5) tool 이름은 반드시 대문자로 정확히 일치
        #
        #          ---
        #
        #          [Few-Shot 예시]
        #
        #          Q: "직원 근태 규정에서 지각 기준이 어떻게 돼?"
        #          A:
        #          {
        #            "tools": ["VECTOR_DB"],
        #            "reason": "내부 규정 문서에 존재하는 정보"
        #          }
        #
        #          Q: "2023년 자산총계가 얼마야?"
        #          A:
        #          {
        #            "tools": ["EXCEL_DB"],
        #            "reason": "정형 재무 데이터 기반 질문"
        #          }
        #
        #          Q: "요즘 기준금리 왜 올라?"
        #          A:
        #          {
        #            "tools": ["WEB_SEARCH"],
        #            "reason": "시장/시사 정보 기반"
        #          }
        #
        #          Q: "크크크앱 안드로이드 배포 방법 알려줘"
        #          A:
        #          {
        #            "tools": ["VECTOR_DB"],
        #            "reason": "내부 서비스 용어 포함"
        #          }
        #
        #          Q: "크크크앱 배포법과 그 과정에 필요한 안드로이드 사전지식도 알려줘"
        #          A:
        #          {
        #            "tools": ["VECTOR_DB", "WEB_SEARCH"],
        #            "reason": "내부 문서 + 외부 플랫폼 정책 둘 다 필요"
        #          }
        #
        #          ---
        #
        #          이제 아래 질문을 분석하고 s
        #          필요한 도구들을 JSON 형식으로만 출력하세요.
        # """


# 초기화 호출
PromptRegistry.init()