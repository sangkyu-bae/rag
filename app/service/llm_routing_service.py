"""LLM을 사용한 문서 카테고리 라우팅 서비스."""

import logging
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from enum import Enum

from openai import AsyncOpenAI
from app.core.config import settings
from app.domain.document.services.llm_parse_service import LlamaParseService, get_llama_parse_service

logger = logging.getLogger(__name__)


class DocumentCategory(str, Enum):
    """문서 카테고리 열거형."""
    LOAN_FINANCE = "loan_finance"
    IT_SYSTEM = "it_system"
    SECURITY_ACCESS = "security_access"
    HR = "hr"
    ACCOUNTING_LEGAL = "accounting_legal"
    GENERAL = "general"


class LLMRoutingService:
    """LLM을 사용하여 PDF 문서를 카테고리별로 라우팅하는 서비스."""

    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        llama_parse_service: Optional[LlamaParseService] = None,
    ):
        """
        LLM 라우팅 서비스 초기화.

        Args:
            openai_api_key: OpenAI API 키. None인 경우 설정에서 가져옴.
            model: 사용할 LLM 모델명 (기본값: gpt-4o-mini)
            llama_parse_service: LlamaParse 서비스 인스턴스. None인 경우 새로 생성.
        """
        self.api_key = openai_api_key or getattr(settings, "OPENAI_API_KEY", None)
        if not self.api_key:
            raise ValueError(
                "OpenAI API 키가 설정되지 않았습니다. OPENAI_API_KEY 환경 변수를 설정해주세요."
            )
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
        self.llama_parse_service = llama_parse_service or get_llama_parse_service()

        # 카테고리 설명
        self.category_descriptions = {
            DocumentCategory.LOAN_FINANCE: "대출, 금융, 투자, 보험, 예금, 신용카드 등 금융 관련 문서",
            DocumentCategory.IT_SYSTEM: "IT 시스템, 소프트웨어, 하드웨어, 네트워크, 데이터베이스, 개발 등 IT 관련 문서",
            DocumentCategory.SECURITY_ACCESS: "보안, 접근 권한, 인증, 암호화, 개인정보보호 등 보안 관련 문서",
            DocumentCategory.HR: "인사, 채용, 평가, 급여, 복리후생, 조직 등 인사 관련 문서",
            DocumentCategory.ACCOUNTING_LEGAL: "회계, 법무, 세무, 계약, 규정, 정책 등 회계/법무 관련 문서",
            DocumentCategory.GENERAL: "위 카테고리에 해당하지 않는 일반 문서",
        }

    def _get_routing_prompt(self, document_content: str) -> str:
        """
        문서 내용을 기반으로 라우팅 프롬프트를 생성합니다.

        Args:
            document_content: 파싱된 문서 내용

        Returns:
            LLM에 전달할 프롬프트
        """
        categories_text = "\n".join([
            f"- {cat.value}: {desc}"
            for cat, desc in self.category_descriptions.items()
        ])

        prompt = f"""다음 문서의 내용을 분석하여 가장 적합한 카테고리를 선택해주세요.

사용 가능한 카테고리:
{categories_text}

문서 내용:
{document_content[:4000]}  # 최대 4000자로 제한

위 문서를 분석하여 다음 형식으로 응답해주세요:
카테고리: [카테고리명]
이유: [선택한 이유를 간단히 설명]

응답은 반드시 다음 중 하나의 카테고리명만 사용해야 합니다:
- loan_finance
- it_system
- security_access
- hr
- accounting_legal
- general
"""
        return prompt

    async def route_document(
        self,
        file_path: str,
        max_content_length: int = 4000,
    ) -> Dict[str, Any]:
        """
        PDF 파일을 읽어서 적절한 카테고리로 라우팅합니다.

        Args:
            file_path: 라우팅할 PDF 파일 경로
            max_content_length: LLM에 전달할 최대 문서 길이 (문자 수)

        Returns:
            카테고리 정보와 메타데이터를 포함한 딕셔너리
            {
                "category": "loan_finance",
                "confidence": "high",
                "reason": "선택한 이유",
                "metadata": {...}
            }

        Raises:
            FileNotFoundError: 파일이 존재하지 않는 경우
            ValueError: API 키가 유효하지 않은 경우
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        try:
            logger.info(f"문서 라우팅 시작: {file_path}")

            # 1. PDF 파일 파싱
            parse_result = await self.llama_parse_service.parse_file_async(
                file_path=file_path,
                result_type="markdown",
            )
            document_content = parse_result["content"]

            # 2. 내용 길이 제한
            if len(document_content) > max_content_length:
                document_content = document_content[:max_content_length]
                logger.warning(
                    f"문서 내용이 {max_content_length}자를 초과하여 잘렸습니다."
                )

            # 3. LLM을 통한 카테고리 분류
            prompt = self._get_routing_prompt(document_content)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 문서를 카테고리별로 분류하는 전문가입니다. 문서의 주요 내용을 분석하여 가장 적합한 카테고리를 정확하게 선택해주세요.",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.3,  # 일관성을 위해 낮은 temperature 사용
                max_tokens=200,
            )

            # 4. 응답 파싱
            llm_response = response.choices[0].message.content.strip()
            category, reason = self._parse_llm_response(llm_response)

            # 5. 카테고리 검증
            try:
                validated_category = DocumentCategory(category)
            except ValueError:
                logger.warning(
                    f"LLM이 유효하지 않은 카테고리를 반환했습니다: {category}. "
                    f"기본값 'general'을 사용합니다."
                )
                validated_category = DocumentCategory.GENERAL
                reason = f"유효하지 않은 카테고리 응답으로 인해 기본값 사용: {llm_response}"

            logger.info(
                f"문서 라우팅 완료: {file_path} -> {validated_category.value}"
            )

            return {
                "category": validated_category.value,
                "confidence": self._calculate_confidence(llm_response),
                "reason": reason,
                "metadata": {
                    **parse_result["metadata"],
                    "model": self.model,
                    "llm_response": llm_response,
                },
            }

        except Exception as e:
            logger.error(f"문서 라우팅 중 오류 발생: {file_path}, 오류: {str(e)}")
            raise

    def _parse_llm_response(self, response: str) -> Tuple[str, str]:
        """
        LLM 응답을 파싱하여 카테고리와 이유를 추출합니다.

        Args:
            response: LLM 응답 텍스트

        Returns:
            (카테고리명, 이유) 튜플
        """
        category = None
        reason = ""

        # 응답에서 카테고리 추출
        lines = response.split("\n")
        for line in lines:
            line_lower = line.lower().strip()
            # "카테고리:" 또는 "category:" 패턴 찾기
            if "카테고리:" in line or "category:" in line_lower:
                # 콜론 뒤의 값 추출
                parts = line.split(":", 1)
                if len(parts) > 1:
                    category = parts[1].strip().lower()
                    # 카테고리명에서 공백 제거 및 언더스코어 확인
                    category = category.replace(" ", "_")
            # "이유:" 또는 "reason:" 패턴 찾기
            elif "이유:" in line or "reason:" in line_lower:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    reason = parts[1].strip()

        # 카테고리를 찾지 못한 경우, 응답에서 직접 찾기
        if not category:
            response_lower = response.lower()
            for cat in DocumentCategory:
                if cat.value in response_lower:
                    category = cat.value
                    break

        # 여전히 찾지 못한 경우, 응답의 첫 줄이나 키워드로 추정
        if not category:
            # 일반적인 키워드 기반 추정
            response_lower = response.lower()
            if any(kw in response_lower for kw in ["loan", "finance", "대출", "금융"]):
                category = DocumentCategory.LOAN_FINANCE.value
            elif any(kw in response_lower for kw in ["it", "system", "소프트웨어", "시스템"]):
                category = DocumentCategory.IT_SYSTEM.value
            elif any(kw in response_lower for kw in ["security", "access", "보안", "접근"]):
                category = DocumentCategory.SECURITY_ACCESS.value
            elif any(kw in response_lower for kw in ["hr", "human", "인사", "채용"]):
                category = DocumentCategory.HR.value
            elif any(kw in response_lower for kw in ["accounting", "legal", "회계", "법무"]):
                category = DocumentCategory.ACCOUNTING_LEGAL.value
            else:
                category = DocumentCategory.GENERAL.value

        if not reason:
            reason = "LLM 응답에서 이유를 추출하지 못했습니다."

        return category, reason

    def _calculate_confidence(self, llm_response: str) -> str:
        """
        LLM 응답을 기반으로 신뢰도를 계산합니다.

        Args:
            llm_response: LLM 응답 텍스트

        Returns:
            "high", "medium", "low" 중 하나
        """
        response_lower = llm_response.lower()
        
        # 명확한 카테고리명이 포함되어 있고, 이유가 상세한 경우
        has_category = any(cat.value in response_lower for cat in DocumentCategory)
        has_reason = len(llm_response) > 50 and ("이유" in llm_response or "reason" in response_lower)
        
        if has_category and has_reason:
            return "high"
        elif has_category:
            return "medium"
        else:
            return "low"

    async def route_document_from_bytes(
        self,
        file_bytes: bytes,
        file_name: str,
        max_content_length: int = 4000,
    ) -> Dict[str, Any]:
        """
        바이트 데이터로부터 PDF 파일을 읽어서 적절한 카테고리로 라우팅합니다.

        Args:
            file_bytes: PDF 파일의 바이트 데이터
            file_name: 파일 이름 (확장자 포함)
            max_content_length: LLM에 전달할 최대 문서 길이 (문자 수)

        Returns:
            카테고리 정보와 메타데이터를 포함한 딕셔너리
        """
        # 임시 파일로 저장 후 라우팅
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_name).suffix) as tmp_file:
            try:
                tmp_file.write(file_bytes)
                tmp_file_path = tmp_file.name
                
                result = await self.route_document(
                    file_path=tmp_file_path,
                    max_content_length=max_content_length,
                )
                
                return result
            finally:
                # 임시 파일 삭제
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)


def get_llm_routing_service(
    openai_api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
) -> LLMRoutingService:
    """
    LLMRoutingService 인스턴스를 생성하고 반환합니다.

    Args:
        openai_api_key: OpenAI API 키. None인 경우 설정에서 가져옴.
        model: 사용할 LLM 모델명

    Returns:
        LLMRoutingService 인스턴스
    """
    return LLMRoutingService(openai_api_key=openai_api_key, model=model)

