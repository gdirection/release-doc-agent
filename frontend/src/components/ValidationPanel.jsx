export default function ValidationPanel({ validationResults }) {
  return (
    <section className="panel compact" aria-label="Validation">
      <h2>Validation</h2>
      {validationResults.length === 0 ? (
        <p className="muted">No validation results.</p>
      ) : (
        <div className="item-list">
          {validationResults.map((result) => (
            <article className="validation-row" key={result.code}>
              <span className={`status ${result.level}`}>{result.level}</span>
              <div>
                <h3>{result.code}</h3>
                <p>{result.message}</p>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
