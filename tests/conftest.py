"""
Pytest configuration and shared fixtures for climate dashboard tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_requests():
    """Mock requests module for testing HTTP calls."""
    with patch('requests.get') as mock_get:
        yield mock_get


@pytest.fixture
def sample_co2_data():
    """Sample CO₂ data for testing."""
    return {
        "year": 2024,
        "month": 12,
        "ppm": 425.48,
        "chart": "co2_24mo.png",
        "source": "https://gml.noaa.gov/ccgg/trends/"
    }


@pytest.fixture
def sample_fires_data():
    """Sample forest fires data for testing."""
    return {
        "count": 15,
        "source": "https://firms.modaps.eosdis.nasa.gov/",
        "description": "Active fires detected by VIIRS satellite in last 24 hours"
    }


@pytest.fixture
def sample_nsidc_data():
    """Sample NSIDC Arctic sea ice data for testing."""
    return {
        "latest": {"date": "2024-12-01", "extent_mkm2": 12.5},
        "chart": "arctic_extent_365d.png",
        "source": "https://nsidc.org/sea-ice-today"
    }


@pytest.fixture
def sample_context():
    """Sample context dictionary for testing HTML generation."""
    return {
        "co2": {
            "year": 2024, "month": 12, "ppm": 425.48,
            "chart": "co2_24mo.png", "source": "https://gml.noaa.gov/ccgg/trends/"
        },
        "warnings": {
            "count": 2, "titles": ["Storm Warning", "Flood Alert"],
            "source": "https://www.met.ie/warnings"
        },
        "dublin": {
            "link": "https://psmsl.org/data/obtaining/stations/432.php",
            "note": "Dublin tide-gauge shows a gradual long-term rise."
        },
        "nsidc": {
            "latest": {"date": "2024-12-01", "extent_mkm2": 12.5},
            "chart": "arctic_extent_365d.png",
            "source": "https://nsidc.org/sea-ice-today"
        },
        "ohc": {
            "year": 2023, "value": 15.2, "units": "J × 10^22",
            "source": "https://www.ncei.noaa.gov/access/global-ocean-heat-content/"
        },
        "fires": {
            "count": 15, "source": "https://firms.modaps.eosdis.nasa.gov/",
            "description": "Active fires detected by VIIRS satellite in last 24 hours"
        }
    }
