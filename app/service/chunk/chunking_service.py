from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
import logging
import json

logger = logging.getLogger(__name__)

load_dotenv()

class ChunkingService:
    def __init__(
        self, 
        threshold_type: str = "percentile", 
        threshold_amount: int = 90,
        embeddings: OpenAIEmbeddings = OpenAIEmbeddings(),
    ):
        self.threshold_type = threshold_type
        self.threshold_amount = threshold_amount
        self.embeddings = embeddings

    def split_text(self, text: str) -> list[str]:
        text_splitter = SemanticChunker(
            embeddings=self.embeddings,
            breakpoint_threshold_type=self.threshold_type,
            breakpoint_threshold_amount=self.threshold_amount
        )
        return text_splitter.split_text(text)
    

    def split_text_with_metadata(self, docs:list[dict]) ->list[str]:
        text_splitter = SemanticChunker(
            embeddings=self.embeddings,
            breakpoint_threshold_type=self.threshold_type,
            breakpoint_threshold_amount=self.threshold_amount
        )

        full_text = "\n".join([doc["text"] for doc in docs])

        # logger.info("Full Text:\n" + json.dumps(full_text, ensure_ascii=False, indent=2))

        cuhnk_result = text_splitter.split_text(full_text)

        logger.info("chunkResult:\n" + json.dumps(cuhnk_result, ensure_ascii=False, indent=2))

        return "test"
        # chunkResult = text_splitter.split_text()



        
        # return text_splitter.split_text_with_metadata(text)
    
    

