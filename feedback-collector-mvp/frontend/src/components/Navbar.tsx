/**
 * Navigation Bar Component
 * Professional header matching app design
 */
import React from 'react';
import { designSystem } from '../design/system';

export const Navbar: React.FC = () => {
  return (
    <nav style={{
      position: 'sticky',
      top: 0,
      zIndex: 50,
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      backdropFilter: 'blur(10px)',
      borderBottom: `1px solid ${designSystem.colors.gray[200]}`,
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)'
    }}>
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        padding: '1rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        {/* Logo */}
        <a href="/" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          textDecoration: 'none'
        }}>
          <div style={{
            width: '2.5rem',
            height: '2.5rem',
            background: `linear-gradient(135deg, ${designSystem.colors.primary[500]} 0%, ${designSystem.colors.secondary[500]} 100%)`,
            borderRadius: designSystem.borderRadius.lg,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: designSystem.shadows.sm
          }}>
            <span style={{ fontSize: '1.25rem', color: 'white' }}>💬</span>
          </div>
          <span style={{
            fontSize: designSystem.typography.fontSize.xl,
            fontWeight: designSystem.typography.fontWeight.bold,
            background: `linear-gradient(135deg, ${designSystem.colors.primary[600]} 0%, ${designSystem.colors.secondary[600]} 100%)`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            fontFamily: designSystem.typography.fontFamily.display.join(', ')
          }}>
            Feedback360
          </span>
        </a>

        {/* Navigation Links */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '2rem'
        }}>
          <a
            href="#features"
            style={{
              fontSize: designSystem.typography.fontSize.base,
              color: designSystem.colors.gray[600],
              textDecoration: 'none',
              fontWeight: designSystem.typography.fontWeight.medium,
              transition: 'color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.color = designSystem.colors.primary[600]}
            onMouseOut={(e) => e.currentTarget.style.color = designSystem.colors.gray[600]}
          >
            Features
          </a>
          <a
            href="#pricing"
            style={{
              fontSize: designSystem.typography.fontSize.base,
              color: designSystem.colors.gray[600],
              textDecoration: 'none',
              fontWeight: designSystem.typography.fontWeight.medium,
              transition: 'color 0.2s'
            }}
            onMouseOver={(e) => e.currentTarget.style.color = designSystem.colors.primary[600]}
            onMouseOut={(e) => e.currentTarget.style.color = designSystem.colors.gray[600]}
          >
            Pricing
          </a>
          <a
            href="/request"
            style={{
              ...designSystem.components.button.primary,
              fontSize: designSystem.typography.fontSize.sm,
              padding: '0.625rem 1.5rem',
              textDecoration: 'none',
              display: 'inline-block'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.transform = 'translateY(-1px)';
              e.currentTarget.style.boxShadow = designSystem.shadows.md;
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = designSystem.shadows.sm;
            }}
          >
            Get Started
          </a>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
