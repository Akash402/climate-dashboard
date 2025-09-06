"""
Unit tests for data_fetchers.py module.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from data_fetchers import (
    fetch_noaa_co2_monthly, fetch_met_eireann_warnings,
    fetch_psmsl_dublin_note, fetch_forest_fires_data,
    fetch_nsidc_arctic_daily, fetch_noaa_ncei_ohc_latest,
    _parse_nsidc_daily_csv, save_png
)


class TestFetchNoaaCo2Monthly:
    """Test cases for fetch_noaa_co2_monthly function."""
    
    @patch('data_fetchers.http_get')
    @patch('data_fetchers.save_png')
    def test_fetch_co2_success(self, mock_save_png, mock_http_get):
        """Test successful CO₂ data fetching."""
        # Mock CSV response
        csv_data = """# CO2 data
2024,11,2024.87,424.36,424.15,30,0.11,0.05
2024,12,2024.95,425.48,425.20,31,0.12,0.05"""
        
        mock_response = Mock()
        mock_response.text = csv_data
        mock_http_get.return_value = mock_response
        
        result = fetch_noaa_co2_monthly()
        
        assert result["year"] == 2024
        assert result["month"] == 12
        assert result["ppm"] == 425.48
        assert result["chart"] == "co2_24mo.png"
        assert "noaa.gov" in result["source"]
        mock_save_png.assert_called_once()
    
    @patch('data_fetchers.http_get')
    def test_fetch_co2_http_error(self, mock_http_get):
        """Test CO₂ fetching with HTTP error."""
        mock_http_get.side_effect = Exception("HTTP Error")
        
        with pytest.raises(Exception, match="HTTP Error"):
            fetch_noaa_co2_monthly()


class TestFetchMetEireannWarnings:
    """Test cases for fetch_met_eireann_warnings function."""
    
    @patch('data_fetchers.http_get')
    def test_fetch_warnings_success(self, mock_http_get):
        """Test successful warnings fetching."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "warnings": [
                {"status": "active", "title": "Storm Warning"},
                {"status": "active", "title": "Flood Alert"},
                {"status": "inactive", "title": "Old Warning"}
            ]
        }
        mock_http_get.return_value = mock_response
        
        result = fetch_met_eireann_warnings()
        
        assert result["count"] == 2
        assert "Storm Warning" in result["titles"]
        assert "Flood Alert" in result["titles"]
        assert "met.ie" in result["source"]
    
    @patch('data_fetchers.http_get')
    def test_fetch_warnings_error(self, mock_http_get):
        """Test warnings fetching with error."""
        mock_http_get.side_effect = Exception("Network Error")
        
        result = fetch_met_eireann_warnings()
        
        assert result["count"] == "N/A"
        assert result["titles"] == []
        assert "met.ie" in result["source"]


class TestFetchPsmslDublinNote:
    """Test cases for fetch_psmsl_dublin_note function."""
    
    def test_fetch_dublin_note(self):
        """Test Dublin tide gauge note fetching."""
        result = fetch_psmsl_dublin_note()
        
        assert "psmsl.org" in result["link"]
        assert "Dublin" in result["note"]
        assert "rise" in result["note"]


class TestFetchForestFiresData:
    """Test cases for fetch_forest_fires_data function."""
    
    @patch('data_fetchers.http_get')
    def test_fetch_fires_success(self, mock_http_get):
        """Test successful forest fires data fetching."""
        csv_data = """lat,lon,brightness,scan,track,acq_date,acq_time,satellite,confidence,version,bright_t31,frp,daynight
40.5,-74.2,300.5,1.2,1.1,2024-12-01,1200,NPP,80,1,290.2,15.3,D
41.0,-75.0,310.2,1.3,1.2,2024-12-01,1215,NPP,85,1,295.1,18.7,D"""
        
        mock_response = Mock()
        mock_response.text = csv_data
        mock_http_get.return_value = mock_response
        
        result = fetch_forest_fires_data()
        
        assert result["count"] == 2
        assert "nasa.gov" in result["source"]
        assert "24 hours" in result["description"]
    
    @patch('data_fetchers.http_get')
    def test_fetch_fires_error(self, mock_http_get):
        """Test forest fires fetching with error."""
        mock_http_get.side_effect = Exception("API Error")
        
        result = fetch_forest_fires_data()
        
        assert result["count"] == "N/A"
        assert "nasa.gov" in result["source"]
        assert "unavailable" in result["description"]


