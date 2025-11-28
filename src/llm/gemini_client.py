import os
from langchain_google_genai import ChatGoogleGenerativeAI
from src.configs.config import yaml_configs

class GeminiClient:
    def __init__(self, model_name: str = "gemini-2.5-pro", temperature: float = 0.7):
        # Try to get API key from environment variables
        # Support both GEMINI_API_KEY and GOOGLE_API_KEY
        self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables.")

        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self.api_key,
            temperature=temperature,
            transport="rest"
        )

    def generate_response(self, prompt: str) -> str:
        """
        Generates a response from the Gemini model based on the input prompt.
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Error generating response: {str(e)}"

    async def agenerate_response(self, prompt: str) -> str:
        """
        Asynchronously generates a response.
        """
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
