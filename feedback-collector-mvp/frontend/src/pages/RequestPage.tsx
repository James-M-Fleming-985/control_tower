import React, { useState } from 'react';

/**
 * RequestPage - Where users request feedback from others
 * This is the main user flow for creating a feedback request
 */
const RequestPage: React.FC = () => {
  const [context, setContext] = useState<'personal' | 'professional'>('professional');
  const [mode, setMode] = useState<'freetext' | 'objective'>('freetext');
  const [emails, setEmails] = useState<string[]>([]);
  const [emailInput, setEmailInput] = useState('');
  const [customMessage, setCustomMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const getObjectivePrompts = () => {
    if (context === 'professional') {
      return [
        "What are my strongest professional skills?",
        "Where do you see the biggest opportunity for my growth?",
        "How effectively do I communicate with the team?",
        "What's one thing I should start/stop/continue doing?",
        "How well do I handle challenging situations?"
      ];
    } else {
      return [
        "What do you appreciate most about our relationship?",
        "Is there anything I could do to be a better friend/partner/family member?",
        "How do you think I've grown in the past year?",
        "What's one thing you wish I understood better about you?",
        "How can I better support you?"
      ];
    }
  };

  const addEmail = () => {
    const trimmed = emailInput.trim();
    if (trimmed && trimmed.includes('@') && !emails.includes(trimmed)) {
      setEmails([...emails, trimmed]);
      setEmailInput('');
    }
  };

  const removeEmail = (email: string) => {
    setEmails(emails.filter(e => e !== email));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (emails.length === 0) {
      alert('Please add at least one recipient email');
      return;
    }

    setIsSubmitting(true);
    try {
      // TODO: API call to create feedback request and send emails
      console.log('Sending feedback request:', { context, mode, emails, customMessage });
      alert('Success! Invitations sent to ' + emails.length + ' recipient(s)');
      // Reset form
      setEmails([]);
      setCustomMessage('');
    } catch (error) {
      alert('Failed to send invitations. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f9fafb' }}>
      {/* Header */}
      <header style={{
        backgroundColor: 'white',
        borderBottom: '1px solid #e5e7eb',
        padding: '1rem 2rem',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
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
          <a href="/" style={{ 
            color: '#6b7280', 
            textDecoration: 'none', 
            fontSize: '0.95rem',
            transition: 'color 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.color = '#111827'}
          onMouseOut={(e) => e.currentTarget.style.color = '#6b7280'}
          >
            ← Back to Home
          </a>
        </div>
      </header>

      {/* Main Content */}
      <main style={{ maxWidth: '800px', margin: '3rem auto', padding: '0 2rem' }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '3rem',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          border: '1px solid #e5e7eb'
        }}>
          <h2 style={{ 
            fontSize: '2rem', 
            fontWeight: 'bold', 
            color: '#111827', 
            marginBottom: '0.5rem' 
          }}>
            Request Feedback
          </h2>
          <p style={{ color: '#6b7280', fontSize: '1rem', marginBottom: '2.5rem' }}>
            Send anonymous feedback requests to people who know you. They'll receive an email with a private link.
          </p>

          <form onSubmit={handleSubmit}>
            {/* Context Toggle */}
            <div style={{ marginBottom: '2rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.75rem',
                color: '#374151',
                fontWeight: '600',
                fontSize: '0.95rem'
              }}>
                Feedback Context
              </label>
              <div style={{
                display: 'flex',
                gap: '1rem',
                backgroundColor: '#f3f4f6',
                padding: '0.5rem',
                borderRadius: '8px'
              }}>
                <button
                  type="button"
                  onClick={() => setContext('professional')}
                  style={{
                    flex: 1,
                    padding: '0.75rem',
                    backgroundColor: context === 'professional' ? '#3b82f6' : 'transparent',
                    color: context === 'professional' ? 'white' : '#4b5563',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '0.95rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  💼 Professional
                </button>
                <button
                  type="button"
                  onClick={() => setContext('personal')}
                  style={{
                    flex: 1,
                    padding: '0.75rem',
                    backgroundColor: context === 'personal' ? '#3b82f6' : 'transparent',
                    color: context === 'personal' ? 'white' : '#4b5563',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '0.95rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  👤 Personal
                </button>
              </div>
            </div>

            {/* Mode Toggle */}
            <div style={{ marginBottom: '2rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.75rem',
                color: '#374151',
                fontWeight: '600',
                fontSize: '0.95rem'
              }}>
                Response Format
              </label>
              <div style={{
                display: 'flex',
                gap: '1rem',
                backgroundColor: '#f3f4f6',
                padding: '0.5rem',
                borderRadius: '8px'
              }}>
                <button
                  type="button"
                  onClick={() => setMode('freetext')}
                  style={{
                    flex: 1,
                    padding: '0.75rem',
                    backgroundColor: mode === 'freetext' ? '#06b6d4' : 'transparent',
                    color: mode === 'freetext' ? 'white' : '#4b5563',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '0.95rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  ✍️ Free Text
                </button>
                <button
                  type="button"
                  onClick={() => setMode('objective')}
                  style={{
                    flex: 1,
                    padding: '0.75rem',
                    backgroundColor: mode === 'objective' ? '#06b6d4' : 'transparent',
                    color: mode === 'objective' ? 'white' : '#4b5563',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '0.95rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  📋 Objective Prompts
                </button>
              </div>
              {mode === 'objective' && (
                <div style={{
                  marginTop: '1rem',
                  padding: '1rem',
                  backgroundColor: '#eff6ff',
                  borderRadius: '6px',
                  fontSize: '0.875rem',
                  color: '#1e40af'
                }}>
                  <strong>Recipients will be asked:</strong>
                  <ul style={{ margin: '0.5rem 0 0 1.5rem', padding: 0 }}>
                    {getObjectivePrompts().slice(0, 3).map((prompt, idx) => (
                      <li key={idx}>{prompt}</li>
                    ))}
                    <li><em>+ 2 more prompts</em></li>
                  </ul>
                </div>
              )}
            </div>

            {/* Email Recipients */}
            <div style={{ marginBottom: '2rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.75rem',
                color: '#374151',
                fontWeight: '600',
                fontSize: '0.95rem'
              }}>
                Recipients
              </label>
              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
                <input
                  type="email"
                  value={emailInput}
                  onChange={(e) => setEmailInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addEmail())}
                  placeholder="colleague@company.com"
                  style={{
                    flex: 1,
                    padding: '0.75rem',
                    border: '2px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '1rem'
                  }}
                />
                <button
                  type="button"
                  onClick={addEmail}
                  style={{
                    padding: '0.75rem 1.5rem',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '0.95rem',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  Add
                </button>
              </div>
              
              {/* Email chips */}
              {emails.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '1rem' }}>
                  {emails.map((email, idx) => (
                    <div key={idx} style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem',
                      padding: '0.5rem 0.75rem',
                      backgroundColor: '#e0f2fe',
                      borderRadius: '6px',
                      fontSize: '0.875rem',
                      color: '#075985'
                    }}>
                      <span>{email}</span>
                      <button
                        type="button"
                        onClick={() => removeEmail(email)}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: '#075985',
                          cursor: 'pointer',
                          fontSize: '1.2rem',
                          padding: 0,
                          lineHeight: 1
                        }}
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}
              
              <p style={{ fontSize: '0.875rem', color: '#6b7280', marginTop: '0.5rem' }}>
                {emails.length === 0 ? 'Add at least one email address' : `${emails.length} recipient(s) added`}
              </p>
            </div>

            {/* Custom Message */}
            <div style={{ marginBottom: '2rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.75rem',
                color: '#374151',
                fontWeight: '600',
                fontSize: '0.95rem'
              }}>
                Personal Message (Optional)
              </label>
              <textarea
                value={customMessage}
                onChange={(e) => setCustomMessage(e.target.value)}
                placeholder="Add a personal note to your invitation email..."
                rows={4}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '2px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '1rem',
                  resize: 'vertical'
                }}
                maxLength={500}
              />
              <div style={{
                textAlign: 'right',
                fontSize: '0.875rem',
                color: '#6b7280',
                marginTop: '0.25rem'
              }}>
                {customMessage.length}/500
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={isSubmitting || emails.length === 0}
              style={{
                width: '100%',
                padding: '1rem',
                background: (isSubmitting || emails.length === 0) ? '#9ca3af' : 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1.1rem',
                fontWeight: '600',
                cursor: (isSubmitting || emails.length === 0) ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s',
                boxShadow: (isSubmitting || emails.length === 0) ? 'none' : '0 4px 12px rgba(59, 130, 246, 0.3)'
              }}
              onMouseOver={(e) => {
                if (!isSubmitting && emails.length > 0) {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 6px 20px rgba(59, 130, 246, 0.4)';
                }
              }}
              onMouseOut={(e) => {
                if (!isSubmitting && emails.length > 0) {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(59, 130, 246, 0.3)';
                }
              }}
            >
              {isSubmitting ? 'Sending Invitations...' : `Send ${emails.length} Invitation${emails.length !== 1 ? 's' : ''}`}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
};

export default RequestPage;
