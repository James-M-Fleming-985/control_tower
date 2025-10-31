import React, { useState, useEffect } from 'react';
import { apiUrl } from '../config/api';
import { designSystem } from '../design/system';
import { trackEvent } from '../analytics';

interface UserData {
  id: number;
  email: string;
  name: string;
  subscription_tier: string;
  total_points: number;
  level: number;
  achievements: string[];
}

interface UsageData {
  tier: string;
  usage: {
    freetext_requests: number;
    prompted_requests: number;
    reset_date: string;
  };
  limits: {
    freetext_requests_per_month: number;
    prompted_requests_per_month: number;
    unlimited_freetext: boolean;
    unlimited_prompted: boolean;
  };
  remaining: {
    freetext_requests: number;
    prompted_requests: number;
  };
}

interface GoalData {
  leadership_score: number;
  communication_score: number;
  technical_skills_score: number;
  collaboration_score: number;
  innovation_score: number;
  reliability_score: number;
  primary_focus_area: string;
  secondary_focus_area: string;
}

const Dashboard: React.FC = () => {
  const [user, setUser] = useState<UserData | null>(null);
  const [usage, setUsage] = useState<UsageData | null>(null);
  const [goals, setGoals] = useState<GoalData | null>(null);
  const [loading, setLoading] = useState(true);

  // For demo purposes, using user_id = 1
  const userId = 1;

  useEffect(() => {
    fetchDashboardData();
    trackEvent('dashboard_viewed', { user_id: userId });
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch user data, usage stats, and goals in parallel
      const [userRes, usageRes, goalsRes] = await Promise.all([
        fetch(apiUrl(`/api/users/${userId}`)),
        fetch(apiUrl(`/api/usage/usage/${userId}`)),
        fetch(apiUrl(`/api/goals/${userId}`))
      ]);

      if (userRes.ok) {
        const userData = await userRes.json();
        setUser(userData);
      }

      if (usageRes.ok) {
        const usageData = await usageRes.json();
        setUsage(usageData);
      }

      if (goalsRes.ok) {
        const goalsData = await goalsRes.json();
        setGoals(goalsData);
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getLevelProgress = () => {
    if (!user) return 0;
    
    // Level thresholds (from gamification_service.py)
    const thresholds = [0, 100, 250, 500, 1000, 2000, 4000, 8000, 15000, 25000];
    const currentLevel = user.level;
    
    if (currentLevel >= thresholds.length) return 100;
    
    const currentThreshold = thresholds[currentLevel - 1];
    const nextThreshold = thresholds[currentLevel];
    const progress = ((user.total_points - currentThreshold) / (nextThreshold - currentThreshold)) * 100;
    
    return Math.min(100, Math.max(0, progress));
  };

  const getTierBadgeColor = (tier: string) => {
    const colors: Record<string, string> = {
      'free': designSystem.colors.gray[400],
      'pro': designSystem.colors.primary[500],
      'premium': designSystem.colors.secondary[500],
      'enterprise': '#8b5cf6'
    };
    return colors[tier.toLowerCase()] || designSystem.colors.gray[400];
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  const getUsagePercentage = (used: number, limit: number) => {
    if (limit === -1) return 0; // Unlimited
    if (limit === 0) return 100;
    return Math.min(100, (used / limit) * 100);
  };

  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return '#ef4444'; // red-500
    if (percentage >= 70) return '#f59e0b'; // yellow-500
    return '#10b981'; // green-500
  };

  const getGoalCompetencies = () => {
    if (!goals) return [];
    
    return [
      { name: 'Leadership', score: goals.leadership_score, key: 'leadership' },
      { name: 'Communication', score: goals.communication_score, key: 'communication' },
      { name: 'Technical Skills', score: goals.technical_skills_score, key: 'technical' },
      { name: 'Collaboration', score: goals.collaboration_score, key: 'collaboration' },
      { name: 'Innovation', score: goals.innovation_score, key: 'innovation' },
      { name: 'Reliability', score: goals.reliability_score, key: 'reliability' }
    ];
  };

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: designSystem.colors.gray[50]
      }}>
        <div style={{
          fontSize: designSystem.typography.fontSize.xl,
          color: designSystem.colors.gray[600]
        }}>
          Loading your dashboard...
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: designSystem.colors.gray[50],
      padding: '2rem'
    }}>
      {/* Header */}
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        marginBottom: '2rem'
      }}>
        <h1 style={{
          fontSize: 'clamp(2rem, 4vw, 3rem)',
          fontWeight: designSystem.typography.fontWeight.bold,
          color: designSystem.colors.gray[900],
          marginBottom: '0.5rem',
          fontFamily: designSystem.typography.fontFamily.display.join(', ')
        }}>
          Welcome back, {user?.name || 'there'}! 👋
        </h1>
        <p style={{
          fontSize: designSystem.typography.fontSize.lg,
          color: designSystem.colors.gray[600]
        }}>
          Track your growth, manage feedback, and achieve your professional goals
        </p>
      </div>

      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '2rem'
      }}>
        {/* Gamification Card */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '2rem',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          border: `1px solid ${designSystem.colors.gray[200]}`
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '1.5rem'
          }}>
            <h2 style={{
              fontSize: designSystem.typography.fontSize['2xl'],
              fontWeight: designSystem.typography.fontWeight.bold,
              color: designSystem.colors.gray[900],
              margin: 0
            }}>
              Your Progress
            </h2>
            <div style={{
              fontSize: 'clamp(2rem, 3vw, 3rem)'
            }}>
              🏆
            </div>
          </div>

          {/* Level Display */}
          <div style={{
            textAlign: 'center',
            marginBottom: '1.5rem',
            padding: '1.5rem',
            background: `linear-gradient(135deg, ${designSystem.colors.primary[500]} 0%, ${designSystem.colors.secondary[500]} 100%)`,
            borderRadius: '12px',
            color: 'white'
          }}>
            <div style={{
              fontSize: designSystem.typography.fontSize.sm,
              opacity: 0.9,
              marginBottom: '0.5rem'
            }}>
              Current Level
            </div>
            <div style={{
              fontSize: 'clamp(3rem, 5vw, 4rem)',
              fontWeight: designSystem.typography.fontWeight.bold,
              marginBottom: '0.25rem'
            }}>
              {user?.level || 1}
            </div>
            <div style={{
              fontSize: designSystem.typography.fontSize.lg,
              fontWeight: designSystem.typography.fontWeight.semibold
            }}>
              {user?.total_points || 0} points
            </div>
          </div>

          {/* Progress Bar */}
          <div style={{ marginBottom: '1rem' }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '0.5rem',
              fontSize: designSystem.typography.fontSize.sm,
              color: designSystem.colors.gray[600]
            }}>
              <span>Level {user?.level}</span>
              <span>Level {(user?.level || 1) + 1}</span>
            </div>
            <div style={{
              width: '100%',
              height: '12px',
              backgroundColor: designSystem.colors.gray[200],
              borderRadius: '6px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${getLevelProgress()}%`,
                height: '100%',
                background: `linear-gradient(90deg, ${designSystem.colors.primary[500]} 0%, ${designSystem.colors.secondary[500]} 100%)`,
                transition: 'width 0.3s ease'
              }} />
            </div>
            <div style={{
              textAlign: 'center',
              marginTop: '0.5rem',
              fontSize: designSystem.typography.fontSize.sm,
              color: designSystem.colors.gray[600]
            }}>
              {getLevelProgress().toFixed(0)}% to next level
            </div>
          </div>

          {/* Achievements */}
          <div style={{
            marginTop: '1.5rem',
            paddingTop: '1.5rem',
            borderTop: `1px solid ${designSystem.colors.gray[200]}`
          }}>
            <div style={{
              fontSize: designSystem.typography.fontSize.sm,
              fontWeight: designSystem.typography.fontWeight.semibold,
              color: designSystem.colors.gray[700],
              marginBottom: '0.75rem'
            }}>
              Achievements Unlocked: {user?.achievements?.length || 0}
            </div>
            <div style={{
              display: 'flex',
              gap: '0.5rem',
              flexWrap: 'wrap'
            }}>
              {(user?.achievements || []).slice(0, 6).map((_, idx) => (
                <div
                  key={idx}
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '8px',
                    background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1.25rem'
                  }}
                >
                  🏅
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Subscription & Usage Card */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '2rem',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          border: `1px solid ${designSystem.colors.gray[200]}`
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '1.5rem'
          }}>
            <h2 style={{
              fontSize: designSystem.typography.fontSize['2xl'],
              fontWeight: designSystem.typography.fontWeight.bold,
              color: designSystem.colors.gray[900],
              margin: 0
            }}>
              Subscription & Usage
            </h2>
            <div
              style={{
                padding: '0.5rem 1rem',
                borderRadius: '8px',
                backgroundColor: getTierBadgeColor(usage?.tier || 'free'),
                color: 'white',
                fontSize: designSystem.typography.fontSize.sm,
                fontWeight: designSystem.typography.fontWeight.semibold,
                textTransform: 'capitalize'
              }}
            >
              {usage?.tier || 'Free'}
            </div>
          </div>

          {/* Free-text Usage */}
          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '0.5rem'
            }}>
              <span style={{
                fontSize: designSystem.typography.fontSize.sm,
                fontWeight: designSystem.typography.fontWeight.semibold,
                color: designSystem.colors.gray[700]
              }}>
                Free-text Requests
              </span>
              <span style={{
                fontSize: designSystem.typography.fontSize.sm,
                color: designSystem.colors.gray[600]
              }}>
                {usage?.limits.unlimited_freetext ? 'Unlimited' : 
                  `${usage?.usage.freetext_requests || 0} / ${usage?.limits.freetext_requests_per_month || 0}`}
              </span>
            </div>
            {!usage?.limits.unlimited_freetext && (
              <div style={{
                width: '100%',
                height: '8px',
                backgroundColor: designSystem.colors.gray[200],
                borderRadius: '4px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${getUsagePercentage(
                    usage?.usage.freetext_requests || 0,
                    usage?.limits.freetext_requests_per_month || 0
                  )}%`,
                  height: '100%',
                  backgroundColor: getUsageColor(getUsagePercentage(
                    usage?.usage.freetext_requests || 0,
                    usage?.limits.freetext_requests_per_month || 0
                  )),
                  transition: 'width 0.3s ease'
                }} />
              </div>
            )}
          </div>

          {/* Prompted Usage */}
          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '0.5rem'
            }}>
              <span style={{
                fontSize: designSystem.typography.fontSize.sm,
                fontWeight: designSystem.typography.fontWeight.semibold,
                color: designSystem.colors.gray[700]
              }}>
                Prompted Requests
              </span>
              <span style={{
                fontSize: designSystem.typography.fontSize.sm,
                color: designSystem.colors.gray[600]
              }}>
                {usage?.limits.unlimited_prompted ? 'Unlimited' : 
                  `${usage?.usage.prompted_requests || 0} / ${usage?.limits.prompted_requests_per_month || 0}`}
              </span>
            </div>
            {!usage?.limits.unlimited_prompted && (
              <div style={{
                width: '100%',
                height: '8px',
                backgroundColor: designSystem.colors.gray[200],
                borderRadius: '4px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${getUsagePercentage(
                    usage?.usage.prompted_requests || 0,
                    usage?.limits.prompted_requests_per_month || 0
                  )}%`,
                  height: '100%',
                  backgroundColor: getUsageColor(getUsagePercentage(
                    usage?.usage.prompted_requests || 0,
                    usage?.limits.prompted_requests_per_month || 0
                  )),
                  transition: 'width 0.3s ease'
                }} />
              </div>
            )}
          </div>

          {/* Reset Date */}
          {usage?.usage.reset_date && (
            <div style={{
              padding: '1rem',
              backgroundColor: designSystem.colors.gray[50],
              borderRadius: '8px',
              fontSize: designSystem.typography.fontSize.sm,
              color: designSystem.colors.gray[600],
              marginBottom: '1rem'
            }}>
              Usage resets on {formatDate(usage.usage.reset_date)}
            </div>
          )}

          {/* Upgrade Button */}
          {usage?.tier === 'free' && (
            <button
              onClick={() => {
                trackEvent('upgrade_clicked', { from: 'dashboard', current_tier: usage?.tier });
                window.location.href = '/#pricing';
              }}
              style={{
                width: '100%',
                padding: '1rem',
                background: `linear-gradient(135deg, ${designSystem.colors.primary[600]} 0%, ${designSystem.colors.primary[700]} 100%)`,
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: designSystem.typography.fontSize.base,
                fontWeight: designSystem.typography.fontWeight.semibold,
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 8px 20px rgba(59, 130, 246, 0.3)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              Upgrade to Pro →
            </button>
          )}
        </div>

        {/* Goals Card */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '2rem',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          border: `1px solid ${designSystem.colors.gray[200]}`
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '1.5rem'
          }}>
            <h2 style={{
              fontSize: designSystem.typography.fontSize['2xl'],
              fontWeight: designSystem.typography.fontWeight.bold,
              color: designSystem.colors.gray[900],
              margin: 0
            }}>
              Your Goals
            </h2>
            <div style={{
              fontSize: 'clamp(2rem, 3vw, 3rem)'
            }}>
              🎯
            </div>
          </div>

          {goals ? (
            <>
              {/* Focus Areas */}
              <div style={{
                padding: '1rem',
                backgroundColor: designSystem.colors.primary[50],
                borderRadius: '8px',
                marginBottom: '1.5rem'
              }}>
                <div style={{
                  fontSize: designSystem.typography.fontSize.sm,
                  fontWeight: designSystem.typography.fontWeight.semibold,
                  color: designSystem.colors.primary[700],
                  marginBottom: '0.5rem'
                }}>
                  Primary Focus
                </div>
                <div style={{
                  fontSize: designSystem.typography.fontSize.lg,
                  fontWeight: designSystem.typography.fontWeight.bold,
                  color: designSystem.colors.primary[900],
                  textTransform: 'capitalize'
                }}>
                  {goals.primary_focus_area || 'Not set'}
                </div>
              </div>

              {/* Competency Scores */}
              <div>
                {getGoalCompetencies().map((competency, idx) => (
                  <div
                    key={idx}
                    style={{
                      marginBottom: '1rem',
                      paddingBottom: '1rem',
                      borderBottom: idx < 5 ? `1px solid ${designSystem.colors.gray[200]}` : 'none'
                    }}
                  >
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      marginBottom: '0.5rem'
                    }}>
                      <span style={{
                        fontSize: designSystem.typography.fontSize.sm,
                        fontWeight: designSystem.typography.fontWeight.medium,
                        color: designSystem.colors.gray[700]
                      }}>
                        {competency.name}
                      </span>
                      <span style={{
                        fontSize: designSystem.typography.fontSize.sm,
                        fontWeight: designSystem.typography.fontWeight.semibold,
                        color: competency.key === goals.primary_focus_area ? 
                          designSystem.colors.primary[600] : designSystem.colors.gray[600]
                      }}>
                        {competency.score}/10
                      </span>
                    </div>
                    <div style={{
                      width: '100%',
                      height: '6px',
                      backgroundColor: designSystem.colors.gray[200],
                      borderRadius: '3px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${(competency.score / 10) * 100}%`,
                        height: '100%',
                        backgroundColor: competency.key === goals.primary_focus_area ?
                          designSystem.colors.primary[500] : designSystem.colors.gray[400],
                        transition: 'width 0.3s ease'
                      }} />
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div style={{
              textAlign: 'center',
              padding: '2rem',
              color: designSystem.colors.gray[600]
            }}>
              <p style={{ marginBottom: '1rem' }}>Set your professional development goals to get personalized feedback alignment insights.</p>
              <button
                onClick={() => {
                  trackEvent('set_goals_clicked', { from: 'dashboard' });
                  window.location.href = '/goals';
                }}
                style={{
                  padding: '0.75rem 1.5rem',
                  backgroundColor: designSystem.colors.primary[600],
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: designSystem.typography.fontSize.base,
                  fontWeight: designSystem.typography.fontWeight.semibold,
                  cursor: 'pointer'
                }}
              >
                Set Your Goals
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div style={{
        maxWidth: '1400px',
        margin: '2rem auto 0',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '1rem'
      }}>
        <button
          onClick={() => {
            trackEvent('new_request_clicked', { from: 'dashboard' });
            window.location.href = '/request';
          }}
          style={{
            padding: '1.5rem',
            background: `linear-gradient(135deg, ${designSystem.colors.primary[600]} 0%, ${designSystem.colors.primary[700]} 100%)`,
            color: 'white',
            border: 'none',
            borderRadius: '12px',
            fontSize: designSystem.typography.fontSize.lg,
            fontWeight: designSystem.typography.fontWeight.semibold,
            cursor: 'pointer',
            transition: 'all 0.2s',
            textAlign: 'left'
          }}
        >
          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📝</div>
          <div>Request Feedback</div>
          <div style={{ fontSize: designSystem.typography.fontSize.sm, opacity: 0.9, marginTop: '0.25rem' }}>
            Get anonymous feedback from colleagues
          </div>
        </button>

        <button
          onClick={() => {
            trackEvent('view_responses_clicked', { from: 'dashboard' });
            window.location.href = '/responses';
          }}
          style={{
            padding: '1.5rem',
            backgroundColor: 'white',
            color: designSystem.colors.gray[900],
            border: `2px solid ${designSystem.colors.gray[200]}`,
            borderRadius: '12px',
            fontSize: designSystem.typography.fontSize.lg,
            fontWeight: designSystem.typography.fontWeight.semibold,
            cursor: 'pointer',
            transition: 'all 0.2s',
            textAlign: 'left'
          }}
        >
          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>💬</div>
          <div>View Responses</div>
          <div style={{ fontSize: designSystem.typography.fontSize.sm, color: designSystem.colors.gray[600], marginTop: '0.25rem' }}>
            See feedback you've received
          </div>
        </button>
      </div>
    </div>
  );
};

export default Dashboard;
