import pytest
import asyncio
from backend.providers.stubs import StubProvider

@pytest.mark.asyncio
async def test_stub_provider():
    provider = StubProvider("test")
    assert provider.is_configured() == True
    assert provider.get_name() == "test"
    
    chunks = []
    async for chunk in provider.generate("test prompt"):
        chunks.append(chunk)
    
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)

@pytest.mark.asyncio
async def test_provider_initialization():
    from backend.providers.openai import OpenAIProvider
    from backend.providers.groq import GroqProvider
    from backend.providers.deepseek import DeepSeekProvider
    from backend.providers.gemini import GeminiProvider
    
    # Test that providers can be initialized without errors
    providers = [
        OpenAIProvider(),
        GroqProvider(),
        DeepSeekProvider(), 
        GeminiProvider()
    ]
    
    for provider in providers:
        assert hasattr(provider, 'is_configured')
        assert hasattr(provider, 'get_name')
        assert hasattr(provider, 'generate')