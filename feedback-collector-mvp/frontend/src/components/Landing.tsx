import React from 'react';
import Navbar from './Navbar';
import Hero from './Hero';
import Features from './Features';
import { trackCheckoutStarted } from '../analytics/events';
import { apiUrl } from '../config/api';
import { designSystem } from '../design/system';

const Landing: React.FC = () => {
  return (
    <div style={{ 
      minHeight: '100vh',
      backgroundColor: designSystem.colors.gray[50]
    }}>
      <Navbar />
      <Hero />
      <Features />
      
      {/* Pricing Section */}
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
            {/* Free Tier - Prompt Responses */}
            <div style={{
              backgroundColor: 'white',
              padding: '2rem',
              borderRadius: '12px',
              border: `2px solid ${designSystem.colors.gray[200]}`,
              transition: 'all 0.2s ease',
              position: 'relative',
              display: 'flex',
              flexDirection: 'column',
              height: '100%'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                marginBottom: '1rem'
              }}>
                <div style={{
                  width: '2.5rem',
                  height: '2.5rem',
                  backgroundColor: designSystem.colors.gray[100],
                  borderRadius: designSystem.borderRadius.lg,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <span style={{ fontSize: '1.25rem' }}>🎯</span>
                </div>
                <h3 style={{
                  fontSize: designSystem.typography.fontSize['2xl'],
                  fontWeight: designSystem.typography.fontWeight.bold,
                  color: designSystem.colors.gray[900],
                  margin: 0
                }}>
                  Starter
                </h3>
              </div>
              <div style={{ marginBottom: '2rem' }}>
                <span style={{
                  fontSize: 'clamp(2.5rem, 4vw, 3.5rem)',
                  fontWeight: designSystem.typography.fontWeight.bold,
                  color: designSystem.colors.gray[900]
                }}>
                  £0
                </span>
                <span style={{ 
                  color: designSystem.colors.gray[600],
                  fontSize: designSystem.typography.fontSize.lg
                }}>
                  /month
                </span>
              </div>
              <div style={{ flex: 1 }}>
                <ul style={{
                  listStyle: 'none',
                  padding: 0,
                  margin: 0,
                  marginBottom: '2rem'
                }}>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ 3 feedback requests per month</li>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ Up to 5 recipients each</li>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ <strong>Prompt-based responses</strong></li>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ Selected answer options</li>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ Basic analytics</li>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ Email notifications</li>
                </ul>
              </div>
              <a href="/request" style={{
                display: 'block',
                textAlign: 'center',
                padding: '0.75rem',
                backgroundColor: '#f3f4f6',
                color: '#111827',
                borderRadius: '8px',
                textDecoration: 'none',
                fontWeight: '600',
                transition: 'background-color 0.2s',
                marginTop: 'auto'
              }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#e5e7eb'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#f3f4f6'}
              >
                Get Started Free
              </a>
            </div>

            {/* Growth Tier - Limited Free Text */}
            <div style={{
              backgroundColor: 'white',
              padding: '2rem',
              borderRadius: '12px',
              border: `2px solid ${designSystem.colors.secondary[300]}`,
              transition: 'all 0.2s ease',
              position: 'relative',
              display: 'flex',
              flexDirection: 'column',
              height: '100%'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                marginBottom: '1rem'
              }}>
                <div style={{
                  width: '2.5rem',
                  height: '2.5rem',
                  background: `linear-gradient(135deg, ${designSystem.colors.secondary[400]} 0%, ${designSystem.colors.secondary[600]} 100%)`,
                  borderRadius: designSystem.borderRadius.lg,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <span style={{ fontSize: '1.25rem', color: 'white' }}>📈</span>
                </div>
                <h3 style={{
                  fontSize: designSystem.typography.fontSize['2xl'],
                  fontWeight: designSystem.typography.fontWeight.bold,
                  color: designSystem.colors.gray[900],
                  margin: 0
                }}>
                  Growth
                </h3>
              </div>
              <div style={{ marginBottom: '2rem' }}>
                <span style={{
                  fontSize: 'clamp(2.5rem, 4vw, 3.5rem)',
                  fontWeight: designSystem.typography.fontWeight.bold,
                  background: `linear-gradient(135deg, ${designSystem.colors.secondary[600]} 0%, ${designSystem.colors.secondary[400]} 100%)`,
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text'
                }}>
                  £4.99
                </span>
                <span style={{ 
                  color: designSystem.colors.gray[600],
                  fontSize: designSystem.typography.fontSize.lg
                }}>
                  /month
                </span>
              </div>
              <div style={{ flex: 1 }}>
                <ul style={{
                  listStyle: 'none',
                  padding: 0,
                  margin: 0,
                  marginBottom: '2rem'
                }}>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ 15 feedback requests per month</li>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ Up to 25 recipients each</li>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ <strong>Limited free-text responses</strong></li>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ Custom question templates</li>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ Enhanced analytics</li>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ PDF export</li>
                </ul>
              </div>
              <button
                onClick={async () => {
                  trackCheckoutStarted('growth');
                  
                  try {
                    const response = await fetch(apiUrl('/api/stripe/create-checkout-session'), {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                      },
                      body: JSON.stringify({
                        tier: 'growth',
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
                }}
                style={{
                  display: 'block',
                  width: '100%',
                  textAlign: 'center',
                  padding: '0.75rem',
                  background: `linear-gradient(135deg, ${designSystem.colors.secondary[500]} 0%, ${designSystem.colors.secondary[600]} 100%)`,
                  color: 'white',
                  borderRadius: '8px',
                  border: 'none',
                  fontWeight: '600',
                  fontSize: '1rem',
                  cursor: 'pointer',
                  boxShadow: '0 2px 8px rgba(6,182,212,0.3)',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  marginTop: 'auto'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(6,182,212,0.4)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(6,182,212,0.3)';
                }}
              >
                Choose Growth
              </button>
            </div>

            {/* Pro Tier - Unlimited Free Text - Featured */}
            <div style={{
              backgroundColor: 'white',
              padding: '2rem',
              borderRadius: '12px',
              border: '3px solid #3b82f6',
              boxShadow: '0 4px 12px rgba(59,130,246,0.2)',
              position: 'relative',
              display: 'flex',
              flexDirection: 'column',
              height: '100%'
            }}>
              <div style={{
                position: 'absolute',
                top: '-12px',
                left: '50%',
                transform: 'translateX(-50%)',
                background: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
                color: 'white',
                padding: '0.25rem 1rem',
                borderRadius: '12px',
                fontSize: '0.875rem',
                fontWeight: 'bold'
              }}>
                MOST POPULAR
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                marginBottom: '1rem'
              }}>
                <div style={{
                  width: '2.5rem',
                  height: '2.5rem',
                  background: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
                  borderRadius: designSystem.borderRadius.lg,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <span style={{ fontSize: '1.25rem', color: 'white' }}>🚀</span>
                </div>
                <h3 style={{
                  fontSize: designSystem.typography.fontSize['2xl'],
                  fontWeight: designSystem.typography.fontWeight.bold,
                  color: designSystem.colors.gray[900],
                  margin: 0
                }}>
                  Pro
                </h3>
              </div>
              <div style={{ marginBottom: '2rem' }}>
                <span style={{
                  fontSize: 'clamp(2.5rem, 4vw, 3.5rem)',
                  fontWeight: designSystem.typography.fontWeight.bold,
                  background: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text'
                }}>
                  £9.99
                </span>
                <span style={{ 
                  color: designSystem.colors.gray[600],
                  fontSize: designSystem.typography.fontSize.lg
                }}>
                  /month
                </span>
              </div>
              <div style={{ flex: 1 }}>
                <ul style={{
                  listStyle: 'none',
                  padding: 0,
                  margin: 0,
                  marginBottom: '2rem'
                }}>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ <strong>Unlimited</strong> feedback requests</li>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ <strong>Unlimited</strong> recipients</li>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ <strong>Unlimited free-text responses</strong></li>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ Complete insight into actual feedback</li>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ Advanced analytics & insights</li>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ Export to PDF/CSV/Excel</li>
                  <li style={{ padding: '0.5rem 0', color: '#4b5563' }}>✓ Priority support</li>
                </ul>
              </div>
              <button
                onClick={async () => {
                  trackCheckoutStarted('pro');
                  
                  try {
                    const response = await fetch(apiUrl('/api/stripe/create-checkout-session'), {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                      },
                      body: JSON.stringify({
                        tier: 'pro',
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
                }}
                style={{
                  display: 'block',
                  width: '100%',
                  textAlign: 'center',
                  padding: '0.75rem',
                  background: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
                  color: 'white',
                  borderRadius: '8px',
                  border: 'none',
                  fontWeight: '600',
                  fontSize: '1rem',
                  cursor: 'pointer',
                  boxShadow: '0 2px 8px rgba(59,130,246,0.3)',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  marginTop: 'auto'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(59,130,246,0.4)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(59,130,246,0.3)';
                }}
              >
                Upgrade to Pro
              </button>
            </div>
          </div>

          <div style={{
            textAlign: 'center',
            marginTop: '3rem',
            color: '#6b7280',
            fontSize: '0.95rem'
          }}>
            <p>All plans include 100% anonymous responses and secure data handling. Cancel anytime.</p>
          </div>
        </div>
      </section>
      
      {/* CTA Section with Gradient */}
      <section style={{
        padding: '4rem 2rem',
        background: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
        color: 'white'
      }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{
            fontSize: '2.5rem',
            marginBottom: '1rem',
            fontWeight: 'bold'
          }}>
            Ready to Get Started?
          </h2>
          <p style={{
            fontSize: '1.2rem',
            marginBottom: '2rem',
            opacity: 0.95,
            lineHeight: '1.6'
          }}>
            Create your first feedback request in under 2 minutes. No account needed to get started.
          </p>
          <a 
            href="/request"
            style={{
              display: 'inline-block',
              padding: '1rem 2.5rem',
              backgroundColor: 'white',
              color: '#3b82f6',
              fontSize: '1.1rem',
              fontWeight: '600',
              borderRadius: '8px',
              textDecoration: 'none',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              transition: 'transform 0.2s, box-shadow 0.2s'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 6px 20px rgba(0,0,0,0.2)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
            }}
          >
            Request Feedback Now →
          </a>
        </div>
      </section>
      
      {/* Footer */}
      <footer style={{
        padding: '2rem',
        backgroundColor: '#1f2937',
        color: '#9ca3af',
        textAlign: 'center',
        fontSize: '0.875rem'
      }}>
        <p style={{ margin: 0 }}>
          © 2025 Feedback360. All feedback is 100% anonymous and private.
        </p>
      </footer>
    </div>
  );
};

export default Landing;
