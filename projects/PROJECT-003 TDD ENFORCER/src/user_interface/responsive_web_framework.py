"""
Responsive Web Framework for Mobile-Friendly UI (Iteration 18)
Simplified PWA approach for 1-2 internal users.

Requirements covered:
- REQ-UI-001: Responsive Mobile Interface (Basic)
"""

from typing import Dict, Any, List
import json


class ResponsiveWebFramework:
    """
    Lightweight responsive web framework with basic PWA features.
    Simplified for internal use - no native apps needed.
    """

    def __init__(self):
        self.viewport_config = {
            "width": "device-width",
            "initial_scale": 1.0,
            "maximum_scale": 5.0,
            "user_scalable": True
        }
        self.breakpoints = {
            "mobile": 480,
            "tablet": 768,
            "desktop": 1024
        }
        self.service_worker_enabled = False

    def get_viewport_meta_tag(self) -> str:
        """Generate HTML viewport meta tag for responsive design."""
        attrs = [f'{key.replace("_", "-")}={value}'
                 for key, value in self.viewport_config.items()]
        return f'<meta name="viewport" content="{", ".join(attrs)}">'

    def get_responsive_css(self) -> str:
        """
        Generate basic CSS media queries for mobile responsiveness.
        Simple approach: stack on mobile, side-by-side on desktop.
        """
        return f"""
/* Base mobile-first styles */
.container {{
    width: 100%;
    padding: 10px;
    box-sizing: border-box;
}}

.responsive-grid {{
    display: flex;
    flex-direction: column;
    gap: 10px;
}}

/* Tablet and larger */
@media (min-width: {self.breakpoints['tablet']}px) {{
    .container {{
        padding: 20px;
        max-width: 90%;
        margin: 0 auto;
    }}

    .responsive-grid {{
        flex-direction: row;
        flex-wrap: wrap;
    }}

    .responsive-grid > * {{
        flex: 1 1 45%;
    }}
}}

/* Desktop */
@media (min-width: {self.breakpoints['desktop']}px) {{
    .container {{
        max-width: 1200px;
    }}

    .responsive-grid > * {{
        flex: 1 1 30%;
    }}
}}

/* Touch-friendly buttons */
.btn {{
    min-height: 44px;
    min-width: 44px;
    padding: 10px 20px;
    font-size: 16px;
}}
"""

    def generate_manifest(self, app_name: str = "TDD Enforcer") -> Dict[str, Any]:
        """
        Generate minimal PWA manifest.json for mobile home screen installation.
        """
        return {
            "name": app_name,
            "short_name": "TDD",
            "start_url": "/",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#007bff",
            "icons": [
                {
                    "src": "/icon-192.png",
                    "sizes": "192x192",
                    "type": "image/png"
                },
                {
                    "src": "/icon-512.png",
                    "sizes": "512x512",
                    "type": "image/png"
                }
            ]
        }

    def get_service_worker_registration(self) -> str:
        """
        Generate JavaScript for service worker registration.
        Enables basic offline capability.
        """
        return """
// Simple service worker registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js').then(function(registration) {
            console.log('ServiceWorker registered:', registration.scope);
        }, function(err) {
            console.log('ServiceWorker registration failed:', err);
        });
    });
}
"""

    def get_basic_service_worker(self, cache_name: str = "tdd-cache-v1") -> str:
        """
        Generate minimal service worker for offline functionality.
        Cache-first strategy for static assets.
        """
        return f"""
const CACHE_NAME = '{cache_name}';
const urlsToCache = [
    '/',
    '/static/css/main.css',
    '/static/js/main.js'
];

// Install - cache static assets
self.addEventListener('install', function(event) {{
    event.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {{
            return cache.addAll(urlsToCache);
        }})
    );
}});

// Fetch - serve from cache, fallback to network
self.addEventListener('fetch', function(event) {{
    event.respondWith(
        caches.match(event.request).then(function(response) {{
            return response || fetch(event.request);
        }})
    );
}});

// Activate - clean old caches
self.addEventListener('activate', function(event) {{
    event.waitUntil(
        caches.keys().then(function(cacheNames) {{
            return Promise.all(
                cacheNames.map(function(cacheName) {{
                    if (cacheName !== CACHE_NAME) {{
                        return caches.delete(cacheName);
                    }}
                }})
            );
        }})
    );
}});
"""

    def detect_device_type(self, user_agent: str) -> str:
        """
        Simple device detection based on user agent.
        Returns: 'mobile', 'tablet', or 'desktop'
        """
        user_agent_lower = user_agent.lower()

        mobile_keywords = ['mobile', 'android', 'iphone', 'ipod', 'blackberry',
                           'windows phone']
        tablet_keywords = ['ipad', 'tablet', 'kindle']

        if any(keyword in user_agent_lower for keyword in tablet_keywords):
            return "tablet"
        elif any(keyword in user_agent_lower for keyword in mobile_keywords):
            return "mobile"
        else:
            return "desktop"

    def enable_service_worker(self):
        """Enable PWA service worker for offline capability."""
        self.service_worker_enabled = True

    def is_pwa_enabled(self) -> bool:
        """Check if PWA features are enabled."""
        return self.service_worker_enabled

    def get_responsive_html_template(self, title: str = "TDD Enforcer") -> str:
        """
        Generate complete responsive HTML template skeleton.
        """
        manifest_link = (
            '<link rel="manifest" href="/manifest.json">'
            if self.service_worker_enabled else ''
        )
        sw_script = (
            f'<script>{self.get_service_worker_registration()}</script>'
            if self.service_worker_enabled else ''
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    {self.get_viewport_meta_tag()}
    <title>{title}</title>
    {manifest_link}
    <style>
        {self.get_responsive_css()}
    </style>
</head>
<body>
    <div class="container">
        <div class="responsive-grid">
            <!-- Content goes here -->
        </div>
    </div>
    {sw_script}
</body>
</html>"""
