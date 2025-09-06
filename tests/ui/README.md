# UI Testing Suite for Climate Dashboard

This directory contains comprehensive end-to-end UI tests for the Climate Dashboard using Playwright. These tests ensure that the user interface works correctly across different browsers, devices, and scenarios.

## 🎭 Test Structure

```
tests/ui/
├── __init__.py
├── conftest.py              # Playwright configuration and fixtures
├── test_dashboard_ui.py     # Core dashboard functionality tests
├── test_animations.py       # Animation and visual effect tests
├── test_performance.py      # Performance and cross-browser tests
└── README.md               # This documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Playwright browsers installed (`playwright install`)
- Dashboard built (`python build.py`)

### Running UI Tests

#### Run All UI Tests
```bash
python -m pytest tests/ui/ -v
```

#### Run Specific Test Files
```bash
python -m pytest tests/ui/test_dashboard_ui.py -v
python -m pytest tests/ui/test_animations.py -v
python -m pytest tests/ui/test_performance.py -v
```

#### Run with Different Browsers
```bash
python -m pytest tests/ui/ --browser chromium -v
python -m pytest tests/ui/ --browser firefox -v
python -m pytest tests/ui/ --browser webkit -v
```

#### Run with Visual Debugging
```bash
python -m pytest tests/ui/ --headed -v          # Show browser
python -m pytest tests/ui/ --slowmo 1000 -v     # Slow motion
python -m pytest tests/ui/ --video on -v        # Record videos
python -m pytest tests/ui/ --screenshot on -v   # Take screenshots
```

#### Use the UI Test Runner
```bash
python run_ui_tests.py
```

## 📋 Test Categories

### 1. Core Dashboard Tests (`test_dashboard_ui.py`)

#### **Basic Functionality**
- Page loading and structure
- Tab navigation (Simple/Details)
- Data display accuracy
- AdSense integration

#### **Interactive Elements**
- Tab switching
- Sea level projection controls
- Chart zoom functionality
- Details expansion

#### **Content Sections**
- Climate solutions section
- Sea level cities section
- Visit counter functionality

#### **Responsive Design**
- Desktop layout (1280x720)
- Mobile layout (375x667)
- Tablet layout (768x1024)

#### **Accessibility**
- Keyboard navigation
- Screen reader compatibility
- Color contrast
- ARIA labels

### 2. Animation Tests (`test_animations.py`)

#### **Count-up Animations**
- CO₂ value counting animation
- Scroll-triggered animations

#### **Reveal Animations**
- Scroll-triggered element reveals
- Smooth transitions

#### **Hover Effects**
- Tile hover animations
- Button hover effects
- Link hover states

#### **Pulse Animation**
- CO₂ tile pulse effect
- Continuous animation

#### **Projection Animation**
- Sea level projection year animation
- Animation button functionality

#### **Image Zoom**
- Chart zoom in/out
- Cursor changes
- Zoom state management

### 3. Performance Tests (`test_performance.py`)

#### **Page Performance**
- Load time metrics
- DOM content loaded time
- Resource loading performance
- Memory usage

#### **Cross-browser Compatibility**
- Chromium, Firefox, WebKit
- CSS compatibility
- JavaScript functionality

#### **Mobile Performance**
- Mobile load times
- Touch interactions
- Viewport handling

#### **Error Handling**
- Network error recovery
- JavaScript error handling
- Missing data handling

## 🔧 Configuration

### Fixtures Available

#### **Browser Fixtures**
- `browser`: Main browser instance
- `context`: Browser context for each test
- `page`: Page instance for each test

#### **Device Fixtures**
- `mobile_context`: Mobile browser context (375x667)
- `mobile_page`: Mobile page instance
- `tablet_context`: Tablet browser context (768x1024)
- `tablet_page`: Tablet page instance

#### **Server Fixture**
- `dashboard_server`: HTTP server running the dashboard

### Test Configuration

Tests are configured in `conftest.py` with:
- Automatic dashboard building
- HTTP server setup
- Browser configuration
- Viewport settings
- User agent strings

## 📊 Test Coverage

### **UI Elements Tested**
- ✅ Page structure and layout
- ✅ Tab navigation system
- ✅ Data tiles and displays
- ✅ Interactive controls
- ✅ Charts and images
- ✅ Climate solutions section
- ✅ Sea level cities section
- ✅ Visit counter
- ✅ AdSense integration

### **Interactions Tested**
- ✅ Click events
- ✅ Hover effects
- ✅ Keyboard navigation
- ✅ Touch interactions (mobile)
- ✅ Scroll-triggered animations
- ✅ Form interactions

### **Browsers Tested**
- ✅ Chromium (primary)
- ✅ Firefox
- ✅ WebKit (Safari)

### **Devices Tested**
- ✅ Desktop (1280x720)
- ✅ Tablet (768x1024)
- ✅ Mobile (375x667)

## 🎯 Test Scenarios

### **Happy Path Scenarios**
1. User loads dashboard successfully
2. User switches between Simple and Details tabs
3. User interacts with sea level projections
4. User zooms into charts
5. User scrolls through all sections

### **Edge Cases**
1. Network failures during page load
2. JavaScript errors
3. Missing data scenarios
4. Slow network conditions
5. Different screen sizes

### **Accessibility Scenarios**
1. Keyboard-only navigation
2. Screen reader compatibility
3. High contrast mode
4. Reduced motion preferences

## 🚨 Common Issues and Solutions

### **Test Failures**

#### **Page Load Timeouts**
```bash
# Increase timeout
pytest tests/ui/ --timeout 30000
```

#### **Element Not Found**
- Check if element selectors are correct
- Verify element is visible and enabled
- Add appropriate waits

#### **Animation Timing Issues**
- Use `page.wait_for_timeout()` for animations
- Wait for specific conditions instead of fixed times

#### **Cross-browser Issues**
- Test on specific browsers
- Check CSS compatibility
- Verify JavaScript features

### **Debugging Tips**

#### **Visual Debugging**
```bash
# Run with browser visible
pytest tests/ui/ --headed

