import { useState } from "react";
import { api } from "../api";

export function WeeklyDigest({ userId }) {
  const [digest, setDigest] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generate = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.generateDigest(userId);
      setDigest(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="weekly-digest">
      <h2>Weekly Digest</h2>
      <button onClick={generate} disabled={loading}>
        {loading ? "Analyzing..." : "Generate My Weekly Digest"}
      </button>
      {error && <p className="error">{error}</p>}
      {digest && (
        <div className="digest-result">
          <h3>Your Week</h3>
          <p className="weakness-summary">{digest.weakness_summary}</p>

          <h4>Top Weaknesses</h4>
          {digest.top_weaknesses.map((w, i) => (
            <div key={i} className="weakness-card">
              <strong>{w.area}</strong> — {w.percent}% of points lost
              <br /><small>{w.evidence}</small>
            </div>
          ))}

          <h4>Recommended Drills</h4>
          {digest.drill_recommendations.map((d, i) => (
            <div key={i} className="drill-card">
              <strong>{d.drill}</strong> ({d.reps} × {d.sets})
              <br /><em>{d.why}</em>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
