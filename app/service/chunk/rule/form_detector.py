import re
import logging

logger = logging.getLogger(__name__)

class FormDetector:
    def __init__(self):
        pass
    
    def rule_based_form_score(text:str)->int:
        text_lower = text.lower()
        score = 0

        # 1) 서식 / 별지 패턴
        if "서식" in text_lower or "별지" in text_lower:
            score += 2

        # 2) markdown table
        if "|" in text and re.search(r"\|\s*-{2,}\s*\|", text):
            score += 2

        # 3) 빈칸 기입 패턴
        if re.search(r"\(\s*\)", text) or "년  월  일" in text:
            score += 2

        # 4) 결재/직인/귀중 패턴
        if any(x in text_lower for x in ["직인", "귀중", "결재"]):
            score += 2

        # 5) 기입 지시문 패턴
        if any(x in text_lower for x in ["기입", "표를", "작성"]):
            score += 1

        # 6) 의미 문장 개수가 매우 적음 (서식일 확률 높음)
        sentences = [s for s in re.split(r"[.!?]\s*", text) if len(s.strip()) > 5]
        if len(sentences) < 3:
            score += 1

        return score
    def rule_based_document_type(text: str) -> dict:
        score = rule_based_form_score(text)

        if score >= 5:
            return {"type": "FORM", "reason": f"Rule score={score} (high certainty)"}

        if score <= 1:
            return {"type": "NORMAL", "reason": f"Rule score={score} (likely natural language)"}

        # score 2~4: ambiguous → LLM에게 넘겨라
        return {"type": "AMBIGUOUS", "reason": f"Rule score={score} (needs LLM checking)"}