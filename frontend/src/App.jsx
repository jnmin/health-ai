import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const API_BASE_CANDIDATES = [
  import.meta.env.VITE_API_BASE_URL,
  "/api",
  "http://127.0.0.1:5000",
  "http://localhost:5000",
].filter(Boolean);

const initialForm = {
  meals: "",
  sleep: "",
  mood: "",
};

function App() {
  const [form, setForm] = useState(initialForm);
  const [logs, setLogs] = useState([]);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [suggestion, setSuggestion] = useState("");
  const [suggestionSource, setSuggestionSource] = useState("");
  const [loadingSuggestion, setLoadingSuggestion] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [activeApiBase, setActiveApiBase] = useState("");

  const requestJson = async (path, options = {}) => {
    const triedErrors = [];
    const basesToTry = activeApiBase
      ? [activeApiBase, ...API_BASE_CANDIDATES.filter((base) => base !== activeApiBase)]
      : API_BASE_CANDIDATES;

    for (const base of basesToTry) {
      try {
        const response = await fetch(`${base}${path}`, options);
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
          throw new Error(data.error || "Request failed.");
        }

        if (activeApiBase !== base) {
          setActiveApiBase(base);
        }

        return data;
      } catch (requestError) {
        triedErrors.push(`${base}: ${requestError.message}`);
      }
    }

    throw new Error(`Unable to reach the backend. Tried ${triedErrors.join(" | ")}`);
  };

  const fetchLogs = async () => {
    const data = await requestJson("/log");
    setLogs(data);
  };

  useEffect(() => {
    fetchLogs().catch(() => {
      setError("Unable to load health logs.");
    });
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setStatus("");

    try {
      await requestJson("/log", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          meals: form.meals,
          sleep: Number(form.sleep),
          mood: form.mood,
        }),
      });

      setForm(initialForm);
      await fetchLogs();
      setStatus("Log saved.");
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleSuggestion = async () => {
    setLoadingSuggestion(true);
    setError("");
    setStatus("");

    try {
      const data = await requestJson("/suggest", {
        method: "POST",
      });

      setSuggestion(data.suggestion);
      setSuggestionSource(data.source || "");
    } catch (suggestionError) {
      setError(suggestionError.message);
    } finally {
      setLoadingSuggestion(false);
    }
  };

  const handleClearLogs = async () => {
    const confirmed = window.confirm("Clear all saved logs?");
    if (!confirmed) {
      return;
    }

    setError("");
    setStatus("");

    try {
      await requestJson("/log", { method: "DELETE" });
      setLogs([]);
      setSuggestion("");
      setSuggestionSource("");
      setShowHistoryModal(false);
      setStatus("Logs cleared.");
    } catch (clearError) {
      setError(clearError.message);
    }
  };

  const recentLogs = logs.slice().reverse();
  const previewLogs = recentLogs.slice(0, 3);

  return (
    <div className="app-shell">
      <header className="hero">
        <h1 className="app-title">Health AI</h1>
        <p className="hero-copy">
          Log meals, sleep, and mood. Get one quick suggestion.
        </p>
      </header>

      <main className="grid">
        <section className="card panel-log">
          <h2>Daily Log</h2>
          <form onSubmit={handleSubmit} className="log-form">
            <label>
              Meals
              <textarea
                name="meals"
                value={form.meals}
                onChange={handleChange}
                placeholder="Oatmeal, salad, salmon..."
                required
              />
            </label>

            <label>
              Sleep Hours
              <input
                type="number"
                name="sleep"
                value={form.sleep}
                onChange={handleChange}
                min="0"
                step="0.5"
                placeholder="7.5"
                required
              />
            </label>

            <label>
              Mood
              <input
                type="text"
                name="mood"
                value={form.mood}
                onChange={handleChange}
                placeholder="Calm, tired, stressed..."
                required
              />
            </label>

            <button type="submit" disabled={submitting}>
              {submitting ? "Saving..." : "Save Log"}
            </button>
          </form>
        </section>

        <section className="card panel-suggestion">
          <div className="section-row">
            <div className="section-copy">
              <h2>AI Suggestion</h2>
              <p className="muted">
                Uses your latest entries to generate one actionable tip.
              </p>
            </div>
            <button
              className="action-button"
              type="button"
              onClick={handleSuggestion}
              disabled={loadingSuggestion}
            >
              {loadingSuggestion ? "Thinking..." : "Get Suggestion"}
            </button>
          </div>

          <div className="suggestion-box">
            {suggestion || "No suggestion yet."}
          </div>
          {suggestionSource ? (
            <p className="muted suggestion-meta">
              Source: {suggestionSource === "basic-local-engine" ? "basic local suggestion engine" : "OpenAI"}
            </p>
          ) : null}
        </section>

        <section className="card panel-chart">
          <h2>Sleep Trend</h2>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={logs}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(184, 255, 82, 0.14)" />
                <XAxis dataKey="date" stroke="#9ab3ff" tick={{ fill: "#9ab3ff" }} />
                <YAxis domain={[0, 12]} stroke="#9ab3ff" tick={{ fill: "#9ab3ff" }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(10, 12, 48, 0.96)",
                    border: "1px solid rgba(184, 255, 82, 0.22)",
                    borderRadius: "12px",
                    color: "#f1ffd8",
                  }}
                  labelStyle={{ color: "#b8ff52" }}
                />
                <Line
                  type="monotone"
                  dataKey="sleep"
                  stroke="#b8ff52"
                  strokeWidth={3}
                  dot={{ r: 4, fill: "#f1ffd8", stroke: "#b8ff52", strokeWidth: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="card panel-history">
          <div className="section-row">
            <h2>Log History</h2>
            <div className="history-actions">
              {logs.length > 3 ? (
                <button
                  className="action-button action-button-small"
                  type="button"
                  onClick={() => setShowHistoryModal(true)}
                >
                  Show More
                </button>
              ) : null}
              {logs.length > 0 ? (
                <button
                  className="ghost-button"
                  type="button"
                  onClick={handleClearLogs}
                >
                  Reset
                </button>
              ) : null}
            </div>
          </div>
          {logs.length === 0 ? (
            <p className="muted">No entries yet.</p>
          ) : (
            <div className="history">
              {previewLogs.map((entry, index) => (
                <article className="history-item" key={`${entry.date}-${index}`}>
                  <p className="history-date">{entry.date}</p>
                  <p><strong>Meals:</strong> {entry.meals}</p>
                  <p><strong>Sleep:</strong> {entry.sleep} hours</p>
                  <p><strong>Mood:</strong> {entry.mood}</p>
                </article>
              ))}
            </div>
          )}
        </section>
      </main>

      {showHistoryModal ? (
        <div className="modal-backdrop" onClick={() => setShowHistoryModal(false)}>
          <div
            className="modal-card"
            onClick={(event) => event.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-labelledby="history-modal-title"
          >
            <div className="modal-header">
              <h2 id="history-modal-title">Full Log History</h2>
              <div className="history-actions">
                {recentLogs.length > 0 ? (
                  <button
                    className="ghost-button"
                    type="button"
                    onClick={handleClearLogs}
                  >
                    Reset
                  </button>
                ) : null}
                <button
                  className="action-button action-button-small"
                  type="button"
                  onClick={() => setShowHistoryModal(false)}
                >
                  Close
                </button>
              </div>
            </div>

            {recentLogs.length === 0 ? (
              <p className="muted">No entries yet.</p>
            ) : (
              <div className="modal-history">
                {recentLogs.map((entry, index) => (
                  <article className="history-item" key={`modal-${entry.date}-${index}`}>
                    <p className="history-date">{entry.date}</p>
                    <p><strong>Meals:</strong> {entry.meals}</p>
                    <p><strong>Sleep:</strong> {entry.sleep} hours</p>
                    <p><strong>Mood:</strong> {entry.mood}</p>
                  </article>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : null}

      {status ? <p className="status-banner">{status}</p> : null}
      {error ? <p className="error-banner">{error}</p> : null}
    </div>
  );
}

export default App;
