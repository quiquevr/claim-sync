# JoyfulClaimSync UI — Architecture

## Overview

A simple single-page monitoring dashboard for the JoyfulClaimSync bot scheduling 
system. Built with React. Communicates with the existing Flask backend in `/services`
via REST. No database, no auth — pure operational visibility UI.

---

## Project Structure

```
joyful-claim-sync/
├── services/        # existing Flask backend
└── ui/
    ├── ARCHITECTURE.md
    ├── package.json
    ├── public/
    │   └── index.html
    └── src/
        ├── main.jsx                # entry point
        ├── App.jsx                 # root component, layout shell
        ├── api/
        │   └── botService.js       # all fetch() calls to the Flask backend
        ├── components/
        │   ├── JobList.jsx         # left panel — list of bot types
        │   ├── MonitoringFeed.jsx  # top right — live log feed for selected job
        │   └── DetailActions.jsx   # bottom — start time + start/stop buttons
        └── hooks/
            └── useBotPolling.js    # polling hook for status + log updates
```

---

## Layout

```
┌─────────────────────────────────────────────────┐
│  Jobs              │  Monitoring                 │
│  ┌─────────────┐   │  ┌───────────────────────┐  │
│  │ EHR         │   │  │ Live log feed for      │  │
│  │ Clearing    │   │  │ selected job, mirroring│  │
│  │   House     │   │  │ console print format:  │  │
│  │ Payer       │   │  │ [BotScheduler] ...     │  │
│  └─────────────┘   │  └───────────────────────┘  │
│                                                   │
│  Detail and actions                               │
│  ┌───────────────────────────────────────────┐   │
│  │ Start time: mm-dd-yyyy  [Start] [Stop]    │   │
│  └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## Components

### App.jsx
- Holds selected job state: `selectedJob` (one of: "ehr", "clearinghouse", "payer")
- Renders the three panel layout: JobList | MonitoringFeed / DetailActions
- Passes `selectedJob` and `onSelect` down to children

### JobList.jsx
- Renders a fixed list of the three bot types: EHR, Clearing House, Payer
- Highlights the currently selected job
- Calls `onSelect(botType)` on click

### MonitoringFeed.jsx
- Receives `selectedJob` as prop
- Polls `GET /bot/{type}/account/acc_001/status` every 3 seconds via `useBotPolling`
- Displays a scrolling feed of log-style entries mirroring the console print format:
    [BotScheduler] SchedulerWorker | loop TICK | type=ehr account=acc_001 next_in=1min
- Newest entries appear at the top
- Shows a placeholder message when no job is selected

### DetailActions.jsx
- Receives `selectedJob` and current status as props
- Displays: "Start time: {started_timestamp formatted as mm-dd-yyyy}"
- Start button: calls `PUT /bot/{type}/account/acc_001/schedule` with default schedule
- Stop button: calls `POST /bot/{type}/account/acc_001/kill`
- Buttons are disabled when no job is selected
- Start is disabled when job is already SCHEDULED
- Stop is disabled when job is KILLED or not yet started

---

## API Layer (api/botService.js)

All calls target `http://localhost:5000` (the Flask backend).

```javascript
// Get status for a bot instance
GET  /bot/{type}/account/acc_001/status

// Schedule a bot with default config (1 min interval for dev)
PUT  /bot/{type}/account/acc_001/schedule
Body: {
  "schedule": { "interval_minutes": 1, "retry_attempts": 1, "timeout_seconds": 30 },
  "max_concurrent_jobs": 1,
  "priority": "high"
}

// Kill a bot
POST /bot/{type}/account/acc_001/kill
```

---

## Polling & Log Feed (hooks/useBotPolling.js)

- Polls `/bot/{type}/account/acc_001/status` every 3 seconds
- Derives log entries from status response fields:
  `bot-instance-id`, `next-exec-date`, `status`, `stats.processed`
- Formats each poll result as a console-style log line and prepends to a local array:
    [BotScheduler] SchedulerWorker | loop TICK | type={type} account=acc_001 status={status} processed={n}
- Caps the feed at 50 entries to avoid unbounded growth
- Clears the feed when `selectedJob` changes

---

## Tech Stack

- **Framework:** React 18 (Vite)
- **Styling:** plain CSS, no component library
- **HTTP:** native fetch()
- **State:** useState + useEffect only, no external state manager

---

## Dev Setup

```bash
cd joyful-claim-sync/ui
npm create vite@latest . -- --template react
npm install
npm run dev       # runs on http://localhost:5173
```

Flask backend must be running on `http://localhost:5000` for API calls to work.
CORS must be enabled on the Flask side — add `flask-cors` and `CORS(app)` in `services/app.py`.

---

## Key Implementation Notes

- `acc_001` is hardcoded as the test account throughout the UI — this matches the
  TEMP TEST seed data in the backend.
- The monitoring feed is simulated from polling — it is not a real log stream.
  Each poll result generates one new log line.
- All three bot types share the same account (`acc_001`) for simplicity.
- Do not add routing, auth, or multiple account support — keep it as a single
  focused monitoring page.
