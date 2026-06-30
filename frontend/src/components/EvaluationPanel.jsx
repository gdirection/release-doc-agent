export default function EvaluationPanel({ evaluation }) {
  if (!evaluation) {
    return (
      <section className="panel compact" aria-label="Evaluation">
        <h2>Evaluation</h2>
        <p className="muted">
          Run evaluation to measure hallucination rate, Jira coverage, and documentation
          recommendation accuracy.
        </p>
      </section>
    );
  }

  return (
    <section className="panel compact" aria-label="Evaluation">
      <h2>Evaluation</h2>
      <div className="item-list">
        {evaluation.metrics.map((metric) => (
          <article className="validation-row" key={metric.name}>
            <span className="chip">{formatPercent(metric.value)}</span>
            <div>
              <h3>{metric.name}</h3>
              <p>{metric.detail}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function formatPercent(value) {
  return `${Math.round(value * 100)}%`;
}
