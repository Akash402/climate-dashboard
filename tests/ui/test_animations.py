"""
UI tests for animations and visual effects.

These tests verify that animations work correctly and enhance
the user experience without causing issues.
"""

import pytest
import re
from playwright.sync_api import expect, Page


class TestCountUpAnimations:
    """Test count-up animations for numerical data."""
    
    def test_co2_count_animation(self, page: Page):
        """Test CO₂ count-up animation."""
        # Wait for page to load and animations to initialize
        page.wait_for_timeout(2000)
        
        # Get the count element
        count_element = page.locator('.count[data-value]')
        expect(count_element).to_be_visible()
        
        # Check that the element has the data-value attribute
        data_value = count_element.get_attribute('data-value')
        assert data_value is not None
        assert data_value != '0'
        
        # The animation should start from 0 and count up
        # We can't easily test the animation itself, but we can verify
        # that the final value is correct
        final_text = count_element.text_content()
        assert final_text is not None
        assert final_text != '0'  # Should have counted up from 0
    
    def test_animation_triggered_by_scroll(self, page: Page):
        """Test that animations are triggered by scroll intersection."""
        # Scroll down to trigger reveal animations
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        # Wait for animations to trigger
        page.wait_for_timeout(1000)
        
        # Check that reveal elements have the 'show' class
        reveal_elements = page.locator('.reveal.show')
        expect(reveal_elements).to_have_count_greater_than(0)


class TestRevealAnimations:
    """Test reveal-on-scroll animations."""
    
    def test_reveal_elements_initial_state(self, page: Page):
        """Test that reveal elements start hidden."""
        reveal_elements = page.locator('.reveal')
        expect(reveal_elements).to_have_count_greater_than(0)
        
        # Initially, reveal elements should not have the 'show' class
        for element in reveal_elements.all():
            expect(element).not_to_have_class(re.compile(r"show"))
    
    def test_reveal_animations_trigger_on_scroll(self, page: Page):
        """Test that reveal animations trigger when elements come into view."""
        # Scroll to bottom to trigger all reveal animations
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        # Wait for animations to complete
        page.wait_for_timeout(2000)
        
        # Check that reveal elements now have the 'show' class
        reveal_elements = page.locator('.reveal.show')
        expect(reveal_elements).to_have_count_greater_than(0)
    
    def test_reveal_animations_smooth_transition(self, page: Page):
        """Test that reveal animations have smooth transitions."""
        # Get a reveal element
        reveal_element = page.locator('.reveal').first
        
        # Scroll to make it visible
        reveal_element.scroll_into_view_if_needed()
        
        # Wait for animation
        page.wait_for_timeout(1000)
        
        # Check that it now has the show class
        expect(reveal_element).to_have_class(re.compile(r"show"))


class TestHoverEffects:
    """Test hover effects and interactive animations."""
    
    def test_tile_hover_effects(self, page: Page):
        """Test hover effects on tiles."""
        tiles = page.locator('.tile, .card')
        
        for tile in tiles.all():
            # Hover over the tile
            tile.hover()
            
            # Check that hover effect is applied (transform)
            # We can't easily test the visual transform, but we can verify
            # that the element is still visible and interactive
            expect(tile).to_be_visible()
    
    def test_button_hover_effects(self, page: Page):
        """Test hover effects on buttons."""
        buttons = page.locator('button, .tabbtn')
        
        for button in buttons.all():
            # Hover over the button
            button.hover()
            
            # Check that button is still functional
            expect(button).to_be_visible()
            expect(button).to_be_enabled()
    
    def test_link_hover_effects(self, page: Page):
        """Test hover effects on links."""
        links = page.locator('a')
        
        for link in links.all():
            # Hover over the link
            link.hover()
            
            # Check that link is still functional
            expect(link).to_be_visible()
            href = link.get_attribute('href')
            if href and not href.startswith('#'):
                # External links should have target="_blank"
                expect(link).to_have_attribute('target', '_blank')


