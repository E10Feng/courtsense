import { useState } from "react";
import { api } from "./api";

export function SessionLogger({ userId, onSessionCreated }) {
  const [sport, setSport] = useState("pickleball");
  const [score, setScore] = useState("");
  const [partnerNames, setPartnerNames] = useState("");
  const [opponentNames, setOpponentNames] = useState("");
  const [drillsDone, setDrillsDone] = useState("");
  const [energy, setEnergy] = useState(3);
  const [mood, setMood] = useState(3);
  const [legs, setLegs] = useState(3);
  const [notes, setNotes] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const res = await api.createSession({
        user_id: userId,
        sport,
        score,
        partner_names: partnerNames,
        opponent_names: opponentNames,
        drills_done: drillsDone,
        energy,
        mood,
        legs,
        notes,
      });
      onSessionCreated?.(res);
      // Reset form
      setScore(""); setPartnerNames(""); setOpponentNames("");
      setDrillsDone(""); setNotes("");
      setEnergy(3); setMood(3); setLegs(3);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="session-form">
      <h2>Log a Session</h2>
      <div className="sport-toggle">
        <button type="button" className={sport === "pickleball" ? "active" : ""} onClick={() => setSport("pickleball")}>Pickleball</button>
        <button type="button" className={sport === "tennis" ? "active" : ""} onClick={() => setSport("tennis")}>Tennis</button>
      </div>
      <input placeholder="Score (e.g., 11-9, 8-11)" value={score} onChange={e => setScore(e.target.value)} required />
      <input placeholder="Partner names (optional)" value={partnerNames} onChange={e => setPartnerNames(e.target.value)} />
      <input placeholder="Opponent names (optional)" value={opponentNames} onChange={e => setOpponentNames(e.target.value)} />
      <input placeholder="Drills done (optional)" value={drillsDone} onChange={e => setDrillsDone(e.target.value)} />
      <div className="ratings">
        <label>Energy: <input type="range" min="1" max="5" value={energy} onChange={e => setEnergy(Number(e.target.value))} /> {energy}</label>
        <label>Mood: <input type="range" min="1" max="5" value={mood} onChange={e => setMood(Number(e.target.value))} /> {mood}</label>
        <label>Legs: <input type="range" min="1" max="5" value={legs} onChange={e => setLegs(Number(e.target.value))} /> {legs}</label>
      </div>
      <textarea placeholder="Notes (optional)" value={notes} onChange={e => setNotes(e.target.value)} rows={2} />
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={submitting}>{submitting ? "Saving..." : "Log Session"}</button>
    </form>
  );
}
