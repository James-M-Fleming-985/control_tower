# Analytics Integration Guide - Feedback360

## Overview

Feedback360 now has unified analytics integration with three leading platforms:
- **Google Analytics 4 (GA4)** - Core web analytics and conversion tracking
- **Mixpanel** - Product analytics and user behavior tracking
- **Amplitude** - User journey analysis and cohort tracking

All three platforms are initialized automatically when the app loads and provide a unified tracking interface.

## Setup

### 1. Environment Configuration

Add the following environment variables to your `.env` file:

```bash
# Analytics Platform API Keys
VITE_GA4_MEASUREMENT_ID=G-XXXXXXXXXX
VITE_MIXPANEL_TOKEN=your_mixpanel_project_token
VITE_AMPLITUDE_API_KEY=your_amplitude_api_key
```

**Important:** Replace the placeholder values with your actual API keys from each platform.

### 2. Getting API Keys

#### Google Analytics 4 (GA4)
1. Go to [Google Analytics](https://analytics.google.com/)
2. Create a new GA4 property
3. Copy the Measurement ID (format: `G-XXXXXXXXXX`)
4. Add to `.env` as `VITE_GA4_MEASUREMENT_ID`

#### Mixpanel
1. Go to [Mixpanel](https://mixpanel.com/)
2. Create a new project
3. Go to Project Settings → Access Keys
4. Copy the Project Token
5. Add to `.env` as `VITE_MIXPANEL_TOKEN`

#### Amplitude
1. Go to [Amplitude](https://amplitude.com/)
2. Create a new project
3. Go to Settings → Projects → [Your Project]
4. Copy the API Key
5. Add to `.env` as `VITE_AMPLITUDE_API_KEY`

## Architecture

### CDN-Based Loading

All three analytics platforms are loaded dynamically from their CDNs (no npm packages required):

- **GA4**: Loaded from `googletagmanager.com`
- **Mixpanel**: Loaded from `cdn.mxpnl.com`
- **Amplitude**: Loaded from `cdn.amplitude.com`

This approach:
- ✅ Eliminates npm dependency conflicts
- ✅ Reduces bundle size
- ✅ Allows runtime configuration via environment variables
- ✅ Provides better cache control

### File Structure

```
frontend/src/analytics/
├── index.ts              # Unified analytics interface
├── types.d.ts           # TypeScript declarations for window globals
├── ga4-config.js        # GA4 initialization and helpers
├── mixpanel-config.js   # Mixpanel initialization and helpers
└── amplitude-config.js  # Amplitude initialization and helpers
```

### Initialization Flow

1. **App Mount** (`App.tsx`):
   ```typescript
   useEffect(() => {
     initializeAnalytics();
   }, []);
   ```

2. **Platform Initialization** (`analytics/index.ts`):
   - Loads each platform's script from CDN
   - Initializes with API keys from environment variables
   - Sets default configuration
   - Logs initialization status

3. **Ready State**:
   - Each platform has an `isReady()` check
   - Events only sent to initialized platforms
   - Graceful degradation if a platform fails to load

## Usage

### Import Analytics Functions

```typescript
import { 
  trackEvent, 
  trackPageView, 
  identifyUser, 
  trackPurchase 
} from '../analytics';
```

### Track Events

```typescript
// Basic event tracking
trackEvent('button_clicked', {
  button_name: 'subscribe',
  location: 'hero_section'
});

// Feedback request created
trackEvent('feedback_request_created', {
  context: 'professional',
  mode: 'freetext',
  recipient_count: 5,
  request_id: 'req_123'
});
```

### Track Page Views

```typescript
useEffect(() => {
  trackPageView('/dashboard', 'User Dashboard');
}, []);
```

### Identify Users

```typescript
// When user signs up or logs in
identifyUser('user_123', {
  email: 'user@example.com',
  name: 'John Doe',
  subscription_tier: 'PRO',
  signup_date: '2024-01-15'
});
```

### Track Purchases/Subscriptions

```typescript
// When user upgrades to paid tier
trackPurchase(29.99, 'PRO', {
  billing_cycle: 'monthly',
  payment_method: 'stripe'
});
```

## Event Naming Conventions

### Standard Events

| Event Name | When to Track | Properties |
|-----------|---------------|------------|
| `page_view` | Page navigation | `page_path`, `page_title` |
| `user_signup` | Account creation | `signup_method`, `subscription_tier` |
| `user_login` | User authentication | `login_method` |
| `feedback_request_created` | New feedback request | `context`, `mode`, `recipient_count` |
| `feedback_response_submitted` | Feedback provided | `request_id`, `response_length` |
| `goal_survey_completed` | User completes goal survey | `primary_focus`, `secondary_focus` |
| `achievement_unlocked` | Gamification achievement | `achievement_name`, `achievement_tier` |
| `level_up` | User levels up | `new_level`, `total_points` |
| `subscription_upgrade` | Tier upgrade | `from_tier`, `to_tier`, `amount` |

### Event Properties Format

Use **snake_case** for all event names and properties:
- ✅ `feedback_request_created`
- ✅ `recipient_count`
- ❌ `FeedbackRequestCreated`
- ❌ `recipientCount`

## Example Implementation

### RequestPage with Analytics

```typescript
import { trackEvent, trackPageView } from '../analytics';

const RequestPage = () => {
  // Track page view on mount
  useEffect(() => {
    trackPageView('/request', 'Request Feedback');
  }, []);

  const handleSubmit = async () => {
    // Track submission attempt
    trackEvent('feedback_request_submitted', {
      context: context,
      mode: mode,
      recipient_count: emails.length
    });

    try {
      const response = await createRequest(data);
      
      // Track success
      trackEvent('feedback_request_created', {
        request_id: response.id,
        context: context,
        mode: mode
      });
    } catch (error) {
      // Track failure
      trackEvent('feedback_request_failed', {
        error: error.message
      });
    }
  };
};
```

### Landing Page with Conversion Tracking

```typescript
import { trackEvent } from '../analytics';

const Landing = () => {
  const handleCTAClick = () => {
    trackEvent('cta_clicked', {
      cta_text: 'Get Started',
      cta_location: 'hero'
    });
  };

  const handlePricingView = () => {
    trackEvent('pricing_viewed', {
      view_source: 'navigation_click'
    });
  };
};
```

## Analytics Dashboard Setup

### GA4 Custom Events

In your GA4 dashboard:
1. Go to **Configure** → **Events**
2. Click **Create Event**
3. Add custom events for key actions:
   - `feedback_request_created` → Mark as conversion
   - `subscription_upgrade` → Mark as conversion
   - `goal_survey_completed` → Mark as conversion

### Mixpanel Custom Properties

Set up custom properties for user profiles:
- `subscription_tier` (FREE/PRO/PREMIUM)
- `total_feedback_requests`
- `total_points`
- `current_level`
- `achievements_unlocked`

### Amplitude User Properties

Configure user properties for cohort analysis:
- `first_request_date`
- `last_activity_date`
- `subscription_tier`
- `lifetime_value`

## Privacy & Compliance

### GDPR Compliance

1. **Cookie Consent**: Implement cookie consent banner before initializing analytics
2. **User Data**: Allow users to opt-out of tracking
3. **Data Retention**: Configure retention periods in each platform

### Data Anonymization

```typescript
// Don't track PII directly
❌ trackEvent('user_data', { email: 'user@example.com' });

// Use anonymized IDs
✅ trackEvent('user_data', { user_id: 'user_123' });
```

## Debugging

### Check Initialization Status

Open browser console and run:

```javascript
// Check which platforms are loaded
console.log({
  GA4: !!window.gtag,
  Mixpanel: !!window.mixpanel,
  Amplitude: !!window.amplitude
});
```

### Enable Debug Mode

In development, all events are logged to console:

```
📊 Event tracked: feedback_request_created
{
  context: "professional",
  mode: "freetext",
  recipient_count: 3,
  timestamp: "2024-01-15T10:30:00.000Z"
}
```

### Test Events

Use each platform's debug view:
- **GA4**: DebugView in GA4 admin panel
- **Mixpanel**: Live View → Events tab
- **Amplitude**: User Lookup → Event Stream

## Performance Considerations

### Lazy Loading

Analytics scripts are loaded asynchronously and don't block page rendering:

```javascript
script.async = true;
script.defer = true;
```

### Bundle Size Impact

- **Before**: ~120KB from npm packages
- **After**: 0KB (CDN-loaded)
- **Runtime Cost**: ~3-5KB per platform (compressed)

### Network Requests

- Initial load: 3 script requests (one per platform)
- Event tracking: Batched and sent in background
- No impact on critical rendering path

## Troubleshooting

### Analytics Not Loading

**Problem**: Console shows "Analytics not initialized"

**Solutions**:
1. Check `.env` file has correct API keys
2. Verify keys are formatted correctly (no quotes in `.env`)
3. Restart dev server after changing `.env`
4. Check browser console for script loading errors

### Events Not Appearing

**Problem**: Events tracked but not visible in dashboards

**Solutions**:
1. **GA4**: Check DebugView (real-time, not historical)
2. **Mixpanel**: Use Live View for instant feedback
3. **Amplitude**: Check User Lookup → Event Stream
4. Wait 24-48 hours for historical data to process

### TypeScript Errors

**Problem**: `Property 'gtag' does not exist on type 'Window'`

**Solution**: Ensure `types.d.ts` is in `src/analytics/` folder and referenced in `tsconfig.json`

## Next Steps

1. **Set up conversion tracking** in GA4 for key events
2. **Create funnels** in Mixpanel for user journey analysis
3. **Build cohorts** in Amplitude for retention analysis
4. **Set up alerts** for critical metrics (signup rate, churn rate)
5. **Create dashboards** for daily monitoring

## Resources

- [GA4 Documentation](https://developers.google.com/analytics/devguides/collection/ga4)
- [Mixpanel JavaScript SDK](https://developer.mixpanel.com/docs/javascript)
- [Amplitude Browser SDK](https://www.docs.developers.amplitude.com/data/sdks/browser-2/)
- [Event Naming Best Practices](https://segment.com/academy/collecting-data/naming-conventions-for-clean-data/)