# Run with slow motion
pytest tests/ui/ --slowmo 1000

# Take screenshots on failure
pytest tests/ui/ --screenshot on
```

#### **Console Debugging**
```python
# Print page content
print(page.content())

# Print element text
print(element.text_content())

# Print element attributes
print(element.get_attribute('class'))
```

## 📈 Performance Benchmarks

### **Load Time Targets**
- Desktop: < 5 seconds
- Mobile: < 8 seconds
- DOM Ready: < 2 seconds

### **Memory Usage**
- < 50MB JavaScript heap
- < 100MB total memory

### **Animation Performance**
- 60fps for smooth animations
- < 100ms response time for interactions

## 🔄 CI/CD Integration

### **GitHub Actions Example**
```yaml
- name: Run UI Tests
  run: |
    python -m pytest tests/ui/ --browser chromium --video on
```

### **Local Development**
```bash
# Run tests before committing
python run_ui_tests.py

# Run specific test categories
python -m pytest tests/ui/ -m "not slow" -v
```

## 📚 Best Practices

### **Writing UI Tests**
1. Use descriptive test names
2. Test one thing per test
3. Use page object pattern for complex pages
4. Wait for conditions, not fixed times
5. Clean up after tests

### **Maintaining Tests**
1. Update selectors when UI changes
2. Keep tests independent
3. Use data attributes for test selectors
4. Document complex test scenarios

### **Performance Testing**
1. Run performance tests regularly
2. Monitor test execution time
3. Optimize slow tests
4. Use parallel execution when possible

## 🆘 Troubleshooting

### **Playwright Installation Issues**
```bash
# Reinstall Playwright
pip uninstall playwright
pip install playwright
playwright install
```

### **Browser Issues**
```bash
# Install specific browser
playwright install chromium
playwright install firefox
playwright install webkit
```

### **Permission Issues**
```bash
# Fix permissions
chmod +x run_ui_tests.py
```

## 📞 Support

For issues with UI tests:
1. Check this documentation
2. Review test logs and screenshots
3. Run tests with `--headed` for visual debugging
4. Check browser console for errors

## 🎉 Success Metrics

A successful UI test run should show:
- ✅ All tests passing
- ✅ No console errors
- ✅ Smooth animations
- ✅ Responsive design working
- ✅ Accessibility features functional
- ✅ Performance within targets

---

**Happy Testing! 🎭✨**
