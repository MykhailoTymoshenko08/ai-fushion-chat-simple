import httpx
from typing import AsyncGenerator
from config import settings
from backend.providers.base import ProviderClient

class DeepSeekProvider(ProviderClient):
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = "https://api.deepseek.com/v1"
    
    def is_configured(self) -> bool:
        return bool(self.api_key)
    
    def get_name(self) -> str:
        return "deepseek"
    
    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        if not self.is_configured():
            raise Exception("DeepSeek API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }
        
        async with httpx.AsyncClient(timeout=settings.PROVIDER_TIMEOUT) as client:
            async with client.stream("POST", f"{self.base_url}/chat/completions", 
                                   json=data, headers=headers) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        if line == "data: [DONE]":
                            break
                        try:
                            import json
                            chunk = json.loads(line[6:])
                            if "choices" in chunk and chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue