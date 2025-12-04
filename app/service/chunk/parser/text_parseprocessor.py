import re
import unicodedata
from typing import List, Iterable, Optional
from dotenv import load_dotenv
import logging
load_dotenv()
logger = logging.getLogger(__name__)
class TextParseProcessor:
    def __init__(self):
        pass
        # 1) 유니코드 정규화 (한글/기호 깨짐 방지)
    def normalize_unicode(text: str, form: str = "NFKC") -> str:
        """
        유니코드 정규화.
        - NFKC: 호환문자도 통합 (예: '１' -> '1')
        """
        return unicodedata.normalize(form, text)


    # 2) 공백/줄바꿈 정리
    def normalize_whitespace(text: str) -> str:
        """
        - 탭을 공백으로
        - 여러 공백을 하나로
        - 양끝 공백 제거
        """
        text = text.replace("\t", " ")
        # 줄 단위로 trim + 빈 줄 축소
        lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
        # 연속 빈 줄은 최대 1개
        normalized_lines = []
        prev_blank = False
        for line in lines:
            if line == "":
                if prev_blank:
                    continue
                prev_blank = True
            else:
                prev_blank = False
            normalized_lines.append(line)
        return "\n".join(normalized_lines).strip()


    # 3) 특수문자/따옴표/대시 통일
    def normalize_punctuation(text: str) -> str:
        """
        - 다양한 따옴표를 " 로 통일
        - 긴 대시(—, –)를 보통 하이픈(-)으로 통일
        """
        # 따옴표
        text = re.sub(r"[“”«»‟]", '"', text)
        text = re.sub(r"[‘’‚‛]", "'", text)

        # 대시류
        text = re.sub(r"[‐-‒–—─]", "-", text)

        # 특수 공백 제거
        text = text.replace("\u00A0", " ").replace("\u200B", "")

        return text


    # 4) 줄바꿈+하이픈으로 쪼개진 단어 붙이기
    def fix_hyphenated_linebreaks(text: str) -> str:
        """
        금-
        융  -> 금융
        처럼 줄 끝 하이픈 + 줄바꿈으로 쪼개진 단어 복원
        """
        # 단어중간 하이픈 + 개행 제거
        return re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)


    # 5) 한 문장인데 줄바꿈으로 쪼개진 경우 합치기
    def merge_broken_lines(text: str) -> str:
        """
        - 라인 끝이 문장부호(.,?!… 등)로 끝나지 않으면 다음 줄과 합침
        - 약관/계약서에서 줄바꿈이 많은 경우 문장 단위로 복원에 도움
        """
        lines = [l.rstrip() for l in text.splitlines()]
        merged_lines: List[str] = []
        buffer = ""

        sentence_end_pattern = re.compile(r"[.!?…]$|[다요죠]\s*$")  # 단순 한국어 종결 어미 포함

        for line in lines:
            if not line:
                if buffer:
                    merged_lines.append(buffer.strip())
                    buffer = ""
                merged_lines.append("")  # 단락 구분 유지
                continue

            if not buffer:
                buffer = line
            else:
                # 이전 줄이 문장 끝이 아니면 이어붙임
                if not sentence_end_pattern.search(buffer):
                    buffer += " " + line.lstrip()
                else:
                    merged_lines.append(buffer.strip())
                    buffer = line

        if buffer:
            merged_lines.append(buffer.strip())

        return "\n".join(merged_lines)
    
        # 12) 전체 파이프라인
    def preprocess_text(
        text: str,
        header_patterns: Optional[Iterable[str]] = None,
        footer_patterns: Optional[Iterable[str]] = None,
        boilerplate_phrases: Optional[Iterable[str]] = None,
        do_sentence_split: bool = False,
    ) -> str | List[str]:
        """
        LlamaParse 결과(heading+content 등)를 받아서
        RAG 임베딩 이전에 돌릴 전체 전처리 파이프라인.

        do_sentence_split=True 이면 문장 리스트 반환.
        """
        text = self.normalize_unicode(text)
        text = self.normalize_punctuation(text)
        text = self.fix_hyphenated_linebreaks(text)
        text = self.normalize_whitespace(text)
        text = self.merge_broken_lines(text)

        return text