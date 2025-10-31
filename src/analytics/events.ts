// Analytics event tracking
// Integrate with Mixpanel, GA4, and Amplitude

class Analytics {
  // Track event to all analytics providers
  track(event: string, properties?: Record<string, any>) {
    console.log(`[Analytics] ${event}`, properties);
    
    // Mixpanel
    if (typeof window !== 'undefined' && (window as any).mixpanel) {
      (window as any).mixpanel.track(event, properties);
    }
    
    // Google Analytics 4
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', event, properties);
    }
    
    // Amplitude
    if (typeof window !== 'undefined' && (window as any).amplitude) {
      (window as any).amplitude.track(event, properties);
    }
  }

  // Identify user (for authenticated flows)
  identify(userId: string, traits?: Record<string, any>) {
    console.log(`[Analytics] Identify ${userId}`, traits);
    
    if (typeof window !== 'undefined' && (window as any).mixpanel) {
      (window as any).mixpanel.identify(userId);
      if (traits) {
        (window as any).mixpanel.people.set(traits);
      }
    }
    
    if (typeof window !== 'undefined' && (window as any).amplitude) {
      (window as any).amplitude.setUserId(userId);
      if (traits) {
        (window as any).amplitude.setUserProperties(traits);
      }
    }
  }

  // Page view tracking
  page(pageName: string, properties?: Record<string, any>) {
    console.log(`[Analytics] Page: ${pageName}`, properties);
    
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'page_view', {
        page_title: pageName,
        ...properties
      });
    }
    
    if (typeof window !== 'undefined' && (window as any).mixpanel) {
      (window as any).mixpanel.track('Page Viewed', {
        page: pageName,
        ...properties
      });
    }
  }
}

export const analytics = new Analytics();

// Subscription-specific events
export const trackCheckoutStarted = (plan: string = 'pro') => {
  analytics.track('checkout_started', {
    plan,
    amount: 9.99,
    currency: 'GBP'
  });
};

export const trackCheckoutCompleted = (sessionId: string, plan: string = 'pro') => {
  analytics.track('checkout_completed', {
    session_id: sessionId,
    plan,
    amount: 9.99,
    currency: 'GBP'
  });
};

export const trackSubscriptionActive = (customerId: string, plan: string = 'pro') => {
  analytics.track('subscription_active', {
    customer_id: customerId,
    plan,
    amount: 9.99,
    currency: 'GBP'
  });
};

export const trackSubscriptionCancelled = (customerId: string) => {
  analytics.track('subscription_cancelled', {
    customer_id: customerId
  });
};

// Feedback-specific events
export const trackFeedbackRequested = (recipientCount: number, mode: string) => {
  analytics.track('feedback_requested', {
    recipient_count: recipientCount,
    mode
  });
};

export const trackFeedbackSubmitted = (mode: string) => {
  analytics.track('feedback_submitted', {
    mode
  });
};
