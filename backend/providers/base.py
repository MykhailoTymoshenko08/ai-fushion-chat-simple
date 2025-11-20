from abc import ABC, abstractmethod
from typing import AsyncGenerator

class ProviderClient(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        pass
    
    @abstractmethod
    def is_configured(self) -> bool:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass