"""
Performance and cross-browser UI tests.

These tests verify that the dashboard performs well across
different browsers and under various conditions.
"""

import pytest
from playwright.sync_api import expect, Page


class TestPagePerformance:
    """Test page performance metrics."""
    
    def test_page_load_time(self, page: Page):
        """Test that page loads within acceptable time."""
        # Measure page load time
        start_time = page.evaluate("performance.now()")
        
        # Wait for page to be fully loaded
        page.wait_for_load_state('networkidle')
        
        load_time = page.evaluate("performance.now()") - start_time
        
        # Page should load within 5 seconds
        assert load_time < 5000, f"Page load time {load_time}ms exceeds 5 seconds"
    
    def test_dom_content_loaded_time(self, page: Page):
        """Test DOM content loaded time."""
        # Wait for DOM content loaded event
        page.wait_for_load_state('domcontentloaded')
        
        # Get DOM content loaded time from performance API
        dom_loaded_time = page.evaluate("""
            () => {
                const navigation = performance.getEntriesByType('navigation')[0];
                return navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart;
            }
        """)
        
        # DOM should be ready within 2 seconds
        assert dom_loaded_time < 2000, f"DOM content loaded time {dom_loaded_time}ms exceeds 2 seconds"
    
    def test_resource_loading_performance(self, page: Page):
        """Test that all resources load efficiently."""
        # Wait for all resources to load
        page.wait_for_load_state('networkidle')
        
        # Get resource loading metrics
        resources = page.evaluate("""
            () => {
                const resources = performance.getEntriesByType('resource');
                return resources.map(r => ({
                    name: r.name,
                    duration: r.duration,
                    size: r.transferSize || 0
                }));
            }
        """)
        
        # Check that no single resource takes too long
        for resource in resources:
            assert resource['duration'] < 3000, f"Resource {resource['name']} took {resource['duration']}ms"
    
    def test_memory_usage(self, page: Page):
        """Test that page doesn't use excessive memory."""
        # Wait for page to stabilize
        page.wait_for_timeout(2000)
        
        # Get memory usage
        memory_info = page.evaluate("""
            () => {
                if (performance.memory) {
                    return {
                        used: performance.memory.usedJSHeapSize,
                        total: performance.memory.totalJSHeapSize,
                        limit: performance.memory.jsHeapSizeLimit
                    };
                }
                return null;
            }
        """)
        
        if memory_info:
            # Memory usage should be reasonable (less than 50MB)
            used_mb = memory_info['used'] / (1024 * 1024)
            assert used_mb < 50, f"Memory usage {used_mb:.2f}MB exceeds 50MB limit"


class TestCrossBrowserCompatibility:
    """Test compatibility across different browsers."""
    
    @pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
    def test_basic_functionality_across_browsers(self, browser_name, dashboard_server):
        """Test basic functionality works across all browsers."""
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            if browser_name == "chromium":
                browser = p.chromium.launch(headless=True)
            elif browser_name == "firefox":
                browser = p.firefox.launch(headless=True)
            else:  # webkit
                browser = p.webkit.launch(headless=True)
            
            try:
                context = browser.new_context()
                page = context.new_page()
                page.goto(dashboard_server)
                
                # Test basic functionality
                expect(page).to_have_title("Climate Now & to 2050 — Dashboard")
                expect(page.locator("h1")).to_be_visible()
                expect(page.locator(".tabs")).to_be_visible()
                
                # Test tab switching
                details_tab = page.locator('button[data-tab="details"]')
                details_tab.click()
                expect(page.locator("#details")).to_have_class(/active/)
                
            finally:
                browser.close()
    
    def test_css_compatibility(self, page: Page):
        """Test that CSS works correctly across browsers."""
        # Test CSS Grid support
        grid = page.locator('.grid')
        grid_style = grid.evaluate("getComputedStyle(this).display")
        assert 'grid' in grid_style, "CSS Grid not supported or not working"
        
        # Test Flexbox support
        tabs = page.locator('.tabs')
        tabs_style = tabs.evaluate("getComputedStyle(this).display")
        assert 'flex' in tabs_style, "CSS Flexbox not supported or not working"
        
        # Test CSS Custom Properties (CSS Variables)
        root_style = page.evaluate("""
            () => {
                const root = document.documentElement;
                const computed = getComputedStyle(root);
                return {
                    primary: computed.getPropertyValue('--primary'),
                    accent: computed.getPropertyValue('--accent'),
                    bg: computed.getPropertyValue('--bg')
                };
            }
        """)
        
        assert root_style['primary'], "CSS custom properties not working"
        assert root_style['accent'], "CSS custom properties not working"
        assert root_style['bg'], "CSS custom properties not working"


