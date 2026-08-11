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

    def generate_conversation_title(
        self,
        question: str,
    ) -> str:
        prompt = f"""
    Generate a short title for a developer conversation.
    
    User question:
    {question}
    
    Rules:
    - Maximum 8 words
    - Be concise and descriptive
    - Do not use quotes
    - Do not add punctuation at the end
    - Return only the title
    """

        title = self.generate(
            prompt=prompt,
        )

        return title.strip()[:255]
