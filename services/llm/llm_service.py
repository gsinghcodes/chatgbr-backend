from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from core.config import GROQ_API_KEY


class LLMService:
    def __init__(self):
        self.model = ChatGroq(model="openai/gpt-oss-120b", api_key=GROQ_API_KEY)
        self.parser = StrOutputParser()

    def generate(
        self,
        prompt: str,
    ) -> str:
        chain = self.model | self.parser

        return chain.invoke(prompt) or ""

    def stream(self, prompt: str):
        for chunk in self.model.stream(prompt):
            reasoning = chunk.additional_kwargs.get("reasoning_content")
            if reasoning:
                yield {"type": "reasoning", "content": reasoning}

            content = self.parser.invoke(chunk)
            if content:
                yield {"type": "token", "content": content}

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
