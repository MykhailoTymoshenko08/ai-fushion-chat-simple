
import google.generativeai as genai
from typing import AsyncGenerator
from config import settings
from backend.providers.base import ProviderClient

class GeminiProvider(ProviderClient):
    def __init__(self):
        self.client = None
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.client = genai
    
    def is_configured(self) -> bool:
        return self.client is not None
    
    def get_name(self) -> str:
        return "gemini"
    
    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        if not self.client:
            raise Exception("Gemini client not configured")
        
        try:
            model = self.client.GenerativeModel('gemini-pro')
            response = await model.generate_content_async(prompt, stream=True)
            
            async for chunk in response:
                yield chunk.text
                
        except Exception as e:
            yield f"Error: {str(e)}"