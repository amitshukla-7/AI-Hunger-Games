import React, { useState, useEffect } from 'react';
import AgentCard from './components/AgentCard';
import TournamentBracket from './components/TournamentBracket';
import VoteAffinityGraph from './components/VoteAffinityGraph';
import ExperimentReport from './components/ExperimentReport';
import WhispersLog from './components/WhispersLog';
import LineageTree from './components/LineageTree';

export default function App() {
  const [state, setState] = useState({ tournament: null, agents: [], rounds: [], answers: [], votes: [], whispers: [] });
  const [analytics, setAnalytics] = useState(null);
  const [activeTab, setActiveTab] = useState('roster');
  const [loading, setLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [customPrompt, setCustomPrompt] = useState('');
  const [wsConnected, setWsConnected] = useState(false);

  const fetchData = async () => {
    try {
      const res = await fetch('/api/state');
      if (res.ok) {
        const data = await res.json();
        setState(data);
      }
      const analyticsRes = await fetch('/api/analytics');
      if (analyticsRes.ok) {
        const aData = await analyticsRes.json();
        setAnalytics(aData);
      }
    } catch (err) {
      console.error("Error fetching state:", err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000);

    // WebSocket Telemetry Connection
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    let ws = null;

    try {
      ws = new WebSocket(wsUrl);
      ws.onopen = () => setWsConnected(true);
      ws.onclose = () => setWsConnected(false);
      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.event === 'round_complete' || msg.event === 'season_start') {
            fetchData();
          }
        } catch (e) {
          console.error("WS Parse error:", e);
        }
      };
    } catch (e) {
      console.error("WS connection error:", e);
    }

    return () => {
      clearInterval(interval);
      if (ws) ws.close();
    };
  }, []);

  const handleStepRound = async () => {
    setLoading(true);
    try {
      const payload = customPrompt && customPrompt.trim() ? { custom_prompt: customPrompt.trim(), prompt_type: "User Challenge" } : {};
      const res = await fetch('/api/tournament/step', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setCustomPrompt('');
        await fetchData();
        setActiveTab('bracket');
      }
    } catch (err) {
      console.error("Error executing round:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleResetTournament = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/tournament/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: "AI Hunger Games — Season " + Date.now() })
      });
      if (res.ok) {
        await fetchData();
        setActiveTab('roster');
      }
    } catch (err) {
      console.error("Error resetting tournament:", err);
    } finally {
      setLoading(false);
    }
  };

  const currentGen = state.agents.length > 0 ? Math.max(...state.agents.map(a => a.generation)) : 1;
  const activeCount = state.agents.filter(a => a.generation === currentGen && a.status === 'active').length;

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-title">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <h1>AI Hunger Games</h1>
            <span 
              style={{
                fontSize: '0.7rem',
                padding: '0.15rem 0.5rem',
                borderRadius: '4px',
                background: wsConnected ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                color: wsConnected ? '#10b981' : '#ef4444',
                border: wsConnected ? '1px solid #10b981' : '1px solid #ef4444',
                fontWeight: '600'
              }}
            >
              {wsConnected ? '● WS Live' : '○ Polling'}
            </span>
          </div>
          <div className="header-subtitle">
            Multi-Agent Peer Evaluation Platform &bull; Generation {currentGen} &bull; Active: {activeCount}
          </div>
        </div>

        <div className="header-actions">
          <button className="btn btn-secondary" onClick={handleResetTournament} disabled={loading}>
            Reset Season
          </button>
        </div>
      </header>

      {/* User Custom Challenge Prompt Bar */}
      <div className="panel" style={{ marginBottom: '1.5rem', display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
        <input 
          type="text"
          value={customPrompt}
          onChange={(e) => setCustomPrompt(e.target.value)}
          placeholder="Type custom arena prompt for agents (or leave empty for default prompt)..."
          style={{
            flex: 1,
            background: '#0b0f17',
            border: '1px solid #1e293b',
            borderRadius: '6px',
            padding: '0.6rem 0.85rem',
            color: '#f1f5f9',
            fontSize: '0.875rem',
            outline: 'none'
          }}
          onKeyDown={(e) => e.key === 'Enter' && !loading && handleStepRound()}
        />
        <button 
          className="btn btn-primary" 
          onClick={handleStepRound} 
          disabled={loading}
          style={{ whiteSpace: 'nowrap' }}
        >
          {loading ? "Simulating..." : "Execute Round"}
        </button>
      </div>

      {/* Tabs */}
      <nav className="tab-nav">
        <button 
          className={`tab-btn ${activeTab === 'roster' ? 'active' : ''}`}
          onClick={() => setActiveTab('roster')}
        >
          Contestants ({state.agents.length})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'bracket' ? 'active' : ''}`}
          onClick={() => setActiveTab('bracket')}
        >
          Brackets & Rounds ({state.rounds.length})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'whispers' ? 'active' : ''}`}
          onClick={() => setActiveTab('whispers')}
        >
          Secret Whispers ({state.whispers ? state.whispers.length : 0})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'graph' ? 'active' : ''}`}
          onClick={() => setActiveTab('graph')}
        >
          Affinity Matrix
        </button>
        <button 
          className={`tab-btn ${activeTab === 'lineage' ? 'active' : ''}`}
          onClick={() => setActiveTab('lineage')}
        >
          Lineage Tree
        </button>
        <button 
          className={`tab-btn ${activeTab === 'report' ? 'active' : ''}`}
          onClick={() => setActiveTab('report')}
        >
          Analysis Report
        </button>
      </nav>

      {/* Main Content */}
      <main>
        {activeTab === 'roster' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h2 style={{ fontSize: '1rem', fontWeight: '600', color: '#f1f5f9' }}>
                Generation {currentGen} Agents
              </h2>
              <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                Select any agent to inspect system prompt & lineage
              </span>
            </div>
            <div className="grid-cards">
              {state.agents.map((ag) => (
                <AgentCard key={ag.id} agent={ag} onSelect={setSelectedAgent} />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'bracket' && (
          <TournamentBracket 
            rounds={state.rounds} 
            answers={state.answers} 
            votes={state.votes} 
            agents={state.agents} 
          />
        )}

        {activeTab === 'whispers' && (
          <WhispersLog 
            whispers={state.whispers || []} 
            agents={state.agents} 
          />
        )}

        {activeTab === 'graph' && (
          <VoteAffinityGraph 
            analytics={analytics} 
            votes={state.votes} 
            agents={state.agents} 
          />
        )}

        {activeTab === 'lineage' && (
          <LineageTree 
            agents={state.agents} 
          />
        )}

        {activeTab === 'report' && (
          <ExperimentReport 
            analytics={analytics} 
            rounds={state.rounds} 
            agents={state.agents} 
          />
        )}
      </main>

      {/* Modal */}
      {selectedAgent && (
        <div className="modal-overlay" onClick={() => setSelectedAgent(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h2 style={{ fontSize: '1.1rem', fontWeight: '600', color: '#f1f5f9' }}>{selectedAgent.name}</h2>
              <button className="btn btn-secondary" onClick={() => setSelectedAgent(null)} style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}>✕ Close</button>
            </div>
            
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
              <span style={{ background: '#1e293b', color: '#38bdf8', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontFamily: 'JetBrains Mono, monospace' }}>
                {selectedAgent.model}
              </span>
              <span style={{ background: '#1e293b', color: '#cbd5e1', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem' }}>
                Generation {selectedAgent.generation}
              </span>
            </div>

            <div style={{ marginBottom: '0.75rem' }}>
              <div style={{ color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '0.2rem' }}>Archetype</div>
              <div style={{ color: '#f1f5f9', fontSize: '0.875rem', fontWeight: '500' }}>{selectedAgent.archetype}</div>
            </div>

            <div>
              <div style={{ color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase', marginBottom: '0.2rem' }}>System Personality Prompt</div>
              <pre style={{ background: '#0b0f17', padding: '0.75rem', borderRadius: '4px', border: '1px solid #1e293b', color: '#94a3b8', fontSize: '0.8rem', whiteSpace: 'pre-wrap', fontFamily: 'JetBrains Mono, monospace' }}>
                {selectedAgent.personality_prompt}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
