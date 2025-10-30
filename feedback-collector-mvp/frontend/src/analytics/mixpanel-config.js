/**
 * Mixpanel Analytics Configuration
 * 
 * App: Feedback360
 * Environment: production
 */

// Mixpanel Project Token (from environment variable)
export const MIXPANEL_TOKEN = import.meta.env.VITE_MIXPANEL_TOKEN || '';
export const MIXPANEL_DEBUG = import.meta.env.DEV || false;
export const APP_NAME = 'Feedback360';
export const ENVIRONMENT = import.meta.env.MODE || 'production';

let isInitialized = false;

/**
 * Initialize Mixpanel
 * Call this once in your app entry point (main.tsx or App.tsx)
 */
export function initializeMixpanel() {
  // Only initialize in browser environment
  if (typeof window === 'undefined') {
    return;
  }

  // Check if token is configured
  if (!MIXPANEL_TOKEN || MIXPANEL_TOKEN.length < 10) {
    console.warn('Mixpanel: Token not configured. Tracking disabled.');
    return;
  }

  // Avoid double initialization
  if (isInitialized) {
    return;
  }

  // Load Mixpanel library dynamically
  const script = document.createElement('script');
  script.src = 'https://cdn.mxpnl.com/libs/mixpanel-2-latest.min.js';
  script.async = true;
  script.onload = () => {
    if (window.mixpanel) {
      // Initialize Mixpanel
      window.mixpanel.init(MIXPANEL_TOKEN, {
        debug: MIXPANEL_DEBUG,
        track_pageview: false, // We'll track manually
        persistence: 'localStorage',
        ignore_dnt: false,
      });

      // Set super properties (sent with every event)
      window.mixpanel.register({
        app_name: APP_NAME,
        environment: ENVIRONMENT,
      });

      isInitialized = true;
      console.log(`✅ Mixpanel initialized`);
    }
  };
  document.head.appendChild(script);
}

/**
 * Check if Mixpanel is loaded and ready
 */
export function isMixpanelReady() {
  return isInitialized && typeof window !== 'undefined' && typeof window.mixpanel !== 'undefined';
}

/**
 * Get Mixpanel instance
 */
export function getMixpanel() {
  if (!isMixpanelReady()) {
    return null;
  }
  return window.mixpanel;
}

/**
 * Get current Mixpanel distinct ID
 */
export function getDistinctId() {
  const mp = getMixpanel();
  return mp ? mp.get_distinct_id() : null;
}

/**
 * Reset Mixpanel (logout)
 */
export function resetMixpanel() {
  const mp = getMixpanel();
  if (mp) {
    mp.reset();
  }
}
