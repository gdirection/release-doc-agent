export default function RetrievedDocsPanel({ retrievedDocs }) {
  return (
    <section className="panel" aria-label="Retrieved documentation">
      <h2>Retrieved Documentation</h2>
      {retrievedDocs.length === 0 ? (
        <p className="muted">No retrieved documentation yet.</p>
      ) : (
        <div className="doc-grid">
          {retrievedDocs.map((doc) => (
            <article className="item" key={`${doc.change_id}-${doc.doc_chunk_id}`}>
              <div className="item-heading">
                <h3>{doc.doc_title}</h3>
                <span>{doc.heading}</span>
              </div>
              <p>{doc.content_preview}</p>
              <footer className="doc-meta">
                <span>{doc.change_id}</span>
                <span>score {doc.score}</span>
              </footer>
              <div className="chips">
                {doc.matched_terms.map((term) => (
                  <span className="chip" key={term}>
                    {term}
                  </span>
                ))}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
