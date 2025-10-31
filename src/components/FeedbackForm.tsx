import React, { useState } from 'react';

interface FeedbackFormProps {
  onSubmit: (content: string, category: string) => Promise<void>;
}

const FeedbackForm: React.FC<FeedbackFormProps> = ({ onSubmit }) => {
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('general');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [context, setContext] = useState<'personal' | 'professional'>('professional');
  const [mode, setMode] = useState<'freetext' | 'objective'>('freetext');

  const getPlaceholder = () => {
    if (mode === 'freetext') {
      return context === 'professional' 
        ? "Share your thoughts on my work, communication style, or areas for improvement..."
        : "Share your honest perspective on our relationship, my growth, or anything you've noticed...";
    } else {
      return context === 'professional'
        ? "Select a prompt below to provide structured feedback..."
        : "Select a prompt below to share your perspective...";
    }
  };

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim()) {
      alert('Please enter your feedback');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(content, category);
      setContent('');
      setCategory('general');
    } catch (error) {
      alert('Failed to submit feedback. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section style={{
      padding: '4rem 2rem',
      background: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
      color: 'white'
    }}>
      <div style={{ maxWidth: '600px', margin: '0 auto' }}>
        <h2 style={{
          fontSize: '2.5rem',
          marginBottom: '1rem',
          textAlign: 'center'
        }}>
          Request Feedback
        </h2>
        <p style={{
          fontSize: '1.1rem',
          marginBottom: '2rem',
          textAlign: 'center',
          opacity: 0.9
        }}>
          Get honest insights from people who matter. Start with a demo request below.
        </p>

        <form onSubmit={handleSubmit} style={{
          backgroundColor: 'white',
          padding: '2rem',
          borderRadius: '12px',
          boxShadow: '0 8px 24px rgba(0,0,0,0.2)'
        }}>
          {/* Context Toggle */}
          <div style={{ marginBottom: '2rem' }}>
            <label style={{
              display: 'block',
              marginBottom: '0.75rem',
              color: '#2d3748',
              fontWeight: '600',
              fontSize: '0.95rem'
            }}>
              Feedback Context
            </label>
            <div style={{
              display: 'flex',
              gap: '1rem',
              backgroundColor: '#f7fafc',
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
                  color: context === 'professional' ? 'white' : '#4a5568',
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
                  color: context === 'personal' ? 'white' : '#4a5568',
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
              color: '#2d3748',
              fontWeight: '600',
              fontSize: '0.95rem'
            }}>
              Response Format
            </label>
            <div style={{
              display: 'flex',
              gap: '1rem',
              backgroundColor: '#f7fafc',
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
                  color: mode === 'freetext' ? 'white' : '#4a5568',
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
                  color: mode === 'objective' ? 'white' : '#4a5568',
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
          </div>

          {/* Objective Prompts (shown only in objective mode) */}
          {mode === 'objective' && (
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.5rem',
                color: '#2d3748',
                fontWeight: '600'
              }}>
                Select a Prompt
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '2px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '1rem'
                }}
              >
                {getObjectivePrompts().map((prompt, idx) => (
                  <option key={idx} value={`prompt-${idx}`}>{prompt}</option>
                ))}
              </select>
            </div>
          )}

          {/* Category (shown only in freetext mode) */}
          {mode === 'freetext' && (
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{
                display: 'block',
                marginBottom: '0.5rem',
                color: '#2d3748',
                fontWeight: '600'
              }}>
                Category (Optional)
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  border: '2px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '1rem'
                }}
              >
                <option value="general">General Feedback</option>
                <option value="strengths">Strengths</option>
                <option value="growth">Areas for Growth</option>
                <option value="communication">Communication</option>
                <option value="other">Other</option>
              </select>
            </div>
          )}

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{
              display: 'block',
              marginBottom: '0.5rem',
              color: '#2d3748',
              fontWeight: '600'
            }}>
              {mode === 'objective' ? 'Your Response' : 'Your Feedback'}
            </label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={getPlaceholder()}
              rows={6}
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '2px solid #e2e8f0',
                borderRadius: '8px',
                fontSize: '1rem',
                resize: 'vertical'
              }}
              maxLength={5000}
            />
            <div style={{
              textAlign: 'right',
              fontSize: '0.875rem',
              color: '#718096',
              marginTop: '0.25rem'
            }}>
              {content.length}/5000
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            style={{
              width: '100%',
              padding: '1rem',
              backgroundColor: isSubmitting ? '#a0aec0' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '1.1rem',
              fontWeight: '600',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseOver={(e) => {
              if (!isSubmitting) e.currentTarget.style.backgroundColor = '#2563eb';
            }}
            onMouseOut={(e) => {
              if (!isSubmitting) e.currentTarget.style.backgroundColor = '#3b82f6';
            }}
          >
            {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
          </button>
        </form>
      </div>
    </section>
  );
};

export default FeedbackForm;
