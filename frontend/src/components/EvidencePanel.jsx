export default function EvidencePanel({ releasePackage, changes }) {
  const evidence = releasePackage?.evidence ?? [];

  return (
    <section className="panel compact" aria-label="Evidence">
      <h2>Evidence</h2>
      {evidence.length === 0 ? (
        <p className="muted">No evidence loaded.</p>
      ) : (
        <div className="chips">
          {evidence.map((evidenceId) => (
            <span className="chip" key={evidenceId}>
              {evidenceId}
            </span>
          ))}
        </div>
      )}

      {changes.length > 0 && (
        <div className="section-block">
          <h3>Change Summaries</h3>
          <div className="item-list">
            {changes.map((change) => (
              <article className="item" key={change.id}>
                <h4>{change.id}</h4>
                <p>{change.title}</p>
                <span className={`risk ${change.risk_level}`}>{change.risk_level}</span>
                <div className="chips">
                  {change.source_ids.map((sourceId) => (
                    <span className="chip" key={sourceId}>
                      {sourceId}
                    </span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
