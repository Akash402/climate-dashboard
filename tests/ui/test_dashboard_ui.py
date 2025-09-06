"""
End-to-end UI tests for the Climate Dashboard.

These tests verify the complete user experience including:
- Page loading and basic functionality
- Tab switching and navigation
- Data display accuracy
- Interactive elements
- Responsive design
- Animations and visual effects
"""

import pytest
import re
from playwright.sync_api import expect, Page


class TestDashboardBasicFunctionality:
    """Test basic dashboard functionality and page structure."""
    
    def test_page_loads_successfully(self, page: Page):
        """Test that the dashboard loads without errors."""
        # Check page title
        expect(page).to_have_title("Climate Now & to 2050 — Dashboard")
        
        # Check main heading
        expect(page.locator("h1")).to_contain_text("Climate Now & to 2050")
        
        # Check that the page has loaded completely
        expect(page.locator("body")).to_be_visible()
    
    def test_page_structure_elements(self, page: Page):
        """Test that all main page elements are present."""
        # Check header elements
        expect(page.locator(".header")).to_be_visible()
        expect(page.locator(".header h1")).to_be_visible()
        expect(page.locator(".header .sub")).to_be_visible()
        
        # Check tab navigation
        expect(page.locator(".tabs")).to_be_visible()
        expect(page.locator('button[data-tab="simple"]')).to_be_visible()
        expect(page.locator('button[data-tab="details"]')).to_be_visible()
        
        # Check main content sections
        expect(page.locator("#simple")).to_be_visible()
        expect(page.locator("#details")).to_be_visible()
        
        # Check sources section
        expect(page.locator(".sub")).to_contain_text("Sources:")
    
    def test_adsense_elements_present(self, page: Page):
        """Test that AdSense elements are present in the HTML."""
        # Check for AdSense script
        expect(page.locator('script[src*="googlesyndication.com"]')).to_be_attached()
        
        # Check for AdSense ad units
        expect(page.locator('.adsbygoogle')).to_have_count(2)  # Banner and footer ads
        
        # Check AdSense data attributes
        ads = page.locator('.adsbygoogle')
        expect(ads.first).to_have_attribute('data-ad-client')
        expect(ads.first).to_have_attribute('data-ad-slot')
        expect(ads.first).to_have_attribute('data-ad-format', 'auto')


class TestTabNavigation:
    """Test tab switching functionality."""
    
    def test_simple_tab_default_active(self, page: Page):
        """Test that Simple tab is active by default."""
        simple_tab = page.locator('button[data-tab="simple"]')
        details_tab = page.locator('button[data-tab="details"]')
        
        expect(simple_tab).to_have_class(re.compile(r"active"))
        expect(details_tab).not_to_have_class(re.compile(r"active"))
        
        expect(page.locator("#simple")).to_have_class(re.compile(r"active"))
        expect(page.locator("#details")).not_to_have_class(re.compile(r"active"))
    
    def test_tab_switching(self, page: Page):
        """Test switching between Simple and Details tabs."""
        simple_tab = page.locator('button[data-tab="simple"]')
        details_tab = page.locator('button[data-tab="details"]')
        
        # Click Details tab
        details_tab.click()
        
        # Check that Details tab is now active
        expect(details_tab).to_have_class(re.compile(r"active"))
        expect(simple_tab).not_to_have_class(re.compile(r"active"))
        
        # Check that Details section is visible
        expect(page.locator("#details")).to_have_class(re.compile(r"active"))
        expect(page.locator("#simple")).not_to_have_class(re.compile(r"active"))
        
        # Switch back to Simple tab
        simple_tab.click()
        
        # Check that Simple tab is active again
        expect(simple_tab).to_have_class(re.compile(r"active"))
        expect(details_tab).not_to_have_class(re.compile(r"active"))
        
        expect(page.locator("#simple")).to_have_class(re.compile(r"active"))
        expect(page.locator("#details")).not_to_have_class(re.compile(r"active"))


