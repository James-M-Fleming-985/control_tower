import React from 'react';
import Hero from './Hero';
import Features from './Features';

const Landing: React.FC = () => {
  return (
    <div style={{ minHeight: '100vh' }}>
      <Hero />
      <Features />
      
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
