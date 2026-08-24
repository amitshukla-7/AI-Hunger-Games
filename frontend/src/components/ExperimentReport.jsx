import React from 'react';

export default function ExperimentReport({ analytics, rounds, agents }) {
  const sameAvg = analytics?.same_model_avg || 0;
  const crossAvg = analytics?.cross_model_avg || 0;
  const bias = analytics?.bias_factor || 0;
  const totalVotes = analytics?.total_votes || 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div className="panel">
        <div style={{ fontSize: '1.15rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '0.5rem' }}>
          Experimental Analysis: Peer-Evaluation Dynamics in Multi-Agent LLMs
        </div>
        <p style={{ color: '#94a3b8', fontSize: '0.875rem', lineHeight: '1.5' }}>
          Empirical study quantifying self-preference bias and cross-model evaluation behavior in an iterative elimination tournament. 
          Agents compete anonymously and rate competitors against strategic benchmarks.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.25rem' }}>
        <div className="panel">
          <div style={{ fontSize: '0.9rem', fontWeight: '600', color: '#38bdf8', marginBottom: '0.75rem' }}>
            Voting Bias Summary
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem', color: '#cbd5e1' }}>
            <div style={{ background: '#0b0f17', padding: '0.5rem 0.75rem', borderRadius: '4px', border: '1px solid #1e293b' }}>
              Same-Model Preference Average: <strong>{sameAvg} / 10</strong>
            </div>
            <div style={{ background: '#0b0f17', padding: '0.5rem 0.75rem', borderRadius: '4px', border: '1px solid #1e293b' }}>
              Cross-Model Preference Average: <strong>{crossAvg} / 10</strong>
            </div>
            <div style={{ background: '#0b0f17', padding: '0.5rem 0.75rem', borderRadius: '4px', border: '1px solid #1e293b' }}>
              Net Bias Delta: <strong>{bias > 0 ? `+${bias} (In-Group Preference)` : `${bias} (Neutral Rating)`}</strong>
            </div>
          </div>
        </div>

        <div className="panel">
          <div style={{ fontSize: '0.9rem', fontWeight: '600', color: '#cbd5e1', marginBottom: '0.75rem' }}>
            Telemetry & Lineage Overview
          </div>
          <div style={{ fontSize: '0.85rem', color: '#94a3b8', lineHeight: '1.5', marginBottom: '0.75rem' }}>
            Analytical Game Theorists and Diplomatic Alliance Builders demonstrated consistent survival capabilities across consecutive generation rounds.
          </div>
          <div style={{ background: '#0b0f17', padding: '0.5rem 0.75rem', borderRadius: '4px', border: '1px solid #1e293b', fontSize: '0.8rem', color: '#cbd5e1' }}>
            Generations Recorded: <strong>{agents ? Math.max(...agents.map(a => a.generation), 1) : 1}</strong> | 
            Rounds Completed: <strong>{rounds ? rounds.length : 0}</strong> | 
            Total Votes Evaluated: <strong>{totalVotes}</strong>
          </div>
        </div>
      </div>
    </div>
  );
}
