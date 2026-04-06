import { useState, useEffect } from "react";
import { api } from "../api";

export function SessionList({ userId, days = 7 }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const data = await api.getSessions(userId, days);
      setSessions(data.sessions);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [userId, days]);

  if (loading) return <p>Loading sessions...</p>;

  return (
    <div className="session-list">
      <h2>Recent Sessions ({days} days)</h2>
      {sessions.length === 0 ? (
        <p>No sessions logged yet. Log your first session above!</p>
      ) : (
        sessions.map(s => (
          <div key={s.id} className="session-card">
            <div className="session-header">
              <span className="sport-badge">{s.sport}</span>
              <span>{s.date}</span>
              <span className="score">{s.score}</span>
            </div>
            {s.notes && <p className="notes">"{s.notes}"</p>}
            <div className="ratings-small">
              <span>E: {s.energy}</span>
              <span>M: {s.mood}</span>
              <span>L: {s.legs}</span>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
