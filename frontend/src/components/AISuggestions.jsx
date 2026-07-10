import './AISuggestions.css'

export default function AISuggestions({ suggestions, health, revivalMessage, onSelect, onClose, loading }) {
  return (
    <div className="ai-suggestions">
      <div className="suggestions-header">
        <span className="suggestions-title">✦ AI Reply Suggestions</span>
        <button className="suggestions-close" onClick={onClose}>✕</button>
      </div>

      {health !== 'healthy' && revivalMessage && (
        <div className={`health-badge ${health}`}>
          {health === 'dying' ? '⚠️' : '💬'} {revivalMessage}
        </div>
      )}

      {loading ? (
        <div className="suggestions-loading">
          <span className="loading-dot" />
          <span className="loading-dot" />
          <span className="loading-dot" />
          <p>Analyzing conversation...</p>
        </div>
      ) : (
        <div className="suggestions-list">
          {suggestions.map((s, i) => (
            <button key={i} className="suggestion-chip" onClick={() => onSelect(s)}>
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
