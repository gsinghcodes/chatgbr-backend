from langchain_google_genai import GoogleGenerativeAIEmbeddings

from core.config import GEMINI_API_KEY
from core.enums.user_usage import AIModel


class EmbeddingService:
    def __init__(self) -> None:
        self.client = GoogleGenerativeAIEmbeddings(
            model=AIModel.GEMINI_EMBEDDING.value,
            google_api_key=GEMINI_API_KEY,
            output_dimensionality=1536,
        )

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        return self.client.embed_query(query)

    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        return self.client.embed_documents([text])[0]

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return self.client.embed_documents(texts)
