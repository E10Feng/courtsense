export function DrillCard({ drill }) {
  return (
    <div className="drill-card">
      <div className="drill-header">
        <strong>{drill.name}</strong>
        <span className="sport-badge-sm">{drill.sport}</span>
      </div>
      <p>{drill.description}</p>
      <div className="drill-meta">
        <span>Target: {drill.target_weakness}</span>
        <span>{drill.reps} × {drill.sets}</span>
        <span className={`diff-${drill.difficulty}`}>{drill.difficulty}</span>
      </div>
    </div>
  );
}
