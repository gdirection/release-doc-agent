import { useState } from "react";

import { approveReleasePackage, evaluateReleasePackage, generateReleasePackage } from "./api.js";
import EvaluationPanel from "./components/EvaluationPanel.jsx";
import EvidencePanel from "./components/EvidencePanel.jsx";
import ReleasePackageEditor from "./components/ReleasePackageEditor.jsx";
import RetrievedDocsPanel from "./components/RetrievedDocsPanel.jsx";
import ValidationPanel from "./components/ValidationPanel.jsx";

const emptyResult = {
  changes: [],
  retrieved_docs: [],
  release_package: null,
  doc_review: [],
  validation_results: [],
};

export default function App() {
  const [data, setData] = useState(emptyResult);
  const [releasePackage, setReleasePackage] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [approved, setApproved] = useState(null);
  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [approving, setApproving] = useState(false);
  const [error, setError] = useState("");

  async function handleGenerate() {
    setLoading(true);
    setError("");
    setApproved(null);
    setEvaluation(null);

    try {
      const payload = await generateReleasePackage();
      setData(payload);
      setReleasePackage(payload.release_package);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleEvaluate() {
    setEvaluating(true);
    setError("");

    try {
      const payload = await evaluateReleasePackage();
      setEvaluation(payload.evaluation);
    } catch (err) {
      setError(err.message);
    } finally {
      setEvaluating(false);
    }
  }

  async function handleApprove() {
    if (!releasePackage) {
      return;
    }

    setApproving(true);
    setError("");

    try {
      const payload = await approveReleasePackage(releasePackage);
      setApproved(payload);
    } catch (err) {
      setError(err.message);
    } finally {
      setApproving(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <h1>Automated Release Documentation Agent</h1>
          <p>Okta SSO release package review</p>
        </div>
        <div className="actions">
          <button type="button" onClick={handleGenerate} disabled={loading}>
            {loading ? "Generating..." : "Generate Release Package"}
          </button>
          <button type="button" onClick={handleEvaluate} disabled={evaluating}>
            {evaluating ? "Evaluating..." : "Run Evaluation"}
          </button>
          <button type="button" onClick={handleApprove} disabled={!releasePackage || approving}>
            {approving ? "Approving..." : "Approve Release Package"}
          </button>
        </div>
      </header>

      {error && <div className="banner error">{error}</div>}
      {approved && (
        <div className="banner success">Approved at {approved.approved_at}</div>
      )}

      <section className="summary-strip">
        <Metric label="Changes" value={data.changes.length} />
        <Metric label="Retrieved Docs" value={data.retrieved_docs.length} />
        <Metric label="Doc Updates" value={releasePackage?.documentation_updates?.length ?? 0} />
        <Metric label="Validation" value={data.validation_results.length} />
      </section>

      <div className="layout">
        <ReleasePackageEditor releasePackage={releasePackage} onChange={setReleasePackage} />
        <aside className="side-panel">
          <ValidationPanel validationResults={data.validation_results} />
          <EvaluationPanel evaluation={evaluation} />
          <EvidencePanel releasePackage={releasePackage} changes={data.changes} />
        </aside>
      </div>

      <RetrievedDocsPanel retrievedDocs={data.retrieved_docs} />
    </main>
  );
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
