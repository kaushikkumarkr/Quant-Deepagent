import pytest
from unittest.mock import MagicMock, patch
from src.llm.router import LLMRouter

@pytest.fixture
def mock_groq():
    with patch('src.llm.providers.groq_provider.GroqProvider.is_available') as mock:
        yield mock

@pytest.fixture
def mock_gemini():
    with patch('src.llm.providers.gemini_provider.GeminiProvider.is_available') as mock:
        yield mock

@pytest.fixture
def mock_mlx():
    with patch('src.llm.providers.mlx_provider.MLXProvider.is_available') as mock:
        yield mock

@pytest.fixture
def router():
    return LLMRouter()

def test_router_prioritizes_groq(router, mock_groq, mock_gemini, mock_mlx):
    mock_groq.return_value = True
    mock_gemini.return_value = True
    mock_mlx.return_value = True
    
    with patch('src.llm.providers.groq_provider.GroqProvider.get_llm') as mock_get:
        mock_get.return_value = MagicMock()
        llm = router.get_llm()
        assert llm is not None
        assert router.groq.get_llm.called

def test_router_falls_back_to_gemini(router, mock_groq, mock_gemini, mock_mlx):
    mock_groq.return_value = False
    mock_gemini.return_value = True
    mock_mlx.return_value = True
    
    with patch('src.llm.providers.gemini_provider.GeminiProvider.get_llm') as mock_get:
        mock_get.return_value = MagicMock()
        llm = router.get_llm()
        assert llm is not None
        assert router.gemini.get_llm.called

def test_router_falls_back_to_mlx(router, mock_groq, mock_gemini, mock_mlx):
    mock_groq.return_value = False
    mock_gemini.return_value = False
    mock_mlx.return_value = True
    
    with patch('src.llm.providers.mlx_provider.MLXProvider.get_llm') as mock_get:
        mock_get.return_value = MagicMock()
        llm = router.get_llm()
        assert llm is not None
        assert router.mlx.get_llm.called

def test_check_health(router, mock_groq, mock_gemini, mock_mlx):
    mock_groq.return_value = True
    mock_gemini.return_value = False
    mock_mlx.return_value = True
    
    health = router.check_health()
    assert health['groq'] == True
    assert health['gemini'] == False
    assert health['mlx'] == True
