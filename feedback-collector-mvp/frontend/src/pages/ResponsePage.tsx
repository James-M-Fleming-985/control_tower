import React, { useState, useEffect } from 'react';

/**
 * ResponsePage - Anonymous feedback submission page
 * Recipients access this via a unique token link from their email
 */
const ResponsePage: React.FC = () => {
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [requestData, setRequestData] = useState({
    context: 'professional' as 'personal' | 'professional',
    mode: 'freetext' as 'freetext' | 'objective',
    requesterName: 'Someone', // TODO: Get from API
    prompts: [] as string[]
  });

  useEffect(() => {
    // TODO: Get token from URL and fetch request details from API
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    console.log('Token:', token);
    
    // Mock data - replace with API call
    setRequestData({
      context: 'professional',
      mode: 'freetext',
      requesterName: 'Your Colleague',
      prompts: []
    });
  }, []);

  const getPlaceholder = () => {
    if (requestData.mode === 'freetext') {
      return requestData.context === 'professional' 
        ? "Share your honest thoughts about their work, communication style, or areas for improvement..."
        : "Share your honest perspective about your relationship, their growth, or anything you've noticed...";
    }
    return "Share your response to the selected prompt above...";
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim()) {
      alert('Please enter your feedback');
      return;
    }

    setIsSubmitting(true);
    try {
      // TODO: API call to submit anonymous feedback
      console.log('Submitting feedback:', content);
      setIsSubmitted(true);
    } catch (error) {
      alert('Failed to submit feedback. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSubmitted) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        padding: '2rem'
      }}>
        <div style={{
          maxWidth: '500px',
          padding: '3rem',
          backgroundColor: 'white',
          borderRadius: '16px',
          boxShadow: '0 8px 32px rgba(0,0,0,0.15)',
          textAlign: 'center'
        }}>
          <div style={{ 
            fontSize: '4rem', 
            marginBottom: '1rem',
            animation: 'bounce 1s ease-in-out'
          }}>✅</div>
          <h2 style={{ 
            fontSize: '1.75rem', 
            fontWeight: 'bold', 
            color: '#111827', 
            marginBottom: '1rem' 
          }}>
            Thank You!
          </h2>
          <p style={{ color: '#6b7280', fontSize: '1rem', lineHeight: '1.6' }}>
            Your anonymous feedback has been submitted successfully. Your honest insights help people grow.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
      {/* Header */}
      <header style={{
        backgroundColor: 'white',
        borderBottom: '1px solid #e5e7eb',
        padding: '1rem 2rem',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h1 style={{ 
            fontSize: '1.75rem', 
            fontWeight: 'bold', 
            background: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            margin: 0,
            letterSpacing: '-0.02em',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0'
          }}>
            Feedback
            <span style={{ 
              position: 'relative',
              display: 'inline-flex',
              alignItems: 'center',
              marginLeft: '0.1em'
            }}>
              36
              <span style={{
                display: 'inline-block',
                width: '0.55em',
                height: '0.55em',
                border: '0.08em solid currentColor',
                borderRadius: '50%',
                position: 'relative',
                marginLeft: '-0.05em'
              }}>
                <span style={{
                  position: 'absolute',
                  top: '-0.12em',
                  right: '-0.12em',
                  width: '0.2em',
                  height: '0.2em',
                  borderTop: '0.08em solid currentColor',
                  borderRight: '0.08em solid currentColor',
                  transform: 'rotate(45deg)'
                }}></span>
              </span>
            </span>
          </h1>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '700px', margin: '3rem auto', padding: '0 2rem' }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '3rem',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          border: '1px solid #e5e7eb'
        }}>
          {/* Info Banner */}
          <div style={{
            padding: '1rem',
            backgroundColor: '#ecfdf5',
            borderLeft: '4px solid #10b981',
            borderRadius: '6px',
            marginBottom: '2rem'
          }}>
            <p style={{ fontSize: '0.875rem', color: '#065f46', margin: 0 }}>
              🔒 <strong>Your response is 100% anonymous.</strong> The requester will never know who provided this feedback.
            </p>
          </div>

          <h2 style={{ fontSize: '1.75rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>
            Feedback Request from {requestData.requesterName}
          </h2>
          <p style={{ color: '#6b7280', fontSize: '1rem', marginBottom: '2rem' }}>
            They're looking for {requestData.context} feedback to help them grow. Your honest perspective matters.
          </p>

          <form onSubmit={handleSubmit}>
            {/* Show prompt if objective mode */}
            {requestData.mode === 'objective' && requestData.prompts.length > 0 && (
              <div style={{ marginBottom: '2rem' }}>
                <label style={{
                  display: 'block',
                  marginBottom: '0.75rem',
                  color: '#374151',
                  fontWeight: '600',
                  fontSize: '0.95rem'
                }}>
                  Please Respond To:
                </label>
                <div style={{
                  padding: '1rem',
                  backgroundColor: '#f3f4f6',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  color: '#1f2937',
                  fontWeight: '500'
                }}>
                  {requestData.prompts[0]}
                </div>
              </div>
            )}

            {/* Feedback textarea */}
            <div style={{ marginBottom: '2rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.75rem',
                color: '#374151',
                fontWeight: '600',
                fontSize: '0.95rem'
              }}>
                Your Feedback
              </label>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder={getPlaceholder()}
                rows={8}
                style={{
                  width: '100%',
                  padding: '1rem',
                  border: '2px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  resize: 'vertical',
                  lineHeight: '1.6'
                }}
                maxLength={5000}
              />
              <div style={{
                textAlign: 'right',
                fontSize: '0.875rem',
                color: '#6b7280',
                marginTop: '0.5rem'
              }}>
                {content.length}/5000 characters
              </div>
            </div>

            {/* Tips */}
            <div style={{
              padding: '1rem',
              backgroundColor: '#f9fafb',
              borderRadius: '8px',
              marginBottom: '2rem'
            }}>
              <p style={{ fontSize: '0.875rem', color: '#4b5563', margin: '0 0 0.5rem 0', fontWeight: '600' }}>
                💡 Tips for helpful feedback:
              </p>
              <ul style={{ fontSize: '0.875rem', color: '#6b7280', margin: 0, paddingLeft: '1.5rem' }}>
                <li>Be specific with examples</li>
                <li>Focus on behaviors, not personality</li>
                <li>Balance constructive criticism with strengths</li>
                <li>Be honest but kind</li>
              </ul>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isSubmitting || !content.trim()}
              style={{
                width: '100%',
                padding: '1rem',
                background: (isSubmitting || !content.trim()) ? '#9ca3af' : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1.1rem',
                fontWeight: '600',
                cursor: (isSubmitting || !content.trim()) ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                boxShadow: (isSubmitting || !content.trim()) ? 'none' : '0 4px 12px rgba(16, 185, 129, 0.3)'
              }}
              onMouseOver={(e) => {
                if (!isSubmitting && content.trim()) {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 6px 20px rgba(16, 185, 129, 0.4)';
                }
              }}
              onMouseOut={(e) => {
                if (!isSubmitting && content.trim()) {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.3)';
                }
              }}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Anonymous Feedback'}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
};

export default ResponsePage;
