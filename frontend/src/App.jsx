import { useState } from "react";
import Feed from "./Feed";
import Checker from "./Checker";

export default function App() {
  const [tab, setTab] = useState("feed");

  return (
    <div className="app">
      <header className="header">
        <h1>NewsCheck</h1>
        <p>
          Headlines cross-referenced across independent sources, so you can see at a glance
          how corroborated a story is — plus a checker for claims you run into elsewhere.
        </p>
        <div className="tabs">
          <button className={`tab ${tab === "feed" ? "active" : ""}`} onClick={() => setTab("feed")}>
            Feed
          </button>
          <button className={`tab ${tab === "check" ? "active" : ""}`} onClick={() => setTab("check")}>
            Check a claim
          </button>
        </div>
      </header>

      {tab === "feed" ? <Feed /> : <Checker />}
    </div>
  );
}
