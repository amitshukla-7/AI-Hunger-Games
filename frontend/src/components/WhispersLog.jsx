import React from 'react';

export default function WhispersLog({ whispers, agents }) {
  if (!whispers || whispers.length === 0) {
    return (
      <div className="panel" style={{ textAlign: 'center', padding: '2.5rem' }}>
        <p style={{ color: '#94a3b8' }}>No secret whispers recorded yet. Execute tournament rounds to intercept agent communications.</p>
      </div>
    );
  }

  const getProposalBadge = (type) => {
    switch (type) {
      case 'alliance':
        return <span className="badge badge-active">Alliance Pact</span>;
      case 'trade':
        return <span className="badge badge-victor">Vote Trade</span>;
      case 'threat':
        return <span className="badge badge-eliminated">Subtle Threat</span>;
      case 'betrayal':
        return <span className="badge badge-eliminated" style={{ background: '#7f1d1d', color: '#fca5a5' }}>Betrayal</span>;
      default:
        return <span className="badge">Side Message</span>;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Intercepted Whispers Feed */}
      <div className="panel">
        <div style={{ fontSize: '1rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '0.25rem' }}>
          Intercepted Agent Whispers & Conspiracies
        </div>
        <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '1rem' }}>
          Private 1-to-1 communications sent between competing agents prior to peer-evaluation voting.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {whispers.map((w) => (
            <div 
              key={w.id}
              style={{
                background: '#0b0f17',
                border: '1px solid #1e293b',
                borderRadius: '6px',
                padding: '0.75rem 1rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.4rem'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontSize: '0.85rem', color: '#f1f5f9', fontWeight: '600' }}>
                  <span style={{ color: '#38bdf8' }}>{w.sender_name}</span>
                  <span style={{ color: '#64748b', margin: '0 0.4rem' }}>→</span>
                  <span style={{ color: '#cbd5e1' }}>{w.receiver_name}</span>
                </div>
                {getProposalBadge(w.proposal_type)}
              </div>

              <div style={{ fontSize: '0.85rem', color: '#cbd5e1', fontStyle: 'italic', background: '#131b2e', padding: '0.5rem 0.75rem', borderRadius: '4px', borderLeft: '3px solid #38bdf8' }}>
                "{w.message}"
              </div>

              <div style={{ fontSize: '0.7rem', color: '#64748b', textAlign: 'right' }}>
                Timestamp: {w.created_at || 'Round Intercept'}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
