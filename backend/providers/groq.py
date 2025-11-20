import groq
from typing import AsyncGenerator
from config import settings
from backend.providers.base import ProviderClient

class GroqProvider(ProviderClient):
    def __init__(self):
        self.client = None
        if settings.GROQ_API_KEY:
            self.client = groq.AsyncGroq(api_key=settings.GROQ_API_KEY)
    
    def is_configured(self) -> bool:
        return self.client is not None
    
    def get_name(self) -> str:
        return "groq"
    
    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        if not self.client:
            raise Exception("Groq client not configured")
        
        try:
            stream = await self.client.chat.completions.create(
                model="llama2-70b-4096",
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                timeout=settings.PROVIDER_TIMEOUT
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"Error: {str(e)}"