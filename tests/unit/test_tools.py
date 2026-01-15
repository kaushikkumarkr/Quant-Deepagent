import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from src.tools.financial.yahoo_finance import YahooFinanceTool
from src.tools.financial.sec_edgar import SECTool
from src.tools.financial.fred import FREDTool
from src.tools.sentiment.news_api import NewsAPITool
from src.utils.cache import disk_cache

# Mock disk_cache to be a pass-through decorator for tests
# This prevents pickling errors when caching methods of objects with MagicMocks
def mock_disk_cache(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

patch('src.utils.cache.disk_cache', side_effect=mock_disk_cache).start()

# --- Yahoo Finance Tests ---
@pytest.fixture
def mock_ticker():
    with patch('yfinance.Ticker') as mock:
        instance = mock.return_value
        instance.info = {'symbol': 'AAPL', 'marketCap': 1000000}
        instance.financials = pd.DataFrame()
        instance.balance_sheet = pd.DataFrame()
        instance.cashflow = pd.DataFrame()
        instance.earnings_history = pd.DataFrame()
        instance.recommendations = pd.DataFrame()  # Older yfinance
        yield mock

def test_yahoo_get_stock_info(mock_ticker):
    data = YahooFinanceTool.get_stock_info("AAPL")
    assert data['symbol'] == 'AAPL'
    assert 'marketCap' in data

def test_yahoo_failures_handled(mock_ticker):
    mock_ticker.side_effect = Exception("API Error")
    data = YahooFinanceTool.get_stock_info("INVALID")
    assert "error" in data

# --- SEC Tool Tests ---
@pytest.fixture
def mock_downloader():
    with patch('src.tools.financial.sec_edgar.Downloader') as mock:
        yield mock

def test_sec_download(mock_downloader):
    tool = SECTool()
    with patch('glob.glob') as mock_glob:
        mock_glob.return_value = ["data/sec/10k.txt"]
        files = tool.download_filings("AAPL", "10-K")
        assert len(files) == 1
        assert files[0] == "data/sec/10k.txt"

# --- FRED Tool Tests ---
@pytest.fixture
def mock_fred():
    with patch('src.tools.financial.fred.Fred') as mock:
        yield mock

def test_fred_get_data(mock_fred):
    # Mock settings to allow client init
    with patch('src.tools.financial.fred.settings') as s:
        s.fred_api_key = "test_key"
        tool = FREDTool()
        
        # Mock series data
        mock_series = pd.Series([1.1, 1.2], index=pd.to_datetime(['2024-01-01', '2024-02-01']))
        tool.client.get_series.return_value = mock_series
        tool.client.get_series_info.return_value = {'units': 'Percent'}
        
        data = tool.get_economic_data("GDP")
        assert data['latest_value'] == 1.2
        assert data['units'] == 'Percent'
        assert len(data['history']) == 2


