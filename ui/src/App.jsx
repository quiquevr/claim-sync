import { useState, useCallback } from 'react'
import JobList from './components/JobList'
import MonitoringFeed from './components/MonitoringFeed'
import DetailActions from './components/DetailActions'

export default function App() {
  const [selectedJob, setSelectedJob] = useState(null)
  const [currentStatus, setCurrentStatus] = useState(null)
  const [refreshKey, setRefreshKey] = useState(0)

  const handleStatusChange = useCallback((status) => {
    setCurrentStatus(status)
  }, [])

  // Bump refreshKey to make MonitoringFeed re-mount and restart polling after an action
  const handleActionComplete = useCallback(() => {
    setRefreshKey(k => k + 1)
  }, [])

  return (
    <div className="app-shell">
      <div className="main-area">
        <JobList selectedJob={selectedJob} onSelect={setSelectedJob} />
        <MonitoringFeed
          key={refreshKey}
          selectedJob={selectedJob}
          onStatusChange={handleStatusChange}
        />
      </div>
      <DetailActions
        selectedJob={selectedJob}
        status={currentStatus}
        onActionComplete={handleActionComplete}
      />
    </div>
  )
}
