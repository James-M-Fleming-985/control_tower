import React from 'react';

interface Feature {
  title: string;
  description: string;
  icon: string;
}

const Features: React.FC = () => {
  const features: Feature[] = [
    {
      title: "100% Anonymous",
      description: "Recipients provide feedback without revealing their identity. Complete privacy guaranteed.",
      icon: "🔒"
    },
    {
      title: "360° Perspective",
      description: "Collect feedback from colleagues, friends, mentors, and family for a complete view.",
      icon: "🎯"
    },
    {
      title: "Easy Requests",
      description: "Send invitation links via email. Recipients respond in minutes, no account needed.",
      icon: "⚡"
    }
  ];

  return (
    <section className="features-section" style={{
      padding: '5rem 2rem',
      backgroundColor: '#f9fafb'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <h2 style={{
          textAlign: 'center',
          fontSize: '2.5rem',
          marginBottom: '1rem',
          color: '#111827',
          fontWeight: 'bold'
        }}>
          Why Feedback360?
        </h2>
        <p style={{
          textAlign: 'center',
          fontSize: '1.1rem',
          color: '#6b7280',
          marginBottom: '3.5rem',
          maxWidth: '600px',
          margin: '0 auto 3.5rem'
        }}>
          Get the honest insights you need to grow, without the awkwardness
        </p>
        
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '2rem'
        }}>
          {features.map((feature, index) => (
            <div key={index} style={{
              backgroundColor: 'white',
              padding: '2.5rem',
              borderRadius: '12px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              textAlign: 'center',
              transition: 'all 0.3s',
              border: '1px solid #e5e7eb'
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px)';
              e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.1)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 1px 3px rgba(0,0,0,0.1)';
            }}
            >
              <div style={{ 
                fontSize: '3rem', 
                marginBottom: '1.5rem',
                filter: 'grayscale(0%)'
              }}>
                {feature.icon}
              </div>
              <h3 style={{
                fontSize: '1.5rem',
                marginBottom: '1rem',
                color: '#111827',
                fontWeight: '600'
              }}>
                {feature.title}
              </h3>
              <p style={{
                color: '#6b7280',
                lineHeight: '1.6',
                fontSize: '1rem'
              }}>
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;
