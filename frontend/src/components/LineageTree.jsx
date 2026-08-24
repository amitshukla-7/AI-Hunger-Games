import React from 'react';

export default function LineageTree({ agents }) {
  if (!agents || agents.length === 0) {
    return (
      <div className="panel" style={{ textAlign: 'center', padding: '2.5rem' }}>
        <p style={{ color: '#94a3b8' }}>No lineage data available yet. Run generations to visualize prompt genetic evolution.</p>
      </div>
    );
  }

  // Group agents by generation
  const generations = {};
  agents.forEach(a => {
    const gen = a.generation || 1;
    if (!generations[gen]) generations[gen] = [];
    generations[gen].push(a);
  });

  const genKeys = Object.keys(generations).map(Number).sort((a, b) => a - b);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      <div className="panel">
        <div style={{ fontSize: '1rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '0.25rem' }}>
          Prompt Lineage & Genetic Evolution Tree
        </div>
        <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '1rem' }}>
          Visual mapping of prompt traits, archetypes, and parent-child inheritance across successive generations.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', padding: '1rem 0' }}>
          {genKeys.map(gen => (
            <div key={gen} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: '700', color: '#38bdf8', borderBottom: '1px solid #1e293b', paddingBottom: '0.3rem' }}>
                GENERATION {gen} ({generations[gen].length} AGENTS)
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
                {generations[gen].map(agent => (
                  <div 
                    key={agent.id}
                    style={{
                      background: '#0b0f17',
                      border: '1px solid #1e293b',
                      borderRadius: '6px',
                      padding: '0.75rem',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.4rem'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: '600', color: '#f1f5f9' }}>{agent.name}</span>
                      <span className={`badge badge-${agent.status}`}>{agent.status}</span>
                    </div>

                    <div style={{ fontSize: '0.75rem', color: '#38bdf8', fontFamily: 'JetBrains Mono, monospace' }}>
                      {agent.model}
                    </div>

                    <div style={{ fontSize: '0.75rem', color: '#cbd5e1' }}>
                      Archetype: <strong>{agent.archetype}</strong>
                    </div>

                    {agent.parent_ids && agent.parent_ids.length > 0 ? (
                      <div style={{ fontSize: '0.7rem', color: '#94a3b8', borderTop: '1px dashed #1e293b', paddingTop: '0.4rem', marginTop: '0.2rem' }}>
                        Inherited From Parents: #{agent.parent_ids.join(', #')}
                      </div>
                    ) : (
                      <div style={{ fontSize: '0.7rem', color: '#64748b', borderTop: '1px dashed #1e293b', paddingTop: '0.4rem', marginTop: '0.2rem' }}>
                        Seed Ancestor (Gen 1)
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
