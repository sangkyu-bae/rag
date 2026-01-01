from typing import List

from fastapi import APIRouter, UploadFile, File, Request, HTTPException
import fitz
import base64
import logging
from dotenv import load_dotenv
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from platformdirs.version import version_tuple

from app.application.service.parse_document_service import ParseDocumentService
from app.application.service.question_service import QuestionService
from app.domain.llm.embedding.openai_embeding_service import OpenAIEmbed
from app.domain.llm.services.llm_client import LlmClient
from app.infrastructure.vector_store.vector_db import VectorDB
from app.infrastructure.vector_store.vector_factory import VectorFactory, VectorType
from app.infrastructure.vector_store.vector_filter import VectorFilter
from app.service.chunk.parser.text_parseprocessor import TextParseProcessor
from app.service.pdf_service import PdfService
from app.service.chunk.chunking_service import ChunkingService
from app.service.chunk.nlp.nlp_service import NLPService
# from app.services.chunk.chunking_service import ChunkingService
from app.domain.document.services.llm_parse_service import LlamaParseService
load_dotenv()
logger = logging.getLogger(__name__)

router = APIRouter()  
@router.post("/parse-detail")
async def parse_pdf_detail(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    result = []

    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        imgs = []

        for img in page.get_images(full=True):
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)
            img_bytes = pix.tobytes("png")

            # base64 인코딩
            encoded = base64.b64encode(img_bytes).decode("utf-8")

            imgs.append({
                "xref": xref,
                # "image_base64": encoded
            })

        result.append({
            "page": page_num + 1,
            "text": text,
            "images": imgs
        })

    return result

@router.post("/chunk")
def chunk_test():
        text_splitter = SemanticChunker(OpenAIEmbeddings())
        chunks = text_splitter.split_text("Hello, world!")

        return chunks
# -----------------------------
# PDF 업로드 → 텍스트 → 청킹
# -----------------------------
@router.post("/parse-and-chunk")
async def parse_and_chunk(file: UploadFile = File(...)):
    # 1) PDF 읽기
    pdf_bytes = await file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    # 2) 전체 페이지 텍스트 합치기
    full_text = ""
    for page in doc:
        text = page.get_text("text")
        full_text += text + "\n"

    # 3) OpenAI Embedding 준비
    # embedder = OpenAIEmbeddings()
    # 4) Semantic Chunker 준비
    # text_splitter = SemanticChunker(OpenAIEmbeddings())

    # 5) 청킹 수행
    text_splitter = SemanticChunker(
        embeddings=OpenAIEmbeddings(),
        breakpoint_threshold_type="percentile",  # 또는 "cosine"
        breakpoint_threshold_amount=65          # ← 민감도 (값 낮출수록 더 많이 쪼개짐)
    )

    chunks = text_splitter.split_text(full_text)

    # 6) 결과 반환
    return {
        "page_count": len(doc),
        "chunk_count": len(chunks),
        "chunks": chunks
    }

@router.post("/parse-and-chunk-with-service")
async def parse_and_chunk_with_service(file: UploadFile = File(...)):
    pdf_service = PdfService()
    pdf_bytes = await file.read()
    result = pdf_service.parse_pdf(pdf_bytes)

    chunking_service = ChunkingService()
    chunks = chunking_service.split_text_with_metadata(result)
    
    # logger.info(f"Parsed full text: {result}")


    # split_service = ChunkingService()
    # chunks = split_service.split_text(result)
    return result

@router.post("/nlp-test")
def nlp_test(text: str, request: Request):
    nlp_service = NLPService()
    tokens = nlp_service.test(request,text)
    return tokens

@router.post("/parse/pdf")
async def parse_pdf(file: UploadFile = File(...)):
    # 파일 확장자 체크
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    # 업로드된 파일 bytes 읽기
    file_bytes = await file.read()
    llama_parse_service = LlamaParseService()
    # 파싱 실행
    try:
        result = llama_parse_service.parse_bytes(file_bytes, file.filename)
        # return {
        #     "file_name": file.filename,
        #     "pages": result["pages"],
        #     "content": result["content"],
        # }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

@router.post("/test/pd")
async def test_pdf(file:UploadFile = File(...)):
    file_bytes = await file.read()
    svc = ParseDocumentService()

    return svc.execute(file_bytes,file.filename)
    # return  text_parser.preprocess_text('# 크크크앱 개발자 매뉴얼\n\n\n\n\n# 1. 안드로이드앱 빌드 및 스토어 등록')

@router.post("/test/question")
async def test_question(question:str):
    vector_db:VectorDB = VectorFactory.get_vectorstore(VectorType.QDRANT,OpenAIEmbed().embeddings)
    vector_filter_list:List[VectorFilter] = []
    vector_filter_list.append(
        VectorFilter.match("metadata.role","child")
    )
    svc = QuestionService(
        collection="test",
        vector_db=vector_db,
        vector_filters=vector_filter_list,
    )
    return svc.execute(question)