class TestDataDisplay:
    """Test data display accuracy and formatting."""
    
    def test_co2_data_display(self, page: Page):
        """Test CO₂ data is displayed correctly."""
        # Check CO₂ value is displayed
        co2_value = page.locator('.tile:has-text("CO₂ in the air") .big')
        expect(co2_value).to_be_visible()
        expect(co2_value).to_contain_text("ppm")
        
        # Check count-up animation data attribute
        count_element = page.locator('.count[data-value]')
        expect(count_element).to_be_attached()
        expect(count_element).to_have_attribute('data-value', re.compile(r'.+'))
    
    def test_sea_level_data_display(self, page: Page):
        """Test sea level data is displayed correctly."""
        sea_level_tile = page.locator('.tile:has-text("Sea level since 1993")')
        expect(sea_level_tile).to_be_visible()
        expect(sea_level_tile).to_contain_text("+3.6 inches")
        expect(sea_level_tile).to_contain_text("phone's thickness")
    
    def test_arctic_ice_data_display(self, page: Page):
        """Test Arctic ice data is displayed correctly."""
        arctic_tile = page.locator('.tile:has-text("Arctic summer ice")')
        expect(arctic_tile).to_be_visible()
        expect(arctic_tile).to_contain_text("million km²")
    
    def test_forest_fires_data_display(self, page: Page):
        """Test forest fires data is displayed correctly."""
        fires_tile = page.locator('.tile:has-text("Active forest fires")')
        expect(fires_tile).to_be_visible()
        expect(fires_tile).to_contain_text("fires")
        expect(fires_tile).to_contain_text("NASA satellites")
    
    def test_ocean_heat_data_display(self, page: Page):
        """Test ocean heat content data is displayed correctly."""
        ocean_tile = page.locator('.tile:has-text("Ocean heat content")')
        expect(ocean_tile).to_be_visible()
        expect(ocean_tile).to_contain_text("heat sponge")
        expect(ocean_tile).to_contain_text("2 km")


class TestInteractiveElements:
    """Test interactive elements and user interactions."""
    
    def test_details_expandable(self, page: Page):
        """Test that details elements can be expanded."""
        details_elements = page.locator('details summary')
        expect(details_elements).to_have_count(4)  # One for each tile
        
        # Click first details element
        first_details = details_elements.first
        first_details.click()
        
        # Check that details content is visible
        details_content = page.locator('details:has(> summary) > :not(summary)')
        expect(details_content.first).to_be_visible()
    
    def test_sea_level_projection_controls(self, page: Page):
        """Test sea level projection controls."""
        # Check radio buttons are present
        radio_buttons = page.locator('input[name="scn"]')
        expect(radio_buttons).to_have_count(3)  # Low, Mid, High
        
        # Check range slider is present
        year_slider = page.locator('#yr')
        expect(year_slider).to_be_visible()
        expect(year_slider).to_have_attribute('type', 'range')
        expect(year_slider).to_have_attribute('min', '2025')
        expect(year_slider).to_have_attribute('max', '2050')
        expect(year_slider).to_have_attribute('value', '2050')
    
    def test_sea_level_projection_interaction(self, page: Page):
        """Test sea level projection interaction."""
        # Get initial projection text
        projection_text = page.locator('#slr')
        initial_text = projection_text.text_content()
        
        # Change scenario to Low
        low_radio = page.locator('input[name="scn"][value="low"]')
        low_radio.click()
        
        # Check that projection text changed
        expect(projection_text).not_to_have_text(initial_text)
        expect(projection_text).to_contain_text("Low")
        
        # Change year slider
        year_slider = page.locator('#yr')
        year_slider.fill('2030')
        
        # Check that year changed in projection
        expect(projection_text).to_contain_text("2030")
    
    def test_animation_button_present(self, page: Page):
        """Test that animation button is present and functional."""
        # Wait for animation button to be added by JavaScript
        page.wait_for_timeout(1000)
        
        animation_button = page.locator('button:has-text("Animate Projections")')
        expect(animation_button).to_be_visible()
        
        # Click animation button
        animation_button.click()
        
        # Check that year slider value changes (animation is running)
        year_slider = page.locator('#yr')
        # Wait a bit for animation to start
        page.wait_for_timeout(500)
        # The value should have changed from 2050
        expect(year_slider).not_to_have_value('2050')


