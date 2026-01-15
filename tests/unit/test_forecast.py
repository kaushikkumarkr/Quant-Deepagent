import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from src.tools.forecast.prophet_forecast import ProphetTool
from src.tools.forecast.technical_indicators import TechnicalAnalysis
from src.utils.cache import disk_cache

# Mock cache
def mock_disk_cache(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

patch('src.utils.cache.disk_cache', side_effect=mock_disk_cache).start()

@pytest.fixture
def mock_yf():
    with patch('src.tools.forecast.prophet_forecast.YahooFinanceTool') as mock:
        yield mock

@pytest.fixture
def mock_yf_tech():
    with patch('src.tools.forecast.technical_indicators.YahooFinanceTool') as mock:
        yield mock

@pytest.fixture
def sample_price_history():
    # Create 200+ days of data
    dates = pd.date_range(start='2023-01-01', periods=250, freq='D')
    prices = np.linspace(100, 200, 250) # Linear trend
    return [
        {"Date": d.strftime('%Y-%m-%d'), "Close": p} 
        for d, p in zip(dates, prices)
    ]

# --- Prophet Tests ---
def test_prophet_forecast(mock_yf, sample_price_history):
    tool = ProphetTool()
    tool.yf_tool.get_price_history.return_value = sample_price_history
    
    # Mock Prophet to avoid slow fitting in unit tests?
    # Actually, fitting on 250 points is fast enough for unit test usually (<1s)
    # But for strict unit testing we might want to mock Prophet.
    # Let's run real Prophet for integration-like verification of the flow.
    
    result = tool.forecast_price("AAPL", periods=5)
    
    assert "error" not in result
    assert result['ticker'] == "AAPL"
    assert result['trend'] in ["bullish", "bearish", "neutral"]
    assert len(result['forecast_data']) == 5
    assert result['forecast_price_30d'] > 0

# --- Technical Analysis Tests ---
def test_tech_indicators(mock_yf_tech, sample_price_history):
    tool = TechnicalAnalysis()
    tool.yf_tool.get_price_history.return_value = sample_price_history
    
    indicators = tool.calculate_indicators("AAPL")
    
    assert "error" not in indicators
    # Test values
    assert indicators['current_price'] == 200.0
    assert indicators['sma_200'] > 0
    # RSI should be high because price is monotonically increasing
    assert indicators['rsi_14'] > 50
    # Volatility should be 0 because linear growth has constant returns? 
    # Actually log returns of linear growth are diff. 
    # But verifying keys exist is main goal.
    assert 'volatility_annualized_pct' in indicators
    assert 'bb_upper' in indicators
