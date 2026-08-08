from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from core.config import GROQ_API_KEY


class LLMService:
    def __init__(self):
        self.model = ChatGroq(model="openai/gpt-oss-120b", api_key=GROQ_API_KEY)

    def generate(
        self,
        prompt: str,
    ) -> str:
        response = self.model.invoke(prompt)
        parser = StrOutputParser()

        return parser.invoke(response) or ""