class TestChartsAndImages:
    """Test chart display and image functionality."""
    
    def test_charts_are_displayed(self, page: Page):
        """Test that charts are displayed correctly."""
        images = page.locator('img')
        expect(images).to_have_count(2)  # CO₂ chart and Arctic ice chart
        
        # Check chart images have proper attributes
        for img in images.all():
            expect(img).to_have_attribute('src')
            expect(img).to_have_attribute('alt')
    
    def test_chart_zoom_functionality(self, page: Page):
        """Test chart zoom functionality."""
        images = page.locator('img')
        
        # Check that images have zoomable class
        for img in images.all():
            expect(img).to_have_class(re.compile(r"zoomable"))
        
        # Click on first image to zoom
        first_image = images.first
        first_image.click()
        
        # Check that image has zoomed class
        expect(first_image).to_have_class(re.compile(r"zoomed"))
        
        # Click again to unzoom
        first_image.click()
        expect(first_image).not_to_have_class(re.compile(r"zoomed"))


class TestClimateSolutionsSection:
    """Test climate solutions section functionality."""
    
    def test_solutions_section_display(self, page: Page):
        """Test that climate solutions section is displayed."""
        solutions_section = page.locator('.solutions')
        expect(solutions_section).to_be_visible()
        expect(solutions_section).to_contain_text("Climate Solutions & Innovations")
    
    def test_solution_items_display(self, page: Page):
        """Test that all solution items are displayed."""
        solution_items = page.locator('.solution-item')
        expect(solution_items).to_have_count(4)
        
        # Check specific solutions
        expect(page.locator('.solution-item:has-text("Carbon Nano Fiber Sheets")')).to_be_visible()
        expect(page.locator('.solution-item:has-text("Advanced Battery Storage")')).to_be_visible()
        expect(page.locator('.solution-item:has-text("Ocean Carbon Capture")')).to_be_visible()
        expect(page.locator('.solution-item:has-text("Regenerative Agriculture")')).to_be_visible()
    
    def test_solution_links_functional(self, page: Page):
        """Test that solution links are functional."""
        solution_links = page.locator('.solution-links a')
        expect(solution_links).to_have_count(8)  # 2 links per solution
        
        # Check that links have proper href attributes
        for link in solution_links.all():
            expect(link).to_have_attribute('href')
            expect(link).to_have_attribute('target', '_blank')


class TestCitiesSection:
    """Test sea level cities section functionality."""
    
    def test_cities_section_display(self, page: Page):
        """Test that cities section is displayed."""
        cities_section = page.locator('.cities')
        expect(cities_section).to_be_visible()
        expect(cities_section).to_contain_text("Major Cities at Risk from Sea Level Rise")
    
    def test_city_items_display(self, page: Page):
        """Test that all city items are displayed."""
        city_items = page.locator('.city-item')
        expect(city_items).to_have_count(4)
        
        # Check specific cities
        expect(page.locator('.city-item:has-text("Miami, Florida")')).to_be_visible()
        expect(page.locator('.city-item:has-text("Dhaka, Bangladesh")')).to_be_visible()
        expect(page.locator('.city-item:has-text("Amsterdam, Netherlands")')).to_be_visible()
        expect(page.locator('.city-item:has-text("Jakarta, Indonesia")')).to_be_visible()
    
    def test_risk_badges_display(self, page: Page):
        """Test that risk badges are displayed correctly."""
        risk_badges = page.locator('.risk-high, .risk-critical, .risk-medium')
        expect(risk_badges).to_have_count(4)
        
        # Check specific risk levels
        expect(page.locator('.risk-high')).to_have_count(2)  # Miami and Jakarta
        expect(page.locator('.risk-critical')).to_have_count(1)  # Dhaka
        expect(page.locator('.risk-medium')).to_have_count(1)  # Amsterdam


