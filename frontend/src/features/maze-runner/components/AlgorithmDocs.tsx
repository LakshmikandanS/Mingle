import type { AlgorithmDocumentationResponse } from '../../../types/maze';
import { formatCategory } from '../mapping';
import './AlgorithmDocs.css';

interface AlgorithmDocsProps {
  documentation: AlgorithmDocumentationResponse | null;
  isLoading: boolean;
  onClose: () => void;
}

export function AlgorithmDocs({ documentation, isLoading, onClose }: AlgorithmDocsProps) {
  if (isLoading) {
    return (
      <div className="algo-docs-overlay" onClick={onClose}>
        <div className="algo-docs-panel" onClick={(e) => e.stopPropagation()}>
          <div className="algo-docs-loading">Loading documentation…</div>
        </div>
      </div>
    );
  }

  if (!documentation) return null;

  const doc = documentation;

  return (
    <div className="algo-docs-overlay" onClick={onClose}>
      <div className="algo-docs-panel" onClick={(e) => e.stopPropagation()}>
        <div className="algo-docs-header">
          <h2 className="algo-docs-title">{doc.name}</h2>
          <button className="algo-docs-close" onClick={onClose} aria-label="Close">✕</button>
        </div>

        <span className="algo-docs-category">{formatCategory(doc.category)}</span>

        <p className="algo-docs-description">{doc.description}</p>

        {doc.core_idea && (
          <section className="algo-docs-section">
            <h3 className="algo-docs-section-title">Core Idea</h3>
            <p className="algo-docs-text">{doc.core_idea}</p>
          </section>
        )}

        {doc.pseudocode && doc.pseudocode.length > 0 && (
          <section className="algo-docs-section">
            <h3 className="algo-docs-section-title">Pseudocode</h3>
            <pre className="algo-docs-code">
              <code>{doc.pseudocode.join('\n')}</code>
            </pre>
          </section>
        )}

        {doc.step_by_step && doc.step_by_step.length > 0 && (
          <section className="algo-docs-section">
            <h3 className="algo-docs-section-title">Step by Step</h3>
            <ol className="algo-docs-steps">
              {doc.step_by_step.map((step, i) => (
                <li key={i}>{step}</li>
              ))}
            </ol>
          </section>
        )}

        <section className="algo-docs-section">
          <h3 className="algo-docs-section-title">Properties</h3>
          <div className="algo-docs-properties">
            <DocProperty label="Data Structure" value={doc.data_structure} />
            <DocProperty label="Complete" value={doc.completeness} />
            <DocProperty label="Optimal" value={doc.optimality} />
            <DocProperty label="Time Complexity" value={doc.time_complexity} />
            <DocProperty label="Space Complexity" value={doc.space_complexity} />
            <DocProperty label="Heuristic" value={doc.heuristic_requirements} />
            <DocProperty label="Weighted Costs" value={doc.weighted_cost_requirements} />
          </div>
        </section>

        {doc.implementation_notes && (
          <section className="algo-docs-section">
            <h3 className="algo-docs-section-title">Mingle Notes</h3>
            <p className="algo-docs-text">{doc.implementation_notes}</p>
          </section>
        )}
      </div>
    </div>
  );
}

function DocProperty({ label, value }: { label: string; value: string }) {
  if (!value) return null;
  return (
    <div className="doc-property">
      <span className="doc-property-label">{label}</span>
      <span className="doc-property-value">{value}</span>
    </div>
  );
}
