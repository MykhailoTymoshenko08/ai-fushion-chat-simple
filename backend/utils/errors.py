from fastapi import HTTPException
from typing import Optional

class ProviderError(Exception):
    def __init__(self, provider: str, message: str, status_code: int = 500):
        self.provider = provider
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def handle_provider_error(error: ProviderError) -> dict:
    return {
        "error": f"Provider {error.provider} error",
        "message": error.message,
        "status_code": error.status_code
    }