class TestVisitCounter:
    """Test visit counter functionality."""
    
    def test_visit_counter_display(self, page: Page):
        """Test that visit counter is displayed."""
        # Wait for visit counter to be added by JavaScript
        page.wait_for_timeout(1000)
        
        visit_counter = page.locator('.visit-counter')
        expect(visit_counter).to_be_visible()
        expect(visit_counter).to_contain_text("Visit #")
        expect(visit_counter).to_contain_text("👥")
    
    def test_visit_counter_positioning(self, page: Page):
        """Test that visit counter is positioned correctly."""
        page.wait_for_timeout(1000)
        
        visit_counter = page.locator('.visit-counter')
        expect(visit_counter).to_have_css('position', 'fixed')
        expect(visit_counter).to_have_css('bottom', '20px')
        expect(visit_counter).to_have_css('right', '20px')


class TestResponsiveDesign:
    """Test responsive design across different screen sizes."""
    
    def test_desktop_layout(self, page: Page):
        """Test desktop layout elements."""
        # Check that grid layout is working
        grid = page.locator('.grid')
        expect(grid).to_be_visible()
        
        # Check that tiles are arranged in grid
        tiles = page.locator('.tile')
        expect(tiles).to_have_count(5)  # 5 tiles in simple view
    
    def test_mobile_layout(self, mobile_page: Page):
        """Test mobile layout and responsiveness."""
        # Check that page loads on mobile
        expect(mobile_page).to_have_title("Climate Now & to 2050 — Dashboard")
        
        # Check that tabs are still functional
        simple_tab = mobile_page.locator('button[data-tab="simple"]')
        details_tab = mobile_page.locator('button[data-tab="details"]')
        
        expect(simple_tab).to_be_visible()
        expect(details_tab).to_be_visible()
        
        # Test tab switching on mobile
        details_tab.click()
        expect(mobile_page.locator("#details")).to_have_class(re.compile(r"active"))
    
    def test_tablet_layout(self, tablet_page: Page):
        """Test tablet layout and responsiveness."""
        # Check that page loads on tablet
        expect(tablet_page).to_have_title("Climate Now & to 2050 — Dashboard")
        
        # Check that all sections are visible
        expect(tablet_page.locator('.solutions')).to_be_visible()
        expect(tablet_page.locator('.cities')).to_be_visible()
        
        # Check that grid adapts to tablet size
        grid = tablet_page.locator('.grid')
        expect(grid).to_be_visible()


class TestAccessibility:
    """Test accessibility features."""
    
    def test_keyboard_navigation(self, page: Page):
        """Test keyboard navigation through the page."""
        # Tab through interactive elements
        page.keyboard.press('Tab')
        page.keyboard.press('Tab')
        
        # Check that focus is on tab buttons
        focused_element = page.locator(':focus')
        expect(focused_element).to_be_visible()
    
    def test_alt_text_on_images(self, page: Page):
        """Test that images have proper alt text."""
        images = page.locator('img')
        
        for img in images.all():
            alt_text = img.get_attribute('alt')
            assert alt_text is not None
            assert len(alt_text) > 0
    
    def test_aria_labels_and_roles(self, page: Page):
        """Test ARIA labels and roles for screen readers."""
        # Check that form elements have proper labels
        radio_buttons = page.locator('input[name="scn"]')
        for radio in radio_buttons.all():
            # Each radio should be associated with a label
            radio_id = radio.get_attribute('id')
            if radio_id:
                label = page.locator(f'label[for="{radio_id}"]')
                expect(label).to_be_visible()
    
    def test_color_contrast(self, page: Page):
        """Test that text has sufficient color contrast."""
        # This would typically use a color contrast checking library
        # For now, we'll just check that text elements are visible
        text_elements = page.locator('.title, .big, .value, .sub')
        for element in text_elements.all():
            expect(element).to_be_visible()
            # Check that element has text content
            text_content = element.text_content()
            assert text_content is not None
            assert len(text_content.strip()) > 0
