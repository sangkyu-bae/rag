"""LlamaParse 서비스를 통한 문서 파싱 로직."""

import asyncio
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from llama_parse import LlamaParse
from app.core.config import settings

logger = logging.getLogger(__name__)


class LlamaParseService:
    """LlamaParse API를 사용한 문서 파싱 서비스."""

    def __init__(self, api_key: Optional[str] = None):
        """
        LlamaParse 서비스 초기화.

        Args:
            api_key: LlamaParse API 키. None인 경우 설정에서 가져옴.
        """
        self.api_key = api_key or getattr(settings, "LLAMA_PARSE_API_KEY", None)
        if not self.api_key:
            raise ValueError("LlamaParse API 키가 설정되지 않았습니다. LLAMA_PARSE_API_KEY 환경 변수를 설정해주세요.")
        
        self.parser = LlamaParse(
            api_key=self.api_key,
            result_type="markdown",  # 또는 "text"
            verbose=True,
        )

    async def parse_file_async(
        self,
        file_path: str,
        result_type: str = "markdown",
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        비동기로 파일을 파싱합니다.

        Args:
            file_path: 파싱할 파일 경로
            result_type: 결과 타입 ("markdown" 또는 "text")
            language: 문서 언어 (예: "ko", "en")

        Returns:
            파싱된 문서 내용과 메타데이터를 포함한 딕셔너리

        Raises:
            FileNotFoundError: 파일이 존재하지 않는 경우
            ValueError: API 키가 유효하지 않은 경우
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        try:
            logger.info(f"파일 파싱 시작: {file_path}")
            
            # LlamaParse는 동기 함수이므로 asyncio.to_thread로 비동기 실행
            loop = asyncio.get_event_loop()
            documents = await loop.run_in_executor(
                None,
                lambda: self.parser.load_data(file_path)
            )

            # 결과 처리
            parsed_content = "\n\n".join([doc.text for doc in documents])
            metadata = {
                "file_path": str(file_path),
                "file_name": file_path_obj.name,
                "file_size": file_path_obj.stat().st_size,
                "pages_count": len(documents),
                "result_type": result_type,
            }

            logger.info(f"파싱 완료: {file_path}, 페이지 수: {len(documents)}")

            return {
                "content": parsed_content,
                "metadata": metadata,
                "documents": [{"text": doc.text, "metadata": doc.metadata} for doc in documents],
            }

        except Exception as e:
            logger.error(f"파일 파싱 중 오류 발생: {file_path}, 오류: {str(e)}")
            raise

    def parse_file_sync(
        self,
        file_path: str,
        result_type: str = "markdown",
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        동기로 파일을 파싱합니다.

        Args:
            file_path: 파싱할 파일 경로
            result_type: 결과 타입 ("markdown" 또는 "text")
            language: 문서 언어 (예: "ko", "en")

        Returns:
            파싱된 문서 내용과 메타데이터를 포함한 딕셔너리

        Raises:
            FileNotFoundError: 파일이 존재하지 않는 경우
            ValueError: API 키가 유효하지 않은 경우
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        try:
            logger.info(f"파일 파싱 시작: {file_path}")
            
            documents = self.parser.load_data(file_path)

            # 결과 처리
            parsed_content = "\n\n".join([doc.text for doc in documents])
            metadata = {
                "file_path": str(file_path),
                "file_name": file_path_obj.name,
                "file_size": file_path_obj.stat().st_size,
                "pages_count": len(documents),
                "result_type": result_type,
            }

            logger.info(f"파싱 완료: {file_path}, 페이지 수: {len(documents)}")

            return {
                "content": parsed_content,
                "metadata": metadata,
                "documents": [{"text": doc.text, "metadata": doc.metadata} for doc in documents],
            }

        except Exception as e:
            logger.error(f"파일 파싱 중 오류 발생: {file_path}, 오류: {str(e)}")
            raise

    async def parse_bytes_async(
        self,
        file_bytes: bytes,
        file_name: str,
        result_type: str = "markdown",
    ) -> Dict[str, Any]:
        """
        비동기로 바이트 데이터를 파싱합니다.

        Args:
            file_bytes: 파싱할 파일의 바이트 데이터
            file_name: 파일 이름 (확장자 포함)
            result_type: 결과 타입 ("markdown" 또는 "text")

        Returns:
            파싱된 문서 내용과 메타데이터를 포함한 딕셔너리
        """
        import tempfile
        import os

        # 임시 파일로 저장 후 파싱
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_name).suffix) as tmp_file:
            try:
                tmp_file.write(file_bytes)
                tmp_file_path = tmp_file.name
                
                result = await self.parse_file_async(
                    file_path=tmp_file_path,
                    result_type=result_type,
                )
                
                return result
            finally:
                # 임시 파일 삭제
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)


def get_llama_parse_service() -> LlamaParseService:
    """
    LlamaParseService 인스턴스를 생성하고 반환합니다.
    
    Returns:
        LlamaParseService 인스턴스
    """
    return LlamaParseService()

