"""
Unit tests for html_builder.py module.
"""

import pytest
from html_builder import (
    build_simple_tiles, build_details_tiles, build_projections_section,
    build_climate_solutions_section, build_sea_level_cities_section,
    build_css, build_javascript, build_html, SEA_LEVEL_2050_INCH, SCENARIO_LABEL
)


class TestBuildSimpleTiles:
    """Test cases for build_simple_tiles function."""
    
    def test_build_simple_tiles(self, sample_context):
        """Test simple tiles generation."""
        result = build_simple_tiles(sample_context)
        
        # Check that all expected tiles are present
        assert "CO₂ in the air" in result
        assert "425" in result  # CO₂ value
        assert "Sea level since 1993" in result
        assert "Arctic summer ice" in result
        assert "Oceans are the heat sponge" in result
        assert "Active forest fires" in result
        assert "15" in result  # Fire count
    
    def test_build_simple_tiles_with_nan_values(self):
        """Test simple tiles with NaN values."""
        context = {
            "co2": {"ppm": float('nan')},
            "nsidc": {"latest": {"extent_mkm2": float('nan')}},
            "fires": {"count": "N/A"}
        }
        
        result = build_simple_tiles(context)
        
        assert "—" in result  # NaN should be formatted as dash
        # N/A values are formatted as dash by fmt_num function


class TestBuildDetailsTiles:
    """Test cases for build_details_tiles function."""
    
    def test_build_details_tiles(self, sample_context):
        """Test details tiles generation."""
        result = build_details_tiles(sample_context)
        
        # Check that all expected detail cards are present
        assert "Atmospheric CO₂" in result
        assert "Met Éireann Warnings" in result
        assert "Arctic Sea Ice Extent" in result
        assert "Dublin Tide Gauge" in result
        assert "Ocean Heat Content" in result
        assert "Active Forest Fires" in result
        
        # Check for data values
        assert "425.48" in result  # CO₂ value
        assert "2" in result  # Warning count
        assert "12.5" in result  # Arctic ice extent
        assert "15.2" in result  # Ocean heat content
        assert "15" in result  # Fire count
    
    def test_build_details_tiles_with_missing_chart(self):
        """Test details tiles when chart is missing."""
        context = {
            "co2": {"year": 2024, "month": 12, "ppm": 425.48, "chart": "", "source": "test"},
            "warnings": {"count": 0, "titles": [], "source": "test"},
            "dublin": {"link": "test", "note": "test"},
            "nsidc": {"latest": {"date": "2024-12-01", "extent_mkm2": 12.5}, "chart": "", "source": "test"},
            "ohc": {"year": 2023, "value": 15.2, "units": "J", "source": "test"},
            "fires": {"count": 5, "source": "test", "description": "test"}
        }
        
        result = build_details_tiles(context)
        
        assert "Chart unavailable this run" in result


class TestBuildProjectionsSection:
    """Test cases for build_projections_section function."""
    
    def test_build_projections_section(self):
        """Test projections section generation."""
        result = build_projections_section()
        
        assert "Sea level projection" in result
        assert "Low" in result
        assert "Middle" in result
        assert "High" in result
        assert "Projection year" in result
        assert "2050" in result
        assert "IPCC" in result


class TestBuildClimateSolutionsSection:
    """Test cases for build_climate_solutions_section function."""
    
    def test_build_climate_solutions_section(self):
        """Test climate solutions section generation."""
        result = build_climate_solutions_section()
        
        assert "Climate Solutions & Innovations" in result
        assert "Carbon Nano Fiber Sheets" in result
        assert "Advanced Battery Storage" in result
        assert "Ocean Carbon Capture" in result
        assert "Regenerative Agriculture" in result
        
        # Check for research links
        assert "nature.com" in result
        assert "science.org" in result
        assert "acs.org" in result


