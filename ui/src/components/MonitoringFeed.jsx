import { useBotPolling } from '../hooks/useBotPolling'

export default function MonitoringFeed({ selectedJob, onStatusChange }) {
  const { status, feed, error } = useBotPolling(selectedJob)

  // Bubble current status up to App so DetailActions can use it
  if (onStatusChange) {
    onStatusChange(status)
  }

  return (
    <div className="monitoring-feed">
      <div className="panel-header">Monitoring{selectedJob ? ` — ${selectedJob}` : ''}</div>
      <div className="feed-body">
        {!selectedJob && (
          <span className="feed-placeholder">Select a job from the left panel to start monitoring.</span>
        )}
        {selectedJob && feed.length === 0 && !error && (
          <span className="feed-placeholder">Waiting for first poll…</span>
        )}
        {feed.map((line, i) => (
          <div key={i} className="feed-line">{line}</div>
        ))}
      </div>
    </div>
  )
}
