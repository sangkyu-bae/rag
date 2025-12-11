from typing import List, Union
from openai import OpenAI
import os

class OpenAIEmbed:
    """
      OpenAI Embedding Service
      - text-embedding-3-small (1536-dim) 지원
      - 단일/다중 텍스트 모두 처리 가능
      """

    def __init__(self, model: str = "text-embedding-3-small"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed(self, text: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """
        text: str 또는 list[str]
        return:
            - 단일 입력: List[float] (벡터 1개)
            - 리스트 입력: List[List[float]] (벡터 여러 개)
        """

        if isinstance(text, str):
            texts = [text]
            single = True
        else:
            texts = text
            single = False

        # OpenAI Embedding API 호출
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )

        vectors = [item.embedding for item in response.data]

        return vectors[0] if single else vectors