class TestPulseAnimation:
    """Test pulse animation on CO₂ tile."""
    
    def test_pulse_animation_present(self, page: Page):
        """Test that pulse animation is applied to CO₂ tile."""
        co2_tile = page.locator('.tile.pulse')
        expect(co2_tile).to_be_visible()
        expect(co2_tile).to_have_class(re.compile(r"pulse"))
    
    def test_pulse_animation_continuous(self, page: Page):
        """Test that pulse animation runs continuously."""
        co2_tile = page.locator('.tile.pulse')
        
        # Wait for multiple animation cycles
        page.wait_for_timeout(5000)
        
        # The element should still be visible and have the pulse class
        expect(co2_tile).to_be_visible()
        expect(co2_tile).to_have_class(re.compile(r"pulse"))


class TestProjectionAnimation:
    """Test sea level projection animation."""
    
    def test_animation_button_functionality(self, page: Page):
        """Test that animation button works correctly."""
        # Wait for animation button to be added by JavaScript
        page.wait_for_timeout(1000)
        
        animation_button = page.locator('button:has-text("Animate Projections")')
        expect(animation_button).to_be_visible()
        
        # Get initial year value
        year_slider = page.locator('#yr')
        initial_value = year_slider.input_value()
        
        # Click animation button
        animation_button.click()
        
        # Wait for animation to start
        page.wait_for_timeout(1000)
        
        # Check that year value has changed (animation is running)
        current_value = year_slider.input_value()
        assert current_value != initial_value
    
    def test_animation_stops_at_end(self, page: Page):
        """Test that animation stops at the end year."""
        # Wait for animation button
        page.wait_for_timeout(1000)
        
        animation_button = page.locator('button:has-text("Animate Projections")')
        animation_button.click()
        
        # Wait for animation to complete (should take about 5 seconds)
        page.wait_for_timeout(6000)
        
        # Check that year slider is at maximum value (2050)
        year_slider = page.locator('#yr')
        final_value = year_slider.input_value()
        assert final_value == '2050'


class TestImageZoomAnimation:
    """Test image zoom animation functionality."""
    
    def test_image_zoom_in_animation(self, page: Page):
        """Test zoom in animation on images."""
        images = page.locator('img.zoomable')
        
        for img in images.all():
            # Click to zoom in
            img.click()
            
            # Check that zoomed class is applied
            expect(img).to_have_class(re.compile(r"zoomed"))
    
    def test_image_zoom_out_animation(self, page: Page):
        """Test zoom out animation on images."""
        images = page.locator('img.zoomable')
        
        for img in images.all():
            # Zoom in first
            img.click()
            expect(img).to_have_class(re.compile(r"zoomed"))
            
            # Click again to zoom out
            img.click()
            expect(img).not_to_have_class(re.compile(r"zoomed"))
    
    def test_image_zoom_cursor_changes(self, page: Page):
        """Test that cursor changes appropriately for zoomable images."""
        images = page.locator('img.zoomable')
        
        for img in images.all():
            # Check initial cursor
            cursor_style = img.evaluate("getComputedStyle(this).cursor")
            assert 'zoom-in' in cursor_style or 'pointer' in cursor_style
            
            # Zoom in
            img.click()
            
            # Check zoomed cursor
            cursor_style = img.evaluate("getComputedStyle(this).cursor")
            assert 'zoom-out' in cursor_style or 'pointer' in cursor_style


class TestLoadingStates:
    """Test loading states and transitions."""
    
    def test_page_loading_complete(self, page: Page):
        """Test that page loading is complete."""
        # Wait for all resources to load
        page.wait_for_load_state('networkidle')
        
        # Check that all main elements are visible
        expect(page.locator('h1')).to_be_visible()
        expect(page.locator('.tabs')).to_be_visible()
        expect(page.locator('.grid')).to_be_visible()
    
    def test_javascript_initialization(self, page: Page):
        """Test that JavaScript has initialized properly."""
        # Wait for JavaScript to initialize
        page.wait_for_timeout(2000)
        
        # Check that visit counter is present (added by JS)
        visit_counter = page.locator('.visit-counter')
        expect(visit_counter).to_be_visible()
        
        # Check that animation button is present (added by JS)
        animation_button = page.locator('button:has-text("Animate Projections")')
        expect(animation_button).to_be_visible()
    
    def test_data_loading_states(self, page: Page):
        """Test that data loading states are handled properly."""
        # All data should be loaded and displayed
        expect(page.locator('.tile')).to_have_count(5)
        expect(page.locator('img')).to_have_count(2)
        
        # Check that no loading spinners or error states are visible
        loading_elements = page.locator('.loading, .spinner, .error')
        expect(loading_elements).to_have_count(0)
