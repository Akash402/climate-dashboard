#!/usr/bin/env python3
"""
Utility functions for the Climate Dashboard.

This module contains helper functions for formatting, HTTP requests,
and other common operations used throughout the dashboard.
"""

from __future__ import annotations
import io
from datetime import datetime, timezone
from pathlib import Path

import requests
import numpy as np


def http_get(url: str, timeout: int = 30, allow_redirects: bool = True) -> requests.Response:
    """
    Make an HTTP GET request with proper headers and error handling.
    
    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds
        allow_redirects: Whether to follow redirects
        
    Returns:
        Response object
        
    Raises:
        requests.RequestException: If the request fails
    """
    r = requests.get(url, timeout=timeout, allow_redirects=allow_redirects,
        headers={"User-Agent": "climate-dashboard/1.2 (+github actions)"})
    r.raise_for_status()
    return r


def try_urls(urls: list[str], timeout: int = 45, binary: bool = False) -> tuple[str, str | bytes]:
    """
    Try multiple URLs in sequence until one succeeds.
    
    Args:
        urls: List of URLs to try
        timeout: Request timeout in seconds
        binary: Whether to return binary content
        
    Returns:
        Tuple of (successful_url, content)
        
    Raises:
        RuntimeError: If all URLs fail
    """
    last_err = None
    for u in urls:
        try:
            r = http_get(u, timeout=timeout)
            return u, (r.content if binary else r.text)
        except Exception as e:
            last_err = e
            continue
    raise last_err if last_err else RuntimeError("No URLs tried")


def now_utc_str() -> str:
    """
    Get current UTC time as a formatted string.
    
    Returns:
        Formatted UTC timestamp string
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def fmt_num(val, nd: int = 2, default: str = "—") -> str:
    """
    Format a number with specified decimal places, handling None and NaN values.
    
    Args:
        val: Value to format
        nd: Number of decimal places
        default: Default string for invalid values
        
    Returns:
        Formatted number string
    """
    try:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return default
        if isinstance(val, (int, np.integer)):
            return f"{val}"
        return f"{float(val):.{nd}f}"
    except Exception:
        return default


def mm_to_inches(mm: float) -> float:
    """Convert millimeters to inches."""
    return mm / 25.4


def m_to_inches(m: float) -> float:
    """Convert meters to inches."""
    return m * 39.3701
