"""
Tests for Responsive Web Framework (Iteration 18)
Simplified PWA approach for internal use.
"""

import pytest
import json
from src.user_interface.responsive_web_framework import ResponsiveWebFramework


class TestResponsiveWebFramework:
    """Test responsive web framework with basic PWA features."""

    def setup_method(self):
        """Setup test framework instance."""
        self.framework = ResponsiveWebFramework()

    def test_viewport_meta_tag_generation(self):
        """Test viewport meta tag for mobile responsiveness."""
        meta_tag = self.framework.get_viewport_meta_tag()

        assert '<meta name="viewport"' in meta_tag
        assert 'width=device-width' in meta_tag
        assert 'initial-scale=1.0' in meta_tag

    def test_responsive_css_includes_breakpoints(self):
        """Test CSS includes mobile/tablet/desktop breakpoints."""
        css = self.framework.get_responsive_css()

        assert '@media (min-width: 768px)' in css  # Tablet
        assert '@media (min-width: 1024px)' in css  # Desktop
        assert '.responsive-grid' in css
        assert 'flex-direction: column' in css  # Mobile-first

    def test_manifest_generation(self):
        """Test PWA manifest.json generation."""
        manifest = self.framework.generate_manifest("Test App")

        assert manifest['name'] == "Test App"
        assert manifest['short_name'] == "TDD"
        assert manifest['display'] == "standalone"
        assert len(manifest['icons']) == 2  # 192 and 512 sizes

    def test_manifest_json_serializable(self):
        """Test manifest can be serialized to JSON."""
        manifest = self.framework.generate_manifest()
        json_str = json.dumps(manifest)

        assert isinstance(json_str, str)
        assert '"name"' in json_str

    def test_service_worker_registration_code(self):
        """Test service worker registration JavaScript."""
        sw_reg = self.framework.get_service_worker_registration()

        assert 'serviceWorker' in sw_reg
        assert 'navigator.serviceWorker.register' in sw_reg
        assert '/sw.js' in sw_reg

    def test_basic_service_worker_code(self):
        """Test service worker code for offline capability."""
        sw_code = self.framework.get_basic_service_worker("test-cache")

        assert 'test-cache' in sw_code
        assert "addEventListener('install'" in sw_code
        assert "addEventListener('fetch'" in sw_code
        assert "addEventListener('activate'" in sw_code
        assert 'caches.open' in sw_code

    def test_device_detection_mobile(self):
        """Test mobile device detection."""
        mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
        device = self.framework.detect_device_type(mobile_ua)

        assert device == "mobile"

    def test_device_detection_tablet(self):
        """Test tablet device detection."""
        tablet_ua = "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)"
        device = self.framework.detect_device_type(tablet_ua)

        assert device == "tablet"

    def test_device_detection_desktop(self):
        """Test desktop device detection."""
        desktop_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/90.0"
        device = self.framework.detect_device_type(desktop_ua)

        assert device == "desktop"

    def test_pwa_disabled_by_default(self):
        """Test PWA features disabled by default."""
        assert not self.framework.is_pwa_enabled()

    def test_enable_service_worker(self):
        """Test enabling service worker."""
        self.framework.enable_service_worker()

        assert self.framework.is_pwa_enabled()

    def test_html_template_without_pwa(self):
        """Test HTML template without PWA features."""
        html = self.framework.get_responsive_html_template("Test")

        assert '<title>Test</title>' in html
        assert 'viewport' in html
        assert 'manifest.json' not in html  # PWA disabled
        assert 'serviceWorker' not in html

    def test_html_template_with_pwa(self):
        """Test HTML template with PWA features enabled."""
        self.framework.enable_service_worker()
        html = self.framework.get_responsive_html_template("Test")

        assert '<title>Test</title>' in html
        assert 'manifest.json' in html  # PWA enabled
        assert 'serviceWorker' in html

    def test_breakpoints_configuration(self):
        """Test default breakpoint configuration."""
        assert self.framework.breakpoints['mobile'] == 480
        assert self.framework.breakpoints['tablet'] == 768
        assert self.framework.breakpoints['desktop'] == 1024

    def test_touch_friendly_buttons_css(self):
        """Test CSS includes touch-friendly button sizes."""
        css = self.framework.get_responsive_css()

        assert '.btn' in css
        assert 'min-height: 44px' in css  # iOS recommended minimum
        assert 'min-width: 44px' in css
