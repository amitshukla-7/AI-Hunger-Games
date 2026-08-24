import React from 'react';

export default function VoteAffinityGraph({ analytics, votes, agents }) {
  if (!analytics || !analytics.model_matrix) {
    return (
      <div className="panel" style={{ textAlign: 'center', padding: '2.5rem' }}>
        <p style={{ color: '#94a3b8' }}>Gathering voting telemetry... Run rounds to see affinity dynamics.</p>
      </div>
    );
  }

  const { same_model_avg, cross_model_avg, bias_factor, total_votes, model_matrix } = analytics;
  const models = Object.keys(model_matrix);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div className="panel">
          <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Same-Model Rating</div>
          <div style={{ fontSize: '1.75rem', fontWeight: '700', color: '#38bdf8', marginTop: '0.2rem' }}>
            {same_model_avg} <span style={{ fontSize: '0.875rem', color: '#64748b' }}>/ 10</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>Average rating for same LLM family</div>
        </div>

        <div className="panel">
          <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Cross-Model Rating</div>
          <div style={{ fontSize: '1.75rem', fontWeight: '700', color: '#f1f5f9', marginTop: '0.2rem' }}>
            {cross_model_avg} <span style={{ fontSize: '0.875rem', color: '#64748b' }}>/ 10</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>Average rating for different LLM family</div>
        </div>

        <div className="panel">
          <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Self-Preference Bias Factor</div>
          <div style={{ fontSize: '1.75rem', fontWeight: '700', color: bias_factor > 0 ? '#ef4444' : '#10b981', marginTop: '0.2rem' }}>
            {bias_factor > 0 ? `+${bias_factor}` : bias_factor}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
            {bias_factor > 0 ? "Positive In-Group Bias" : "Neutral Cross-Model Rating"}
          </div>
        </div>

        <div className="panel">
          <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Total Votes</div>
          <div style={{ fontSize: '1.75rem', fontWeight: '700', color: '#f1f5f9', marginTop: '0.2rem' }}>
            {total_votes}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>Recorded peer evaluation events</div>
        </div>
      </div>

      {/* Model Affinity Matrix */}
      <div className="panel">
        <div style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '0.25rem', color: '#f1f5f9' }}>
          Model Evaluation Matrix
        </div>
        <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '1rem' }}>
          Rows represent evaluating model families; Columns represent candidate model families being evaluated.
        </p>

        {models.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #1e293b' }}>
                  <th style={{ padding: '0.6rem', color: '#64748b', fontSize: '0.75rem', textAlign: 'left', fontWeight: '500' }}>Evaluator ↓ \ Candidate →</th>
                  {models.map(m => (
                    <th key={m} style={{ padding: '0.6rem', color: '#cbd5e1', fontSize: '0.8rem', fontWeight: '600', fontFamily: 'JetBrains Mono, monospace' }}>{m}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {models.map(voterM => (
                  <tr key={voterM} style={{ borderBottom: '1px solid #162032' }}>
                    <td style={{ padding: '0.6rem', color: '#38bdf8', fontWeight: '500', fontSize: '0.8rem', textAlign: 'left', fontFamily: 'JetBrains Mono, monospace' }}>{voterM}</td>
                    {models.map(candM => {
                      const score = model_matrix[voterM]?.[candM];
                      const isSame = (voterM === candM);
                      return (
                        <td key={candM} style={{ padding: '0.6rem' }}>
                          {score !== undefined ? (
                            <span 
                              style={{
                                padding: '0.25rem 0.6rem',
                                borderRadius: '4px',
                                fontSize: '0.8rem',
                                fontWeight: '600',
                                display: 'inline-block',
                                background: isSame ? 'rgba(56, 189, 248, 0.1)' : '#0b0f17',
                                color: isSame ? '#38bdf8' : '#cbd5e1',
                                border: '1px solid #1e293b'
                              }}
                            >
                              {score} / 10
                            </span>
                          ) : (
                            <span style={{ color: '#64748b', fontSize: '0.75rem' }}>—</span>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: '#64748b', fontSize: '0.85rem' }}>No cross-model vote data available yet.</p>
        )}
      </div>
    </div>
  );
}
