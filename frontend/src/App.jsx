import { useState } from "react";

import { approveReleasePackage, generateReleasePackage } from "./api.js";
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
  const [result, setResult] = useState(emptyResult);
  const [releasePackage, setReleasePackage] = useState(null);
  const [approvedResponse, setApprovedResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [approving, setApproving] = useState(false);
  const [error, setError] = useState("");

  async function handleGenerate() {
    setLoading(true);
    setError("");
    setApprovedResponse(null);

    try {
      const payload = await generateReleasePackage();
      setResult(payload);
      setReleasePackage(payload.release_package);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
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
      setApprovedResponse(payload);
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
          <h1>Release Documentation Agent</h1>
          <p>Okta SSO release package review</p>
        </div>
        <div className="actions">
          <button type="button" onClick={handleGenerate} disabled={loading}>
            {loading ? "Generating..." : "Generate"}
          </button>
          <button type="button" onClick={handleApprove} disabled={!releasePackage || approving}>
            {approving ? "Approving..." : "Approve"}
          </button>
        </div>
      </header>

      {error && <div className="banner error">{error}</div>}
      {approvedResponse && (
        <div className="banner success">Approved at {approvedResponse.approved_at}</div>
      )}

      <section className="summary-strip">
        <Metric label="Changes" value={result.changes.length} />
        <Metric label="Retrieved Docs" value={result.retrieved_docs.length} />
        <Metric label="Doc Updates" value={releasePackage?.documentation_updates?.length ?? 0} />
        <Metric label="Validation" value={result.validation_results.length} />
      </section>

      <div className="layout">
        <ReleasePackageEditor releasePackage={releasePackage} onChange={setReleasePackage} />
        <aside className="side-panel">
          <ValidationPanel validationResults={result.validation_results} />
          <EvidencePanel releasePackage={releasePackage} changes={result.changes} />
        </aside>
      </div>

      <RetrievedDocsPanel retrievedDocs={result.retrieved_docs} />
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
