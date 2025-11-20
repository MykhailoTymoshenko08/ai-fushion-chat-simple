import asyncio
import random
from typing import AsyncGenerator
from backend.providers.base import ProviderClient

class StubProvider(ProviderClient):
    def __init__(self, name: str):
        self.name = name
        self.sample_responses = [
            "This is a sample response from the {provider} model.",
            "Based on my analysis, I would recommend considering multiple perspectives.",
            "The key factors to consider here are clarity, accuracy, and relevance.",
            "I've analyzed your query and here's my synthesized response.",
            "This appears to be a complex topic that requires careful consideration."
        ]
    
    def is_configured(self) -> bool:
        return True
    
    def get_name(self) -> str:
        return self.name
    
    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        response = random.choice(self.sample_responses).format(provider=self.name)
        words = response.split()
        
        for word in words:
            await asyncio.sleep(0.1)  # Simulate streaming
            yield word + " "
        
        await asyncio.sleep(0.5)