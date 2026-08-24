import React from 'react';

export default function AgentCard({ agent, onSelect }) {
  const renderBadge = (status) => {
    switch (status) {
      case 'victor':
        return <span className="badge badge-victor">Victor</span>;
      case 'eliminated':
        return <span className="badge badge-eliminated">Eliminated</span>;
      default:
        return <span className="badge badge-active">Active</span>;
    }
  };

  return (
    <div 
      className={`agent-card ${agent.status}`}
      onClick={() => onSelect && onSelect(agent)}
      style={{ cursor: 'pointer' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
        <div>
          <h3 style={{ fontSize: '1rem', fontWeight: '600', color: '#f1f5f9' }}>{agent.name}</h3>
          <span style={{ fontSize: '0.75rem', color: '#94a3b8', fontFamily: 'JetBrains Mono, monospace' }}>
            {agent.model}
          </span>
        </div>
        {renderBadge(agent.status)}
      </div>

      <div style={{ marginBottom: '0.75rem' }}>
        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Archetype</div>
        <div style={{ fontSize: '0.85rem', color: '#cbd5e1', fontWeight: '500' }}>{agent.archetype}</div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#64748b', borderTop: '1px solid #1e293b', paddingTop: '0.5rem' }}>
        <span>Generation {agent.generation}</span>
        {agent.parent_ids && agent.parent_ids.length > 0 && (
          <span>Lineage: #{agent.parent_ids.join(', #')}</span>
        )}
      </div>
    </div>
  );
}
