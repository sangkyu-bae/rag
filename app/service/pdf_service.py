import fitz
import base64
import logging
import json
import re

logger = logging.getLogger(__name__)

class PdfService:
    def __init__(self):
        pass
    # ------------------------------
    # 1. Layout 기반 섹션 감지기
    # ------------------------------
    def split_sections_layout(self, page) -> list[str]:
        blocks = page.get_text("dict")["blocks"]

        sections = []
        buffer = []

        last_font = None

        for block in blocks:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    font = span["size"]

                    # 1) 글자 크기가 확 증가하면 섹션 시작
                    if last_font and font > last_font + 1.2:
                        if buffer:
                            sections.append("\n".join(buffer))
                            buffer = []

                    # 2) 리스트/번호로 시작하는 경우 섹션 단위로 나눔
                    if re.match(r"^\d+\.\s|^\d+\)\s|^\(\d+\)", text):
                        if buffer:
                            sections.append("\n".join(buffer))
                            buffer = []

                    buffer.append(text)
                    last_font = font

        if buffer:
            sections.append("\n".join(buffer))

        return sections

    # ------------------------------
    # 2. PDF → 페이지별 → 섹션별 parsing
    # ------------------------------
    def parse_pdf(self, pdf_bytes: bytes, filetype: str = "pdf") -> list[dict]:
        doc = fitz.open(stream=pdf_bytes, filetype=filetype)
        result = []

        for page_num, page in enumerate(doc):
            # 섹션 감지
            sections = self.split_sections_layout(page)

            imgs = []
            for img in page.get_images(full=True):
                xref = img[0]
                try:
                    pix = fitz.Pixmap(doc, xref)
                    img_bytes = pix.tobytes("png")
                    encoded = base64.b64encode(img_bytes).decode("utf-8")
                except:
                    continue

                imgs.append({
                    "xref": xref,
                    # "image_base64": encoded
                })

            # 섹션 별로 저장
            for sec in sections:
                result.append({
                    "page": page_num + 1,
                    "text": sec,
                    "images": imgs
                })

        logger.info("Parsed PDF:\n" + json.dumps(result, ensure_ascii=False, indent=2))
        return result

    # 기존 normalize — 지금은 사용 안 해도 되지만 남겨둠
    def normalize_numbered_lines(self, text: str) -> str:
        lines = text.splitlines()
        merged = []
        for i, line in enumerate(lines):
            if re.fullmatch(r"\d+\.", line.strip()) and i + 1 < len(lines):
                merged.append(f"{line.strip()} {lines[i+1].lstrip()}")
                lines[i+1] = ""
            elif line != "":
                merged.append(line)
        return "\n".join(merged)

    def parse_full_text(self, pdf_bytes: bytes, filetype: str = "pdf") -> str:
        doc = fitz.open(stream=pdf_bytes, filetype=filetype)
        full_text = ""
        for page in doc:
            text = page.get_text("text")
            full_text += text + "\n"
        return full_text

    # def parse_pdf(self, pdf_bytes: bytes, filetype: str = "pdf") -> list[dict]:
    #     doc = fitz.open(stream=pdf_bytes, filetype=filetype)
    #     result = []

    #     for page_num, page in enumerate(doc):
    #         text = page.get_text("text")
    #         text = self.normalize_numbered_lines(text)
    #         imgs = []

    #         for img in page.get_images(full=True):
    #             xref = img[0]
    #             try:
    #                 pix = fitz.Pixmap(doc, xref)
    #                 img_bytes = pix.tobytes("png")
    #                 encoded = base64.b64encode(img_bytes).decode("utf-8")
    #             except Exception as e:
    #                 # 이미지 추출 실패 방지
    #                 continue

    #             imgs.append({
    #                 "xref": xref,
    #                 # "image_base64": encoded
    #             })

    #         result.append({
    #             "page": page_num + 1,
    #             "text": text,
    #             "images": imgs
    #         })

    #     logger.info("Parsed PDF:\n" + json.dumps(result, ensure_ascii=False, indent=2))
    #     return result

    # def normalize_numbered_lines(self, text: str) -> str:
    #     lines = text.splitlines()
    #     merged = []
    #     for i, line in enumerate(lines):
    #         if re.fullmatch(r"\d+\.", line.strip()) and i + 1 < len(lines):
    #             # 다음 줄과 합치기
    #             merged.append(f"{line.strip()} {lines[i+1].lstrip()}")
    #             # 다음 줄은 스킵
    #             lines[i+1] = ""
    #         elif line != "":
    #             merged.append(line) 
    #     return "\n".join(merged)
    #     return chunks    

    # def parse_full_text(self,pdf_bytes: bytes,filetype: str = "pdf") -> str:
    #     doc = fitz.open(stream=pdf_bytes, filetype=filetype)

    #     full_text = ""
    #     for page in doc:
    #         text = page.get_text("text")
    #         full_text += text + "\n"
    #     return full_text