class TestBuildSeaLevelCitiesSection:
    """Test cases for build_sea_level_cities_section function."""
    
    def test_build_sea_level_cities_section(self):
        """Test sea level cities section generation."""
        result = build_sea_level_cities_section()
        
        assert "Major Cities at Risk from Sea Level Rise" in result
        assert "Miami, Florida" in result
        assert "Dhaka, Bangladesh" in result
        assert "Amsterdam, Netherlands" in result
        assert "Jakarta, Indonesia" in result
        
        # Check for risk levels
        assert "High Risk" in result
        assert "Critical Risk" in result
        assert "Medium Risk" in result
        
        # Check for data sources
        assert "nasa.gov" in result
        assert "climatecentral.org" in result


class TestBuildCss:
    """Test cases for build_css function."""
    
    def test_build_css(self):
        """Test CSS generation."""
        result = build_css()
        
        # Check for key CSS elements
        assert ":root" in result
        assert "--primary" in result
        assert "--accent" in result
        assert "body" in result
        assert ".grid" in result
        assert ".tile" in result
        assert ".card" in result
        assert ".solutions-grid" in result
        assert ".cities-grid" in result
        assert ".zoomable" in result
        assert ".visit-counter" in result


class TestBuildJavascript:
    """Test cases for build_javascript function."""
    
    def test_build_javascript(self):
        """Test JavaScript generation."""
        result = build_javascript()
        
        # Check for key JavaScript functionality
        assert "addEventListener" in result
        assert "IntersectionObserver" in result
        assert "localStorage" in result
        assert "zoomable" in result
        assert "animateProjections" in result
        assert "updateSLR" in result


class TestBuildHtml:
    """Test cases for build_html function."""
    
    def test_build_html_structure(self, sample_context):
        """Test complete HTML generation."""
        result = build_html(sample_context)
        
        # Check HTML structure
        assert "<!DOCTYPE html>" in result
        assert "<html lang=\"en\">" in result
        assert "<head>" in result
        assert "<body>" in result
        assert "</body>" in result
        assert "</html>" in result
        
        # Check for key sections
        assert "Climate Now & to 2050" in result
        assert "Simple" in result
        assert "Details" in result
        assert "AdSense" in result
    
    def test_build_html_with_data(self, sample_context):
        """Test HTML generation with actual data."""
        result = build_html(sample_context)
        
        # Check that data is properly embedded
        assert "425.48" in result  # CO₂ value
        assert "2" in result  # Warning count
        assert "12.5" in result  # Arctic ice
        assert "15.2" in result  # Ocean heat
        assert "15" in result  # Fire count
    
    def test_build_html_sources(self, sample_context):
        """Test that all data sources are included."""
        result = build_html(sample_context)
        
        # Check for all source links
        assert "noaa.gov" in result
        assert "nsidc.org" in result
        assert "ncei.noaa.gov" in result
        assert "psmsl.org" in result
        assert "met.ie" in result
        assert "nasa.gov" in result


class TestConstants:
    """Test cases for module constants."""
    
    def test_sea_level_2050_inch_structure(self):
        """Test SEA_LEVEL_2050_INCH constant structure."""
        assert "low" in SEA_LEVEL_2050_INCH
        assert "mid" in SEA_LEVEL_2050_INCH
        assert "high" in SEA_LEVEL_2050_INCH
        
        # Check that all scenarios have tuples with 2 values
        for scenario in SEA_LEVEL_2050_INCH.values():
            assert isinstance(scenario, tuple)
            assert len(scenario) == 2
            assert all(isinstance(x, (int, float)) for x in scenario)
    
    def test_scenario_label_structure(self):
        """Test SCENARIO_LABEL constant structure."""
        assert "low" in SCENARIO_LABEL
        assert "mid" in SCENARIO_LABEL
        assert "high" in SCENARIO_LABEL
        
        # Check that all labels are strings
        for label in SCENARIO_LABEL.values():
            assert isinstance(label, str)
            assert len(label) > 0