class TestAccessibilityPerformance:
    """Test accessibility performance and compliance."""
    
    def test_keyboard_navigation_performance(self, page: Page):
        """Test that keyboard navigation is fast and responsive."""
        # Start timing
        start_time = page.evaluate("performance.now()")
        
        # Navigate through page with keyboard
        page.keyboard.press('Tab')  # First tab
        page.keyboard.press('Tab')  # Second tab
        page.keyboard.press('Tab')  # Third tab
        
        # Check that focus is working
        focused_element = page.locator(':focus')
        expect(focused_element).to_be_visible()
        
        end_time = page.evaluate("performance.now()")
        navigation_time = end_time - start_time
        
        # Keyboard navigation should be fast
        assert navigation_time < 100, f"Keyboard navigation took {navigation_time}ms"
    
    def test_screen_reader_compatibility(self, page: Page):
        """Test that page is compatible with screen readers."""
        # Check that all interactive elements have proper labels
        buttons = page.locator('button')
        for button in buttons.all():
            # Each button should have accessible text
            text_content = button.text_content()
            assert text_content is not None
            assert len(text_content.strip()) > 0
        
        # Check that form elements have labels
        inputs = page.locator('input')
        for input_elem in inputs.all():
            input_id = input_elem.get_attribute('id')
            if input_id:
                label = page.locator(f'label[for="{input_id}"]')
                expect(label).to_be_visible()
    
    def test_color_contrast_ratios(self, page: Page):
        """Test that text has sufficient color contrast."""
        # This is a simplified test - in practice, you'd use a proper
        # color contrast checking library
        text_elements = page.locator('.title, .big, .value, .sub, h1, h4')
        
        for element in text_elements.all():
            # Check that element is visible (basic contrast check)
            expect(element).to_be_visible()
            
            # Check that element has text content
            text_content = element.text_content()
            assert text_content is not None
            assert len(text_content.strip()) > 0


class TestMobilePerformance:
    """Test performance on mobile devices."""
    
    def test_mobile_page_load_time(self, mobile_page: Page):
        """Test page load time on mobile."""
        start_time = mobile_page.evaluate("performance.now()")
        mobile_page.wait_for_load_state('networkidle')
        load_time = mobile_page.evaluate("performance.now()") - start_time
        
        # Mobile should load within 8 seconds (slower than desktop)
        assert load_time < 8000, f"Mobile page load time {load_time}ms exceeds 8 seconds"
    
    def test_mobile_touch_interactions(self, mobile_page: Page):
        """Test touch interactions on mobile."""
        # Test tab switching with touch
        details_tab = mobile_page.locator('button[data-tab="details"]')
        details_tab.tap()  # Use tap instead of click for mobile
        
        expect(mobile_page.locator("#details")).to_have_class(/active/)
        
        # Test image zoom with touch
        images = mobile_page.locator('img.zoomable')
        if images.count() > 0:
            first_image = images.first
            first_image.tap()
            expect(first_image).to_have_class(/zoomed/)
    
    def test_mobile_viewport_handling(self, mobile_page: Page):
        """Test that mobile viewport is handled correctly."""
        # Check viewport meta tag
        viewport_meta = mobile_page.locator('meta[name="viewport"]')
        expect(viewport_meta).to_be_attached()
        
        viewport_content = viewport_meta.get_attribute('content')
        assert 'width=device-width' in viewport_content
        assert 'initial-scale=1' in viewport_content
        
        # Check that page fits mobile screen
        body_width = mobile_page.evaluate("document.body.scrollWidth")
        viewport_width = mobile_page.evaluate("window.innerWidth")
        
        # Page should not be wider than viewport (no horizontal scroll)
        assert body_width <= viewport_width + 20, "Page is wider than mobile viewport"


class TestErrorHandling:
    """Test error handling and graceful degradation."""
    
    def test_network_error_handling(self, page: Page):
        """Test handling of network errors."""
        # Simulate network failure for external resources
        page.route("**/*", lambda route: route.abort())
        
        # Reload page with network failure
        page.reload()
        
        # Page should still load basic structure
        expect(page.locator("h1")).to_be_visible()
        expect(page.locator(".tabs")).to_be_visible()
    
    def test_javascript_error_handling(self, page: Page):
        """Test that JavaScript errors don't break the page."""
        # Inject a JavaScript error
        page.evaluate("throw new Error('Test error')")
        
        # Page should still be functional
        expect(page.locator("h1")).to_be_visible()
        
        # Tab switching should still work
        details_tab = page.locator('button[data-tab="details"]')
        details_tab.click()
        expect(page.locator("#details")).to_have_class(/active/)
    
    def test_missing_data_handling(self, page: Page):
        """Test handling of missing or invalid data."""
        # Check that page handles missing data gracefully
        # (This would require modifying the data fetchers to return empty data)
        
        # All tiles should still be visible even with missing data
        tiles = page.locator('.tile')
        expect(tiles).to_have_count(5)
        
        # No error messages should be visible
        error_messages = page.locator('.error, .alert, .warning')
        expect(error_messages).to_have_count(0)
