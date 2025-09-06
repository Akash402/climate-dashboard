"""
Unit tests for utils.py module.
"""

import pytest
from datetime import datetime, timezone
import numpy as np
from unittest.mock import Mock, patch

from utils import (
    http_get, try_urls, now_utc_str, fmt_num,
    mm_to_inches, m_to_inches
)


class TestHttpGet:
    """Test cases for http_get function."""
    
    def test_http_get_success(self, mock_requests):
        """Test successful HTTP GET request."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response
        
        result = http_get("https://example.com")
        
        mock_requests.assert_called_once_with(
            "https://example.com", 
            timeout=30, 
            allow_redirects=True,
            headers={"User-Agent": "climate-dashboard/1.2 (+github actions)"}
        )
        assert result == mock_response
    
    def test_http_get_with_custom_params(self, mock_requests):
        """Test HTTP GET with custom parameters."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_requests.return_value = mock_response
        
        result = http_get("https://example.com", timeout=60, allow_redirects=False)
        
        mock_requests.assert_called_once_with(
            "https://example.com", 
            timeout=60, 
            allow_redirects=False,
            headers={"User-Agent": "climate-dashboard/1.2 (+github actions)"}
        )


class TestTryUrls:
    """Test cases for try_urls function."""
    
    def test_try_urls_success_first_url(self, mock_requests):
        """Test try_urls with successful first URL."""
        mock_response = Mock()
        mock_response.content = b"binary data"
        mock_response.text = "text data"
        mock_requests.return_value = mock_response
        
        urls = ["https://example1.com", "https://example2.com"]
        url, content = try_urls(urls, binary=True)
        
        assert url == "https://example1.com"
        assert content == b"binary data"
        mock_requests.assert_called_once()
    
    def test_try_urls_success_second_url(self, mock_requests):
        """Test try_urls with first URL failing, second succeeding."""
        mock_response = Mock()
        mock_response.text = "text data"
        
        # First call raises exception, second succeeds
        mock_requests.side_effect = [Exception("First failed"), mock_response]
        
        urls = ["https://example1.com", "https://example2.com"]
        url, content = try_urls(urls, binary=False)
        
        assert url == "https://example2.com"
        assert content == "text data"
        assert mock_requests.call_count == 2
    
    def test_try_urls_all_fail(self, mock_requests):
        """Test try_urls when all URLs fail."""
        mock_requests.side_effect = Exception("All failed")
        
        urls = ["https://example1.com", "https://example2.com"]
        
        with pytest.raises(Exception, match="All failed"):
            try_urls(urls)


class TestNowUtcStr:
    """Test cases for now_utc_str function."""
    
    def test_now_utc_str_format(self):
        """Test that now_utc_str returns properly formatted string."""
        result = now_utc_str()
        
        # Should be in format "YYYY-MM-DD HH:MM UTC"
        assert "UTC" in result
        assert len(result) == 20  # "YYYY-MM-DD HH:MM UTC"
        
        # Should be parseable as datetime
        dt = datetime.strptime(result, "%Y-%m-%d %H:%M UTC")
        assert dt.tzinfo is None  # UTC time without timezone info


class TestFmtNum:
    """Test cases for fmt_num function."""
    
    def test_fmt_num_integer(self):
        """Test formatting integer values."""
        assert fmt_num(42) == "42"
        assert fmt_num(0) == "0"
        assert fmt_num(-5) == "-5"
    
    def test_fmt_num_float(self):
        """Test formatting float values."""
        assert fmt_num(42.5) == "42.50"
        assert fmt_num(42.567) == "42.57"  # Rounds to 2 decimal places
        assert fmt_num(42.0) == "42.00"
    
    def test_fmt_num_custom_decimal_places(self):
        """Test formatting with custom decimal places."""
        assert fmt_num(42.567, nd=1) == "42.6"
        assert fmt_num(42.567, nd=3) == "42.567"
        assert fmt_num(42.567, nd=0) == "43"
    
    def test_fmt_num_none(self):
        """Test formatting None values."""
        assert fmt_num(None) == "—"
        assert fmt_num(None, default="N/A") == "N/A"
    
    def test_fmt_num_nan(self):
        """Test formatting NaN values."""
        assert fmt_num(float('nan')) == "—"
        assert fmt_num(np.nan) == "—"
    
    def test_fmt_num_exception(self):
        """Test formatting with invalid input."""
        assert fmt_num("invalid") == "—"


class TestUnitConversions:
    """Test cases for unit conversion functions."""
    
    def test_mm_to_inches(self):
        """Test millimeters to inches conversion."""
        assert mm_to_inches(25.4) == pytest.approx(1.0, rel=1e-6)
        assert mm_to_inches(0) == 0
        assert mm_to_inches(100) == pytest.approx(3.937, rel=1e-3)
    
    def test_m_to_inches(self):
        """Test meters to inches conversion."""
        assert m_to_inches(1) == pytest.approx(39.3701, rel=1e-6)
        assert m_to_inches(0) == 0
        assert m_to_inches(0.1) == pytest.approx(3.937, rel=1e-3)
