const JOBS = [
  { id: 'ehr',           label: 'EHR' },
  { id: 'clearinghouse', label: 'Clearing House' },
  { id: 'payer',         label: 'Payer' },
]

export default function JobList({ selectedJob, onSelect }) {
  return (
    <div className="job-list">
      <div className="panel-header">Jobs</div>
      <ul>
        {JOBS.map(job => (
          <li
            key={job.id}
            className={`job-item${selectedJob === job.id ? ' job-item--selected' : ''}`}
            onClick={() => onSelect(job.id)}
          >
            {job.label}
          </li>
        ))}
      </ul>
    </div>
  )
}
