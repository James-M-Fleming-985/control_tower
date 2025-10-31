import React, { useState, useEffect } from 'react';
import { apiUrl } from '../config/api';
import { designSystem } from '../design/system';
import { trackEvent } from '../analytics';

interface TierLimit {
  freetext_requests_per_month: number;
  prompted_requests_per_month: number;
  total_requests_per_month: number;
  recipients_per_request: number;
  feedback_history_days: number;
  goal_tracking: boolean;
  analytics_access: boolean;
  priority_support: boolean;
  export_reports?: boolean;
  api_access?: boolean;
  sso_enabled?: boolean;
  team_features?: boolean;
}

interface Tier {
  tier: string;
  name: string;
  tagline: string;
  price: number;
  currency: string;
  interval: string | null;
  features: string[];
  limits: TierLimit;
  is_popular: boolean;
  is_free: boolean;
}

const PricingSection: React.FC = () => {
  const [tiers, setTiers] = useState<Tier[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTiers();
  }, []);

  const fetchTiers = async () => {
    try {
      const response = await fetch(apiUrl('/api/stripe/tiers'));
      const data = await response.json();
      setTiers(data.tiers);
    } catch (error) {
      console.error('Failed to load pricing tiers:', error);
      // Fallback to hardcoded tiers
      setTiers(getDefaultTiers());
    } finally {
      setLoading(false);
    }
  };

  const getDefaultTiers = (): Tier[] => {
    return [
      {
        tier: 'free',
        name: 'Free',
        tagline: 'Perfect for trying out feedback',
        price: 0,
        currency: 'GBP',
        interval: null,
        features: [
          'Prompted feedback only',
          'Up to 3 feedback requests per month',
          'Basic feedback templates',
          'Email notifications',
          '7-day feedback history'
        ],
        limits: {
          freetext_requests_per_month: 0,
          prompted_requests_per_month: 3,
          total_requests_per_month: 3,
          recipients_per_request: 3,
          feedback_history_days: 7,
          goal_tracking: false,
          analytics_access: false,
          priority_support: false
        },
        is_popular: false,
        is_free: true
      },
      {
        tier: 'pro',
        name: 'Pro',
        tagline: 'For individuals serious about growth',
        price: 9.99,
        currency: 'GBP',
        interval: 'month',
        features: [
          '5 free-text feedback requests per month',
          'Unlimited prompted feedback',
          'Advanced feedback templates',
          'Goal alignment scoring',
          'Basic analytics dashboard',
          '30-day feedback history',
          'Email support'
        ],
        limits: {
          freetext_requests_per_month: 5,
          prompted_requests_per_month: -1,
          total_requests_per_month: -1,
          recipients_per_request: 10,
          feedback_history_days: 30,
          goal_tracking: true,
          analytics_access: true,
          priority_support: false
        },
        is_popular: true,
        is_free: false
      },
      {
        tier: 'premium',
        name: 'Premium',
        tagline: 'For professionals maximizing development',
        price: 24.99,
        currency: 'GBP',
        interval: 'month',
        features: [
          'Unlimited free-text feedback requests',
          'Unlimited prompted feedback',
          'All feedback templates',
          'Advanced goal alignment & tracking',
          'Comprehensive analytics dashboard',
          'Gamification & achievements',
          'Unlimited feedback history',
          'Priority email support',
          'Export feedback reports (PDF/CSV)'
        ],
        limits: {
          freetext_requests_per_month: -1,
          prompted_requests_per_month: -1,
          total_requests_per_month: -1,
          recipients_per_request: 25,
          feedback_history_days: -1,
          goal_tracking: true,
          analytics_access: true,
          priority_support: true,
          export_reports: true
        },
        is_popular: false,
        is_free: false
      }
    ];
  };

  const handleUpgrade = async (tier: Tier) => {
    if (tier.is_free) {
      window.location.href = '/request';
      return;
    }

    trackEvent('checkout_started', {
      tier: tier.tier,
      price: tier.price
    });

    try {
      const response = await fetch(apiUrl('/api/stripe/create-checkout-session'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tier: tier.tier,
          customer_email: ''
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to create checkout session: ${errorText}`);
      }

      const { checkout_url } = await response.json();
      window.location.href = checkout_url;
    } catch (error) {
      console.error('Checkout error:', error);
      alert('Unable to start checkout. Please try again.');
    }
  };

  const getTierIcon = (tierName: string): string => {
    const icons: Record<string, string> = {
      'Free': '🎯',
      'Pro': '🚀',
      'Premium': '💎',
      'Enterprise': '🏢'
    };
    return icons[tierName] || '📊';
  };

  const formatPrice = (price: number): string => {
    return price === 0 ? '£0' : `£${price.toFixed(2)}`;
  };

  if (loading) {
    return (
      <section id="pricing" style={{ padding: '6rem 0', backgroundColor: 'white' }}>
        <div style={{ textAlign: 'center', color: designSystem.colors.gray[600] }}>
          Loading pricing...
        </div>
      </section>
    );
  }

  return (
    <section id="pricing" style={{
      padding: '6rem 0',
      backgroundColor: 'white'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 2rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
          <h2 style={{
            fontSize: 'clamp(2rem, 4vw, 3rem)',
            fontWeight: designSystem.typography.fontWeight.bold,
            color: designSystem.colors.gray[900],
            marginBottom: '1rem',
            fontFamily: designSystem.typography.fontFamily.display.join(', ')
          }}>
            Choose Your{' '}
            <span style={{
              background: `linear-gradient(135deg, ${designSystem.colors.primary[600]} 0%, ${designSystem.colors.secondary[600]} 100%)`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              Growth Plan
            </span>
          </h2>
          <p style={{
            fontSize: designSystem.typography.fontSize.xl,
            color: designSystem.colors.gray[600],
            maxWidth: '36rem',
            margin: '0 auto'
          }}>
            Flexible pricing that scales with your feedback collection needs
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '2rem',
          maxWidth: '1200px',
          margin: '0 auto',
          alignItems: 'stretch'
        }}>
          {tiers.map((tier) => (
            <div
              key={tier.tier}
              style={{
                backgroundColor: 'white',
                padding: '2rem',
                borderRadius: '12px',
                border: tier.is_popular 
                  ? `2px solid ${designSystem.colors.primary[500]}`
                  : `2px solid ${designSystem.colors.gray[200]}`,
                transition: 'all 0.2s ease',
                position: 'relative',
                display: 'flex',
                flexDirection: 'column',
                height: '100%',
                boxShadow: tier.is_popular ? '0 8px 24px rgba(59, 130, 246, 0.15)' : 'none'
              }}
            >
              {tier.is_popular && (
                <div style={{
                  position: 'absolute',
                  top: '-12px',
                  right: '24px',
                  backgroundColor: designSystem.colors.primary[600],
                  color: 'white',
                  padding: '0.25rem 1rem',
                  borderRadius: '12px',
                  fontSize: designSystem.typography.fontSize.sm,
                  fontWeight: designSystem.typography.fontWeight.semibold
                }}>
                  Most Popular
                </div>
              )}

              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                marginBottom: '1rem'
              }}>
                <div style={{
                  width: '2.5rem',
                  height: '2.5rem',
                  background: tier.is_popular
                    ? `linear-gradient(135deg, ${designSystem.colors.primary[400]} 0%, ${designSystem.colors.primary[600]} 100%)`
                    : designSystem.colors.gray[100],
                  borderRadius: designSystem.borderRadius.lg,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <span style={{ fontSize: '1.25rem' }}>
                    {getTierIcon(tier.name)}
                  </span>
                </div>
                <h3 style={{
                  fontSize: designSystem.typography.fontSize['2xl'],
                  fontWeight: designSystem.typography.fontWeight.bold,
                  color: designSystem.colors.gray[900],
                  margin: 0
                }}>
                  {tier.name}
                </h3>
              </div>

              <p style={{
                color: designSystem.colors.gray[600],
                fontSize: designSystem.typography.fontSize.sm,
                marginBottom: '1.5rem'
              }}>
                {tier.tagline}
              </p>

              <div style={{ marginBottom: '2rem' }}>
                <span style={{
                  fontSize: 'clamp(2.5rem, 4vw, 3.5rem)',
                  fontWeight: designSystem.typography.fontWeight.bold,
                  color: tier.is_popular ? designSystem.colors.primary[600] : designSystem.colors.gray[900]
                }}>
                  {formatPrice(tier.price)}
                </span>
                <span style={{
                  color: designSystem.colors.gray[600],
                  fontSize: designSystem.typography.fontSize.lg
                }}>
                  {tier.interval ? `/${tier.interval}` : ''}
                </span>
              </div>

              <div style={{ flex: 1 }}>
                <ul style={{
                  listStyle: 'none',
                  padding: 0,
                  margin: 0,
                  marginBottom: '2rem'
                }}>
                  {tier.features.map((feature, index) => (
                    <li
                      key={index}
                      style={{
                        padding: '0.5rem 0',
                        color: designSystem.colors.gray[700],
                        fontSize: designSystem.typography.fontSize.sm,
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '0.5rem'
                      }}
                    >
                      <span style={{ color: designSystem.colors.primary[600], flexShrink: 0 }}>✓</span>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <button
                onClick={() => handleUpgrade(tier)}
                style={{
                  display: 'block',
                  width: '100%',
                  textAlign: 'center',
                  padding: '0.875rem',
                  background: tier.is_popular
                    ? `linear-gradient(135deg, ${designSystem.colors.primary[600]} 0%, ${designSystem.colors.primary[700]} 100%)`
                    : tier.is_free
                    ? designSystem.colors.gray[100]
                    : `linear-gradient(135deg, ${designSystem.colors.secondary[500]} 0%, ${designSystem.colors.secondary[600]} 100%)`,
                  color: tier.is_free ? designSystem.colors.gray[900] : 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: designSystem.typography.fontSize.base,
                  fontWeight: designSystem.typography.fontWeight.semibold,
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  marginTop: 'auto'
                }}
                onMouseOver={(e) => {
                  if (tier.is_popular) {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 8px 20px rgba(59, 130, 246, 0.3)';
                  } else if (tier.is_free) {
                    e.currentTarget.style.backgroundColor = designSystem.colors.gray[200];
                  } else {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 8px 20px rgba(6, 182, 212, 0.3)';
                  }
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                  if (tier.is_free) {
                    e.currentTarget.style.backgroundColor = designSystem.colors.gray[100];
                  }
                }}
              >
                {tier.is_free ? 'Get Started Free' : `Upgrade to ${tier.name}`}
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default PricingSection;
