import openai
from typing import AsyncGenerator
import asyncio
from config import settings
from backend.providers.base import ProviderClient

class OpenAIProvider(ProviderClient):
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    def is_configured(self) -> bool:
        return self.client is not None
    
    def get_name(self) -> str:
        return "openai"
    
    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        if not self.client:
            raise Exception("OpenAI client not configured")
        
        try:
            stream = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                timeout=settings.PROVIDER_TIMEOUT
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"Error: {str(e)}"