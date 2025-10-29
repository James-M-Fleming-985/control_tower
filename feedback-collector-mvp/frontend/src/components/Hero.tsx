/**
 * Hero Section Component - Professional Rebranding
 * Updated with modern, professional design system
 */
import React from 'react';
import { designSystem } from '../design/system';

export const Hero: React.FC = () => {
  const handlePrimaryCTA = () => {
    window.location.href = '/request';
  };

  const handleSecondaryCTA = () => {
    document.querySelector('.features-section')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="relative overflow-hidden" style={{ 
      background: 'linear-gradient(135deg, #f8fafc 0%, #f0f9ff 50%, #faf5ff 100%)',
      minHeight: '85vh',
      display: 'flex',
      alignItems: 'center',
      paddingTop: '3rem',
      paddingBottom: '4rem'
    }}>
      {/* Background Pattern */}
      <div style={{
        position: 'absolute',
        inset: 0,
        backgroundImage: `radial-gradient(circle at 25% 25%, ${designSystem.colors.primary[100]} 0%, transparent 50%), 
                         radial-gradient(circle at 75% 75%, ${designSystem.colors.secondary[100]} 0%, transparent 50%)`,
        opacity: 0.3,
        zIndex: 0
      }} />
      
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="mx-auto max-w-4xl text-center">
          {/* Main Headline */}
          <h2 style={{
            fontSize: 'clamp(2.5rem, 5vw, 4rem)',
            lineHeight: '1.1',
            marginBottom: '1.5rem',
            color: designSystem.colors.gray[900],
            fontWeight: designSystem.typography.fontWeight.bold,
            fontFamily: designSystem.typography.fontFamily.display.join(', ')
          }}>
            Transform Your Growth with{' '}
            <span style={{
              background: `linear-gradient(135deg, ${designSystem.colors.primary[600]} 0%, ${designSystem.colors.secondary[600]} 100%)`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              Anonymous Feedback
            </span>
          </h2>

          {/* Subtitle */}
          <p style={{
            fontSize: designSystem.typography.fontSize.xl,
            lineHeight: '1.6',
            color: designSystem.colors.gray[600],
            marginBottom: '3rem',
            maxWidth: '42rem',
            margin: '0 auto 3rem auto'
          }}>
            Collect honest, actionable feedback from colleagues, clients, and teams. 
            Our enterprise-grade platform ensures complete anonymity while delivering 
            the insights you need for professional growth.
          </p>

          {/* CTA Buttons */}
          <div style={{
            display: 'flex',
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
            marginBottom: '4rem',
            flexWrap: 'wrap'
          }}>
            <button
              onClick={handlePrimaryCTA}
              style={{
                ...designSystem.components.button.primary,
                fontSize: designSystem.typography.fontSize.lg,
                padding: '1rem 2.5rem',
                boxShadow: designSystem.shadows.lg,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = designSystem.shadows.xl;
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = designSystem.shadows.lg;
              }}
            >
              <span>Start Collecting Feedback</span>
              <span style={{ fontSize: '1rem' }}>→</span>
            </button>
            
            <button
              onClick={handleSecondaryCTA}
              style={{
                ...designSystem.components.button.secondary,
                fontSize: designSystem.typography.fontSize.lg,
                padding: '1rem 2rem',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = designSystem.colors.gray[50];
                e.currentTarget.style.borderColor = designSystem.colors.gray[300];
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = 'white';
                e.currentTarget.style.borderColor = designSystem.colors.gray[200];
              }}
            >
              <span>See How It Works</span>
            </button>
          </div>

          {/* Trust Indicators */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '2rem',
            maxWidth: '900px',
            margin: '0 auto',
            padding: '2.5rem 2rem',
            backgroundColor: 'white',
            borderRadius: designSystem.borderRadius.xl,
            border: `1px solid ${designSystem.colors.gray[200]}`,
            boxShadow: designSystem.shadows.md
          }}>
            <div style={{ 
              textAlign: 'center',
              display: 'flex', 
              flexDirection: 'column',
              alignItems: 'center', 
              gap: '0.75rem' 
            }}>
              <div style={{
                width: '3.5rem',
                height: '3.5rem',
                backgroundColor: designSystem.colors.primary[50],
                borderRadius: designSystem.borderRadius.full,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.5rem'
              }}>🔒</div>
              <div>
                <h4 style={{ 
                  margin: 0, 
                  fontWeight: designSystem.typography.fontWeight.semibold,
                  color: designSystem.colors.gray[900],
                  fontSize: designSystem.typography.fontSize.base
                }}>
                  100% Anonymous
                </h4>
                <p style={{ 
                  margin: '0.25rem 0 0 0', 
                  fontSize: designSystem.typography.fontSize.sm,
                  color: designSystem.colors.gray[600]
                }}>
                  Complete privacy guaranteed
                </p>
              </div>
            </div>
            
            <div style={{ 
              textAlign: 'center',
              display: 'flex', 
              flexDirection: 'column',
              alignItems: 'center', 
              gap: '0.75rem' 
            }}>
              <div style={{
                width: '3.5rem',
                height: '3.5rem',
                backgroundColor: designSystem.colors.secondary[50],
                borderRadius: designSystem.borderRadius.full,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.5rem'
              }}>⚡</div>
              <div>
                <h4 style={{ 
                  margin: 0, 
                  fontWeight: designSystem.typography.fontWeight.semibold,
                  color: designSystem.colors.gray[900],
                  fontSize: designSystem.typography.fontSize.base
                }}>
                  2-Minute Setup
                </h4>
                <p style={{ 
                  margin: '0.25rem 0 0 0', 
                  fontSize: designSystem.typography.fontSize.sm,
                  color: designSystem.colors.gray[600]
                }}>
                  Start collecting today
                </p>
              </div>
            </div>
            
            <div style={{ 
              textAlign: 'center',
              display: 'flex', 
              flexDirection: 'column',
              alignItems: 'center', 
              gap: '0.75rem' 
            }}>
              <div style={{
                width: '3.5rem',
                height: '3.5rem',
                backgroundColor: designSystem.colors.success + '20',
                borderRadius: designSystem.borderRadius.full,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.5rem'
              }}>📊</div>
              <div>
                <h4 style={{ 
                  margin: 0, 
                  fontWeight: designSystem.typography.fontWeight.semibold,
                  color: designSystem.colors.gray[900],
                  fontSize: designSystem.typography.fontSize.base
                }}>
                  Actionable Insights
                </h4>
                <p style={{ 
                  margin: '0.25rem 0 0 0', 
                  fontSize: designSystem.typography.fontSize.sm,
                  color: designSystem.colors.gray[600]
                }}>
                  Data-driven growth
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;