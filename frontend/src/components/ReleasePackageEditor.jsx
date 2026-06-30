export default function ReleasePackageEditor({ releasePackage, onChange }) {
  if (!releasePackage) {
    return (
      <section className="panel" aria-label="Release package editor">
        <h2>Release Package</h2>
        <p className="muted">Generate a release package to review changelog, notes, and doc updates.</p>
      </section>
    );
  }

  function updateField(field, value) {
    onChange({ ...releasePackage, [field]: value });
  }

  return (
    <section className="panel" aria-label="Release package editor">
      <h2>Release Package</h2>

      <div className="section-block">
        <h3>Changelog</h3>
        <div className="item-list">
          {releasePackage.changelog.map((item) => (
            <article className="item" key={item.title}>
              <h4>{item.title}</h4>
              <p>{item.summary}</p>
              <EvidenceList evidenceIds={item.evidence_ids} />
            </article>
          ))}
        </div>
      </div>

      <label className="field">
        <span>Internal Release Notes</span>
        <textarea
          value={releasePackage.internal_release_notes}
          onChange={(event) => updateField("internal_release_notes", event.target.value)}
          rows={5}
        />
      </label>

      <label className="field">
        <span>Customer Release Notes</span>
        <textarea
          value={releasePackage.customer_release_notes}
          onChange={(event) => updateField("customer_release_notes", event.target.value)}
          rows={4}
        />
      </label>

      <div className="section-block">
        <h3>Documentation Updates</h3>
        <div className="item-list">
          {releasePackage.documentation_updates.map((update) => (
            <article className="item" key={update.doc_chunk_id}>
              <div className="item-heading">
                <h4>{update.doc_title}</h4>
                <span>{update.section}</span>
              </div>
              <p>{update.suggested_change}</p>
              <p className="muted">{update.reason}</p>
              <EvidenceList evidenceIds={update.evidence_ids} />
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

function EvidenceList({ evidenceIds }) {
  return (
    <div className="chips" aria-label="Evidence IDs">
      {evidenceIds.map((evidenceId) => (
        <span className="chip" key={evidenceId}>
          {evidenceId}
        </span>
      ))}
    </div>
  );
}
