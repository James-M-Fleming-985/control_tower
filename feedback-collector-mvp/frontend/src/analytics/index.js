/**
 * Unified Analytics Configuration for Feedback360
 * Integrates GA4, Mixpanel, and Amplitude
 */

import { initializeGA4, isGA4Ready } from './ga4-config';
import { initializeMixpanel, isMixpanelReady } from './mixpanel-config';
import { initializeAmplitude, isAmplitudeReady } from './amplitude-config';

// Track initialization status
let analyticsInitialized = false;

/**
 * Initialize all analytics platforms
 * Call this once in your App.tsx or main entry point
 */
export function initializeAnalytics() {
  if (analyticsInitialized) {
    console.log('⚠️ Analytics already initialized');
    return;
  }

  console.log('🚀 Initializing Feedback360 Analytics...');

  // Initialize GA4
  try {
    initializeGA4();
  } catch (error) {
    console.error('GA4 initialization failed:', error);
  }

  // Initialize Mixpanel
  try {
    initializeMixpanel();
  } catch (error) {
    console.error('Mixpanel initialization failed:', error);
  }

  // Initialize Amplitude
  try {
    initializeAmplitude();
  } catch (error) {
    console.error('Amplitude initialization failed:', error);
  }

  analyticsInitialized = true;
  
  // Log status
  const status = {
    GA4: isGA4Ready(),
    Mixpanel: isMixpanelReady(),
    Amplitude: isAmplitudeReady()
  };
  
  console.log('📊 Analytics Status:', status);
}

/**
 * Track an event across all analytics platforms
 * 
 * @param {string} eventName - Name of the event
 * @param {object} properties - Event properties/parameters
 */
export function trackEvent(eventName, properties = {}) {
  // Add common properties
  const enrichedProperties = {
    ...properties,
    timestamp: new Date().toISOString(),
    app_name: 'Feedback360',
    platform: 'web'
  };

  // GA4
  if (isGA4Ready() && window.gtag) {
    window.gtag('event', eventName, enrichedProperties);
  }

  // Mixpanel
  if (isMixpanelReady() && window.mixpanel) {
    window.mixpanel.track(eventName, enrichedProperties);
  }

  // Amplitude
  if (isAmplitudeReady() && window.amplitude) {
    window.amplitude.track(eventName, enrichedProperties);
  }

  if (import.meta.env.DEV) {
    console.log('📊 Event tracked:', eventName, enrichedProperties);
  }
}

/**
 * Track page view across all platforms
 * 
 * @param {string} pagePath - Page path/URL
 * @param {string} pageTitle - Page title
 */
export function trackPageView(pagePath, pageTitle = '') {
  const properties = {
    page_path: pagePath,
    page_title: pageTitle || document.title,
    page_location: window.location.href
  };

  // GA4 automatically tracks pageviews, but we can send custom ones
  if (isGA4Ready() && window.gtag) {
    window.gtag('event', 'page_view', properties);
  }

  // Mixpanel
  if (isMixpanelReady() && window.mixpanel) {
    window.mixpanel.track('Page View', properties);
  }

  // Amplitude
  if (isAmplitudeReady() && window.amplitude) {
    window.amplitude.track('Page View', properties);
  }
}

/**
 * Identify user across all platforms
 * 
 * @param {string} userId - Unique user identifier
 * @param {object} userProperties - User properties
 */
export function identifyUser(userId, userProperties = {}) {
  // GA4 - Set user ID
  if (isGA4Ready() && window.gtag) {
    window.gtag('config', window.GA4_MEASUREMENT_ID, {
      user_id: userId
    });
    
    // Set user properties
    window.gtag('set', 'user_properties', userProperties);
  }

  // Mixpanel - Identify and set properties
  if (isMixpanelReady() && window.mixpanel) {
    window.mixpanel.identify(userId);
    window.mixpanel.people.set(userProperties);
  }

  // Amplitude - Identify and set properties
  if (isAmplitudeReady() && window.amplitude) {
    window.amplitude.setUserId(userId);
    
    const identify = new window.amplitude.Identify();
    Object.entries(userProperties).forEach(([key, value]) => {
      identify.set(key, value);
    });
    window.amplitude.identify(identify);
  }

  console.log('👤 User identified:', userId);
}

/**
 * Set user properties across all platforms
 * 
 * @param {object} properties - User properties to set
 */
export function setUserProperties(properties) {
  // GA4
  if (isGA4Ready() && window.gtag) {
    window.gtag('set', 'user_properties', properties);
  }

  // Mixpanel
  if (isMixpanelReady() && window.mixpanel) {
    window.mixpanel.people.set(properties);
  }

  // Amplitude
  if (isAmplitudeReady() && window.amplitude) {
    const identify = new window.amplitude.Identify();
    Object.entries(properties).forEach(([key, value]) => {
      identify.set(key, value);
    });
    window.amplitude.identify(identify);
  }
}

/**
 * Track conversion/goal completion
 * 
 * @param {string} goalName - Name of the goal
 * @param {number} value - Value of the conversion (optional)
 * @param {object} properties - Additional properties
 */
export function trackConversion(goalName, value = 0, properties = {}) {
  const conversionData = {
    ...properties,
    value: value,
    currency: 'GBP'
  };

  trackEvent('conversion', {
    goal_name: goalName,
    ...conversionData
  });

  // GA4 specific conversion event
  if (isGA4Ready() && window.gtag) {
    window.gtag('event', 'conversion', {
      send_to: window.GA4_MEASUREMENT_ID,
      ...conversionData
    });
  }
}

/**
 * Track revenue/purchase
 * 
 * @param {number} amount - Purchase amount
 * @param {string} tier - Subscription tier
 * @param {object} properties - Additional properties
 */
export function trackPurchase(amount, tier, properties = {}) {
  const purchaseData = {
    value: amount,
    currency: 'GBP',
    subscription_tier: tier,
    ...properties
  };

  // GA4 purchase event
  if (isGA4Ready() && window.gtag) {
    window.gtag('event', 'purchase', purchaseData);
  }

  // Mixpanel revenue tracking
  if (isMixpanelReady() && window.mixpanel) {
    window.mixpanel.track('Purchase', purchaseData);
    window.mixpanel.people.track_charge(amount);
  }

  // Amplitude revenue tracking
  if (isAmplitudeReady() && window.amplitude) {
    const revenue = new window.amplitude.Revenue()
      .setPrice(amount)
      .setProductId(tier)
      .setQuantity(1);
    window.amplitude.revenue(revenue);
  }
}

export default {
  initialize: initializeAnalytics,
  trackEvent,
  trackPageView,
  identifyUser,
  setUserProperties,
  trackConversion,
  trackPurchase
};