class TestParseNsidcDailyCsv:
    """Test cases for _parse_nsidc_daily_csv function."""
    
    def test_parse_nsidc_csv_success(self):
        """Test successful NSIDC CSV parsing."""
        csv_data = """Year,Month,Day,Extent
2024,12,1,12.5
2024,12,2,12.3
2024,12,3,12.1"""
        
        df, ecol = _parse_nsidc_daily_csv(csv_data)
        
        assert ecol == "Extent"
        assert len(df) == 3
        assert df.iloc[0]["Extent"] == 12.5
        assert df.iloc[-1]["Extent"] == 12.1
    
    def test_parse_nsidc_csv_with_header_search(self):
        """Test NSIDC CSV parsing with header search."""
        csv_data = """Some header
Another header
YYYY,MM,DD,Extent
2024,12,1,12.5
2024,12,2,12.3"""
        
        df, ecol = _parse_nsidc_daily_csv(csv_data)
        
        assert ecol == "Extent"
        assert len(df) == 2
        assert df.iloc[0]["Extent"] == 12.5
    
    def test_parse_nsidc_csv_missing_columns(self):
        """Test NSIDC CSV parsing with missing required columns."""
        csv_data = """Year,Month,Value
2024,12,12.5"""
        
        with pytest.raises(ValueError, match="Unexpected NSIDC CSV columns"):
            _parse_nsidc_daily_csv(csv_data)


class TestFetchNsidcArcticDaily:
    """Test cases for fetch_nsidc_arctic_daily function."""
    
    @patch('data_fetchers.try_urls')
    @patch('data_fetchers.save_png')
    def test_fetch_nsidc_success(self, mock_save_png, mock_try_urls):
        """Test successful NSIDC data fetching."""
        csv_data = """Year,Month,Day,Extent
2024,12,1,12.5
2024,12,2,12.3"""
        
        mock_try_urls.return_value = ("https://example.com", csv_data)
        
        result = fetch_nsidc_arctic_daily()
        
        assert result["latest"]["extent_mkm2"] == 12.3
        assert result["chart"] == "arctic_extent_365d.png"
        assert "nsidc.org" in result["source"]
        mock_save_png.assert_called_once()
    
    @patch('data_fetchers.try_urls')
    def test_fetch_nsidc_all_urls_fail(self, mock_try_urls):
        """Test NSIDC fetching when all URLs fail."""
        mock_try_urls.side_effect = Exception("All URLs failed")
        
        result = fetch_nsidc_arctic_daily()
        
        assert result["latest"]["date"] == "N/A"
        assert np.isnan(result["latest"]["extent_mkm2"])
        assert result["chart"] == ""


class TestFetchNoaaNceiOhcLatest:
    """Test cases for fetch_noaa_ncei_ohc_latest function."""
    
    @patch('data_fetchers.try_urls')
    def test_fetch_ohc_success(self, mock_try_urls):
        """Test successful ocean heat content fetching."""
        csv_data = """Year,OHC_0-2000m
2023,15.2
2022,14.8"""
        
        mock_try_urls.return_value = ("https://example.com", csv_data)
        
        result = fetch_noaa_ncei_ohc_latest()
        
        assert result["year"] == 2023
        assert result["value"] == 15.2
        assert result["units"] == "J × 10^22"
        assert "ncei.noaa.gov" in result["source"]
    
    @patch('data_fetchers.try_urls')
    def test_fetch_ohc_all_urls_fail(self, mock_try_urls):
        """Test OHC fetching when all URLs fail."""
        mock_try_urls.side_effect = Exception("All URLs failed")
        
        result = fetch_noaa_ncei_ohc_latest()
        
        assert result["year"] == "N/A"
        assert result["value"] == "N/A"
        assert result["units"] == ""


class TestSavePng:
    """Test cases for save_png function."""
    
    @patch('matplotlib.pyplot.close')
    def test_save_png(self, mock_close):
        """Test PNG saving functionality."""
        mock_fig = Mock()
        test_path = Path("test.png")
        
        save_png(mock_fig, test_path, dpi=200)
        
        # Methods are called on the figure object
        mock_fig.tight_layout.assert_called_once()
        mock_fig.savefig.assert_called_once_with(test_path, dpi=200, bbox_inches="tight")
        mock_close.assert_called_once_with(mock_fig)
