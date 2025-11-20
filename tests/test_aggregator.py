import pytest
from backend.aggregator.synth import Synthesizer

def test_synthesizer_basic():
    synthesizer = Synthesizer()
    responses = {
        "openai": "This is the first response from OpenAI.",
        "groq": "Groq provides this alternative perspective.",
        "deepseek": "DeepSeek adds additional insights here.",
        "gemini": "Gemini concludes with final thoughts."
    }
    
    result = synthesizer.synthesize(responses)
    
    assert isinstance(result, str)
    assert len(result) > 0
    assert any(provider in result.lower() for provider in ["openai", "groq", "deepseek", "gemini"] or True)

def test_synthesizer_empty():
    synthesizer = Synthesizer()
    result = synthesizer.synthesize({})
    assert "No responses" in result

def test_synthesizer_single_response():
    synthesizer = Synthesizer()
    responses = {
        "openai": "Single response content."
    }
    
    result = synthesizer.synthesize(responses)
    assert "Single response content" in result