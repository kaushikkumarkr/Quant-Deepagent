import pytest
from unittest.mock import MagicMock, patch
from src.tools.sentiment.finbert import FinBERT
from src.tools.search.web_search import WebSearchTool
from src.tools.sentiment.news_search import NewsSentimentTool

# --- FinBERT Tests ---
@pytest.fixture
def mock_transformers():
    with patch('src.tools.sentiment.finbert.AutoTokenizer') as mock_tok, \
         patch('src.tools.sentiment.finbert.AutoModelForSequenceClassification') as mock_model, \
         patch('src.tools.sentiment.finbert.pipeline') as mock_pipe:
        yield mock_pipe

def test_finbert_singleton(mock_transformers):
    # Ensure initialized only once
    fb1 = FinBERT()
    fb2 = FinBERT()
    assert fb1 is fb2

def test_finbert_analysis(mock_transformers):
    fb = FinBERT()
    # Mock pipeline output
    fb.nlp.return_value = [[{'label': 'positive', 'score': 0.9}, {'label': 'negative', 'score': 0.1}]]
    
    res = fb.analyze_text("Great stock!")
    assert res['label'] == 'positive'
    assert res['score'] == 0.9

def test_finbert_batch(mock_transformers):
    fb = FinBERT()
    fb.nlp.return_value = [[{'label': 'positive', 'score': 0.9}]] # Repeated for each call
    
    res = fb.analyze_batch(["Good", "Good"])
    assert res['sentiment_score'] > 0
    assert res['label'] == 'bullish'

# --- Search Tests ---
@pytest.fixture
def mock_ddgs():
    with patch('src.tools.search.web_search.DDGS') as mock:
        yield mock

def test_web_search(mock_ddgs):
    tool = WebSearchTool()
    tool.ddgs.text.return_value = [{'title': 'Test', 'href': 'url', 'body': 'content'}]
    
    res = tool.search_general("query")
    assert len(res) == 1
    assert res[0]['title'] == 'Test'

# --- Combined Pipeline Tests ---
def test_news_pipeline():
    with patch('src.tools.sentiment.news_search.WebSearchTool') as mock_search, \
         patch('src.tools.sentiment.news_search.FinBERT') as mock_finbert, \
         patch('src.tools.sentiment.news_search.disk_cache') as mock_cache:
         
        # Mock cache bypass
        mock_cache.side_effect = lambda expire=0: lambda f: f
        
        pipeline = NewsSentimentTool()
        mock_search.return_value.search_news.return_value = [
            {'title': 'Title', 'href': 'url', 'body': 'Good news', 'date': 'Today'}
        ]
        
        mock_finbert.return_value.analyze_batch.return_value = {
            'sentiment_score': 0.8,
            'label': 'bullish'
        }
        
        res = pipeline.analyze_ticker_news("AAPL")
        assert res['overall_sentiment'] == 'bullish'
        assert res['sentiment_score'] == 0.8
