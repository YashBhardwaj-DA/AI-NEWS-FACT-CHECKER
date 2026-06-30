import { useState } from "react";
import { checkClaim } from "./api";

function badgeClass(verdict) {
  return verdict.toLowerCase().replace(/\s+/g, "-");
}

export default function Checker() {
  const [claim, setClaim] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!claim.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await checkClaim(claim.trim());
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <form className="checker" onSubmit={handleSubmit}>
        <textarea
          placeholder="Paste a headline or claim you saw and want checked…"
          value={claim}
          onChange={(e) => setClaim(e.target.value)}
        />
        <button className="submit" type="submit" disabled={loading || !claim.trim()}>
          {loading ? "Checking…" : "Check claim"}
        </button>
      </form>

      {error && <div className="error-state">{error}</div>}

      {result && (
        <div className="verdict-card">
          <span className={`verdict-badge ${badgeClass(result.verdict)}`}>{result.verdict}</span>
          <p className="reasoning">{result.reasoning}</p>
          <div className="confidence">
            CONFIDENCE: {result.confidence.toUpperCase()} · {result.source_agreement_count} CORROBORATING SOURCE
            {result.source_agreement_count === 1 ? "" : "S"}
          </div>

          {result.matched_sources.length > 0 && (
            <div className="sources-list" style={{ marginTop: 16 }}>
              {result.matched_sources.map((s, i) => (
                <a
                  key={i}
                  className="source-chip"
                  href={s.link}
                  target="_blank"
                  rel="noreferrer"
                  style={{ textDecoration: "none" }}
                >
                  {s.source}
                </a>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
