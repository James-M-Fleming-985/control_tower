import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { trackCheckoutCompleted } from '../analytics/events';

const SuccessPage: React.FC = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Get session_id from URL
    const params = new URLSearchParams(window.location.search);
    const sessionId = params.get('session_id');
    
    if (sessionId) {
      trackCheckoutCompleted(sessionId, 'pro');
    }
  }, []);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)' }}>
      <div style={{ maxWidth: '600px', padding: '3rem', backgroundColor: 'white', borderRadius: '16px', boxShadow: '0 8px 24px rgba(0,0,0,0.15)', textAlign: 'center' }}>
        <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🎉</div>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '1rem' }}>
          Welcome to Feedback360° Pro!
        </h1>
        <p style={{ fontSize: '1.2rem', color: '#6b7280', marginBottom: '2rem' }}>
          Your subscription is now active. You have unlimited access to all Pro features.
        </p>
        
        <div style={{ padding: '1.5rem', backgroundColor: '#f0f9ff', borderRadius: '8px', marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#0369a1', marginBottom: '0.5rem' }}>
            What's Next?
          </h3>
          <ul style={{ textAlign: 'left', color: '#0c4a6e', paddingLeft: '1.5rem' }}>
            <li>Create unlimited feedback requests</li>
            <li>Add as many recipients as you need</li>
            <li>Access your analytics dashboard</li>
            <li>Export your data anytime</li>
          </ul>
        </div>

        <button
          onClick={() => navigate('/request')}
          style={{
            width: '100%',
            padding: '1rem',
            background: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '1.1rem',
            fontWeight: 'bold',
            cursor: 'pointer',
            boxShadow: '0 2px 8px rgba(59,130,246,0.3)',
            transition: 'transform 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
          onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
        >
          Create Your First Request
        </button>
      </div>
    </div>
  );
};

export default SuccessPage;
