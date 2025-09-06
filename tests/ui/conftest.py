"""
Playwright configuration and fixtures for UI tests.
"""

import pytest
import subprocess
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


@pytest.fixture(scope="session")
def dashboard_server():
    """Start the dashboard server for testing."""
    # Build the dashboard first
    subprocess.run(["python", "build.py"], check=True)
    
    # Start a simple HTTP server
    process = subprocess.Popen(
        ["python", "-m", "http.server", "8000"],
        cwd="dist",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(2)
    
    yield "http://localhost:8000"
    
    # Cleanup
    process.terminate()
    process.wait()


@pytest.fixture(scope="session")
def browser():
    """Create a browser instance for testing."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def context(browser: Browser):
    """Create a browser context for each test."""
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    )
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext, dashboard_server: str):
    """Create a page for each test."""
    page = context.new_page()
    page.goto(dashboard_server)
    yield page
    page.close()


@pytest.fixture
def mobile_context(browser: Browser):
    """Create a mobile browser context for responsive testing."""
    context = browser.new_context(
        viewport={"width": 375, "height": 667},
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
    )
    yield context
    context.close()


@pytest.fixture
def mobile_page(mobile_context: BrowserContext, dashboard_server: str):
    """Create a mobile page for responsive testing."""
    page = mobile_context.new_page()
    page.goto(dashboard_server)
    yield page
    page.close()


@pytest.fixture
def tablet_context(browser: Browser):
    """Create a tablet browser context for responsive testing."""
    context = browser.new_context(
        viewport={"width": 768, "height": 1024},
        user_agent="Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
    )
    yield context
    context.close()


@pytest.fixture
def tablet_page(tablet_context: BrowserContext, dashboard_server: str):
    """Create a tablet page for responsive testing."""
    page = tablet_context.new_page()
    page.goto(dashboard_server)
    yield page
    page.close()
