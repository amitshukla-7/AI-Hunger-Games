import React, { useState } from 'react';

export default function TournamentBracket({ rounds, answers, votes, agents }) {
  const [selectedRoundId, setSelectedRoundId] = useState(null);

  const activeRound = rounds && rounds.length > 0
    ? (rounds.find(r => r.id === selectedRoundId) || rounds[rounds.length - 1])
    : null;

  const currentAnswers = activeRound
    ? answers.filter(a => a.round_id === activeRound.id)
    : [];

  const currentVotes = activeRound
    ? votes.filter(v => v.round_id === activeRound.id)
    : [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Round Selection Bar */}
      <div style={{ display: 'flex', gap: '0.5rem', overflowX: 'auto', paddingBottom: '0.25rem' }}>
        {rounds.map((r) => (
          <button
            key={r.id}
            onClick={() => setSelectedRoundId(r.id)}
            className="btn btn-secondary"
            style={{
              padding: '0.4rem 0.8rem',
              fontSize: '0.8rem',
              borderColor: activeRound && activeRound.id === r.id ? '#38bdf8' : '#1e293b',
              background: activeRound && activeRound.id === r.id ? '#1e293b' : '#0f172a'
            }}
          >
            Gen {r.generation} — Round {r.round_number}
          </button>
        ))}
      </div>

      {activeRound ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '1.25rem' }}>
          {/* Main Round Content */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {/* Task Prompt Banner */}
            <div className="panel">
              <div style={{ fontSize: '0.75rem', fontWeight: '600', color: '#38bdf8', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                Challenge: {activeRound.prompt_type}
              </div>
              <div style={{ fontSize: '1rem', color: '#f1f5f9', fontWeight: '500' }}>
                {activeRound.task_prompt}
              </div>
            </div>

            <div style={{ fontSize: '0.9rem', fontWeight: '600', color: '#cbd5e1' }}>
              Submissions & Peer Ratings
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {currentAnswers.map((ans) => {
                const votesReceived = currentVotes.filter(v => v.candidate_id === ans.agent_id);
                return (
                  <div 
                    key={ans.id} 
                    className="panel"
                    style={{
                      borderColor: ans.eliminated ? '#ef4444' : '#1e293b',
                      opacity: ans.eliminated ? 0.75 : 1
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontWeight: '600', color: '#f1f5f9', fontSize: '0.95rem' }}>{ans.agent_name}</span>
                        <span style={{ fontSize: '0.75rem', color: '#64748b', fontFamily: 'JetBrains Mono, monospace' }}>
                          {ans.agent_model}
                        </span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '0.9rem', fontWeight: '700', color: ans.eliminated ? '#ef4444' : '#10b981' }}>
                          {ans.score} / 10
                        </span>
                        {ans.eliminated === 1 && (
                          <span className="badge badge-eliminated">Eliminated</span>
                        )}
                      </div>
                    </div>

                    <p style={{ fontSize: '0.875rem', color: '#cbd5e1', lineHeight: '1.5', marginBottom: '0.75rem', background: '#0b0f17', padding: '0.6rem 0.75rem', borderRadius: '4px' }}>
                      "{ans.answer_text}"
                    </p>

                    {votesReceived.length > 0 && (
                      <div style={{ borderTop: '1px solid #1e293b', paddingTop: '0.5rem' }}>
                        <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '0.25rem' }}>
                          Peer Voting Feedback ({votesReceived.length} votes):
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                          {votesReceived.map((v) => (
                            <div key={v.id} style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'flex', justifyContent: 'space-between' }}>
                              <span><strong>{v.voter_name}</strong>: "{v.justification}"</span>
                              <span style={{ color: v.same_model ? '#38bdf8' : '#94a3b8', fontWeight: '600', marginLeft: '0.5rem' }}>
                                [{v.score_given}/10]
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Elimination Sidebar */}
          <div>
            <div className="panel" style={{ position: 'sticky', top: '1rem' }}>
              <div style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.75rem', color: '#f1f5f9' }}>
                Status Tracker
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {agents.map((ag) => (
                  <div 
                    key={ag.id}
                    style={{
                      display: 'flex',
                      justify: 'space-between',
                      alignItems: 'center',
                      padding: '0.4rem 0.6rem',
                      borderRadius: '4px',
                      background: ag.status === 'eliminated' ? 'rgba(239, 68, 68, 0.05)' : '#0b0f17',
                      border: '1px solid #1e293b'
                    }}
                  >
                    <div>
                      <div style={{ fontSize: '0.8rem', fontWeight: '500', color: ag.status === 'eliminated' ? '#64748b' : '#f1f5f9' }}>
                        {ag.name}
                      </div>
                      <div style={{ fontSize: '0.7rem', color: '#64748b', fontFamily: 'JetBrains Mono, monospace' }}>{ag.model}</div>
                    </div>
                    {ag.status === 'eliminated' ? (
                      <span className="badge badge-eliminated">Out</span>
                    ) : ag.status === 'victor' ? (
                      <span className="badge badge-victor">Victor</span>
                    ) : (
                      <span className="badge badge-active">Active</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="panel" style={{ textAlign: 'center', padding: '2.5rem' }}>
          <p style={{ color: '#94a3b8' }}>No rounds executed yet. Click "Run Tournament Round" to start.</p>
        </div>
      )}
    </div>
  );
}
