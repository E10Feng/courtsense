import { useState } from "react";
import { SessionLogger } from "./components/SessionLogger";
import { SessionList } from "./components/SessionList";
import { WeeklyDigest } from "./components/WeeklyDigest";
import { DrillCard } from "./components/DrillCard";
import { api } from "./api";

const DEMO_USER_ID = "00000000-0000-0000-0000-000000000001";

export default function App() {
  const [activeTab, setActiveTab] = useState("log");
  const [drillResults, setDrillResults] = useState([]);
  const [drillQuery, setDrillQuery] = useState("");
  const [drillSport, setDrillSport] = useState("pickleball");

  const searchDrills = async (e) => {
    e.preventDefault();
    if (!drillQuery.trim()) return;
    const res = await api.searchDrills(drillQuery, drillSport);
    setDrillResults(res.drills);
  };

  return (
    <div className="app">
      <header>
        <h1>CourtSense 🎾</h1>
        <nav>
          <button className={activeTab === "log" ? "active" : ""} onClick={() => setActiveTab("log")}>Log</button>
          <button className={activeTab === "history" ? "active" : ""} onClick={() => setActiveTab("history")}>History</button>
          <button className={activeTab === "digest" ? "active" : ""} onClick={() => setActiveTab("digest")}>Digest</button>
          <button className={activeTab === "drills" ? "active" : ""} onClick={() => setActiveTab("drills")}>Drills</button>
        </nav>
      </header>
      <main>
        {activeTab === "log" && (
          <SessionLogger userId={DEMO_USER_ID} />
        )}
        {activeTab === "history" && (
          <SessionList userId={DEMO_USER_ID} />
        )}
        {activeTab === "digest" && (
          <WeeklyDigest userId={DEMO_USER_ID} />
        )}
        {activeTab === "drills" && (
          <div className="drill-search">
            <h2>Find Drills</h2>
            <form onSubmit={searchDrills}>
              <input
                placeholder="What do you want to improve? (e.g., net play, backhand)"
                value={drillQuery}
                onChange={e => setDrillQuery(e.target.value)}
              />
              <select value={drillSport} onChange={e => setDrillSport(e.target.value)}>
                <option value="pickleball">Pickleball</option>
                <option value="tennis">Tennis</option>
              </select>
              <button type="submit">Search</button>
            </form>
            <div className="drill-results">
              {drillResults.map(d => <DrillCard key={d.id} drill={d} />)}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
