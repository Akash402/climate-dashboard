"""
Integration tests for main build.py module.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import shutil

from build import main


class TestMainIntegration:
    """Integration tests for the main function."""
    
    @patch('build.fetch_noaa_co2_monthly')
    @patch('build.fetch_met_eireann_warnings')
    @patch('build.fetch_psmsl_dublin_note')
    @patch('build.fetch_nsidc_arctic_daily')
    @patch('build.fetch_noaa_ncei_ohc_latest')
    @patch('build.fetch_forest_fires_data')
    @patch('build.build_html')
    @patch('pathlib.Path.write_text')
    def test_main_success(self, mock_write_text, mock_build_html, mock_fetch_fires,
                         mock_fetch_ohc, mock_fetch_nsidc, mock_fetch_dublin,
                         mock_fetch_warnings, mock_fetch_co2):
        """Test successful main function execution."""
        # Mock all data fetchers
        mock_fetch_co2.return_value = {
            "year": 2024, "month": 12, "ppm": 425.48,
            "chart": "co2_24mo.png", "source": "https://gml.noaa.gov/ccgg/trends/"
        }
        mock_fetch_warnings.return_value = {
            "count": 2, "titles": ["Storm Warning"], "source": "https://www.met.ie/warnings"
        }
        mock_fetch_dublin.return_value = {
            "link": "https://psmsl.org/data/obtaining/stations/432.php",
            "note": "Dublin tide-gauge shows a gradual long-term rise."
        }
        mock_fetch_nsidc.return_value = {
            "latest": {"date": "2024-12-01", "extent_mkm2": 12.5},
            "chart": "arctic_extent_365d.png", "source": "https://nsidc.org/sea-ice-today"
        }
        mock_fetch_ohc.return_value = {
            "year": 2023, "value": 15.2, "units": "J × 10^22",
            "source": "https://www.ncei.noaa.gov/access/global-ocean-heat-content/"
        }
        mock_fetch_fires.return_value = {
            "count": 15, "source": "https://firms.modaps.eosdis.nasa.gov/",
            "description": "Active fires detected by VIIRS satellite in last 24 hours"
        }
        
        # Mock HTML generation
        mock_build_html.return_value = "<html>Test Dashboard</html>"
        
        # Run main function
        main()
        
        # Verify all fetchers were called
        mock_fetch_co2.assert_called_once()
        mock_fetch_warnings.assert_called_once()
        mock_fetch_dublin.assert_called_once()
        mock_fetch_nsidc.assert_called_once()
        mock_fetch_ohc.assert_called_once()
        mock_fetch_fires.assert_called_once()
        
        # Verify HTML was built and written
        mock_build_html.assert_called_once()
        mock_write_text.assert_called_once()
    
    @patch('build.fetch_noaa_co2_monthly')
    @patch('build.fetch_met_eireann_warnings')
    @patch('build.fetch_psmsl_dublin_note')
    @patch('build.fetch_nsidc_arctic_daily')
    @patch('build.fetch_noaa_ncei_ohc_latest')
    @patch('build.fetch_forest_fires_data')
    @patch('build.build_html')
    @patch('pathlib.Path.write_text')
    def test_main_with_errors(self, mock_write_text, mock_build_html, mock_fetch_fires,
                             mock_fetch_ohc, mock_fetch_nsidc, mock_fetch_dublin,
                             mock_fetch_warnings, mock_fetch_co2):
        """Test main function with some data fetchers failing."""
        # Mock successful fetchers
        mock_fetch_co2.return_value = {
            "year": 2024, "month": 12, "ppm": 425.48,
            "chart": "co2_24mo.png", "source": "https://gml.noaa.gov/ccgg/trends/"
        }
        mock_fetch_dublin.return_value = {
            "link": "https://psmsl.org/data/obtaining/stations/432.php",
            "note": "Dublin tide-gauge shows a gradual long-term rise."
        }
        
        # Mock failing fetchers
        mock_fetch_warnings.side_effect = Exception("Network error")
        mock_fetch_nsidc.side_effect = Exception("API error")
        mock_fetch_ohc.side_effect = Exception("Data error")
        mock_fetch_fires.side_effect = Exception("Fire API error")
        
        # Mock HTML generation
        mock_build_html.return_value = "<html>Test Dashboard</html>"
        
        # Run main function - should not raise exception
        main()
        
        # Verify all fetchers were called
        mock_fetch_co2.assert_called_once()
        mock_fetch_warnings.assert_called_once()
        mock_fetch_dublin.assert_called_once()
        mock_fetch_nsidc.assert_called_once()
        mock_fetch_ohc.assert_called_once()
        mock_fetch_fires.assert_called_once()
        
        # Verify HTML was still built and written
        mock_build_html.assert_called_once()
        mock_write_text.assert_called_once()
    
    @patch('build.fetch_noaa_co2_monthly')
    @patch('build.fetch_met_eireann_warnings')
    @patch('build.fetch_psmsl_dublin_note')
    @patch('build.fetch_nsidc_arctic_daily')
    @patch('build.fetch_noaa_ncei_ohc_latest')
    @patch('build.fetch_forest_fires_data')
    def test_main_context_structure(self, mock_fetch_fires, mock_fetch_ohc, mock_fetch_nsidc,
                                   mock_fetch_dublin, mock_fetch_warnings, mock_fetch_co2):
        """Test that main function creates proper context structure."""
        # Mock all data fetchers
        mock_fetch_co2.return_value = {"year": 2024, "month": 12, "ppm": 425.48, "chart": "", "source": ""}
        mock_fetch_warnings.return_value = {"count": 0, "titles": [], "source": ""}
        mock_fetch_dublin.return_value = {"link": "", "note": ""}
        mock_fetch_nsidc.return_value = {"latest": {"date": "", "extent_mkm2": 0}, "chart": "", "source": ""}
        mock_fetch_ohc.return_value = {"year": 2023, "value": 0, "units": "", "source": ""}
        mock_fetch_fires.return_value = {"count": 0, "source": "", "description": ""}
        
        # Mock build_html to capture context
        captured_context = {}
        def capture_context(context):
            captured_context.update(context)
            return "<html>Test</html>"
        
        with patch('build.build_html', side_effect=capture_context):
            main()
        
        # Verify context structure
        assert "co2" in captured_context
        assert "warnings" in captured_context
        assert "dublin" in captured_context
        assert "nsidc" in captured_context
        assert "ohc" in captured_context
        assert "fires" in captured_context
        
        # Verify each context item has expected structure
        assert "year" in captured_context["co2"]
        assert "count" in captured_context["warnings"]
        assert "link" in captured_context["dublin"]
        assert "latest" in captured_context["nsidc"]
        assert "value" in captured_context["ohc"]
        assert "count" in captured_context["fires"]


class TestMainErrorHandling:
    """Test cases for error handling in main function."""
    
    @patch('build.fetch_noaa_co2_monthly')
    @patch('build.fetch_met_eireann_warnings')
    @patch('build.fetch_psmsl_dublin_note')
    @patch('build.fetch_nsidc_arctic_daily')
    @patch('build.fetch_noaa_ncei_ohc_latest')
    @patch('build.fetch_forest_fires_data')
    @patch('build.build_html')
    @patch('pathlib.Path.write_text')
    def test_main_all_fetchers_fail(self, mock_write_text, mock_build_html, mock_fetch_fires,
                                   mock_fetch_ohc, mock_fetch_nsidc, mock_fetch_dublin,
                                   mock_fetch_warnings, mock_fetch_co2):
        """Test main function when all data fetchers fail."""
        # Mock all fetchers to fail
        mock_fetch_co2.side_effect = Exception("CO2 error")
        mock_fetch_warnings.side_effect = Exception("Warnings error")
        mock_fetch_nsidc.side_effect = Exception("NSIDC error")
        mock_fetch_ohc.side_effect = Exception("OHC error")
        mock_fetch_fires.side_effect = Exception("Fires error")
        
        # Mock HTML generation
        mock_build_html.return_value = "<html>Test Dashboard</html>"
        
        # Run main function - should not raise exception
        main()
        
        # Verify all fetchers were called
        mock_fetch_co2.assert_called_once()
        mock_fetch_warnings.assert_called_once()
        mock_fetch_dublin.assert_called_once()
        mock_fetch_nsidc.assert_called_once()
        mock_fetch_ohc.assert_called_once()
        mock_fetch_fires.assert_called_once()
        
        # Verify HTML was still built and written
        mock_build_html.assert_called_once()
        mock_write_text.assert_called_once()
    
    @patch('build.fetch_noaa_co2_monthly')
    @patch('build.fetch_met_eireann_warnings')
    @patch('build.fetch_psmsl_dublin_note')
    @patch('build.fetch_nsidc_arctic_daily')
    @patch('build.fetch_noaa_ncei_ohc_latest')
    @patch('build.fetch_forest_fires_data')
    @patch('build.build_html')
    def test_main_html_generation_fails(self, mock_build_html, mock_fetch_fires,
                                       mock_fetch_ohc, mock_fetch_nsidc, mock_fetch_dublin,
                                       mock_fetch_warnings, mock_fetch_co2):
        """Test main function when HTML generation fails."""
        # Mock all data fetchers to succeed
        mock_fetch_co2.return_value = {"year": 2024, "month": 12, "ppm": 425.48, "chart": "", "source": ""}
        mock_fetch_warnings.return_value = {"count": 0, "titles": [], "source": ""}
        mock_fetch_dublin.return_value = {"link": "", "note": ""}
        mock_fetch_nsidc.return_value = {"latest": {"date": "", "extent_mkm2": 0}, "chart": "", "source": ""}
        mock_fetch_ohc.return_value = {"year": 2023, "value": 0, "units": "", "source": ""}
        mock_fetch_fires.return_value = {"count": 0, "source": "", "description": ""}
        
        # Mock HTML generation to fail
        mock_build_html.side_effect = Exception("HTML generation error")
        
        # Run main function - should raise exception
        with pytest.raises(Exception, match="HTML generation error"):
            main()
