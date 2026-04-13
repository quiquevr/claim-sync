# Joyful Claim Sync — UI

A single-page monitoring dashboard for the JoyfulClaimSync bot scheduling system. Built with React + Vite. Communicates with the Flask backend via REST.

---

## Project Structure

```
ui/
├── index.html
├── vite.config.js
├── package.json
└── src/
    ├── main.jsx                  # Entry point
    ├── App.jsx                   # Root component, layout shell, shared state
    ├── App.css                   # Three-panel layout and all styles
    ├── api/
    │   └── botService.js         # fetch() wrappers for the Flask backend
    ├── components/
    │   ├── JobList.jsx           # Left panel — list of bot types
    │   ├── MonitoringFeed.jsx    # Top right — live log feed for selected job
    │   └── DetailActions.jsx     # Bottom strip — start time + start/stop buttons
    └── hooks/
        └── useBotPolling.js      # Polling hook: status + log feed updates
```

---

## Setup & Running

### 1. Install dependencies (first time only)

```bash
cd joyful-claim-sync/ui
npm install
```

### 2. Start the Flask backend (required)

Open a terminal and run:

```bash
cd joyful-claim-sync/service
python app.py
# → running on http://localhost:5000
```

### 3. Start the UI dev server

Open a second terminal and run:

```bash
cd joyful-claim-sync/ui
npm run dev
# → running on http://localhost:5173
```

Then open **http://localhost:5173** in your browser.

> Both processes must be running at the same time. The UI will show network errors in the feed if the backend is not up.

---

## Layout

```
┌─────────────────────────────────────────────────┐
│  Jobs              │  Monitoring                 │
│  ┌─────────────┐   │  ┌───────────────────────┐  │
│  │ EHR         │   │  │ [BotScheduler] ...     │  │
│  │ Clearing    │   │  │ [BotScheduler] ...     │  │
│  │   House     │   │  │ [BotScheduler] ...     │  │
│  │ Payer       │   │  └───────────────────────┘  │
│  └─────────────┘   │                             │
├────────────────────────────────────────────────-─┤
│  Start time: mm-dd-yyyy          [Start] [Stop]  │
└─────────────────────────────────────────────────┘
```

---

## Components

### `JobList.jsx`
Static list of the three bot types (`ehr`, `clearinghouse`, `payer`). Clicking a row selects it and starts monitoring.

### `MonitoringFeed.jsx`
Polls `GET /bot/{type}/account/acc_001/status` every 3 seconds via `useBotPolling`. Renders log lines newest-first in a dark monospace terminal panel. Shows a placeholder when no job is selected.

### `DetailActions.jsx`
Displays the next scheduled execution date and two action buttons:

| Button | Color | Disabled when |
|--------|-------|---------------|
| Start | Green | No job selected, or status is `SCHEDULED` |
| Stop | Red | No job selected, or status is `KILLED` / not started |

Calls `PUT /bot/{type}/account/acc_001/schedule` (Start) and `POST /bot/{type}/account/acc_001/kill` (Stop).

### `useBotPolling.js`
- Polls every **3 seconds**
- Prepends each result as a console-style log line
- Caps the feed at **50 entries**
- Clears the feed when the selected job changes

---

## API

All calls target `http://localhost:5000`. The account is hardcoded to `acc_001`.

| Function | Method | Endpoint |
|----------|--------|----------|
| `getStatus(type)` | GET | `/bot/{type}/account/acc_001/status` |
| `scheduleBOT(type)` | PUT | `/bot/{type}/account/acc_001/schedule` |
| `killBot(type)` | POST | `/bot/{type}/account/acc_001/kill` |

Default schedule payload used by Start:
```json
{
  "schedule": { "interval_minutes": 1, "retry_attempts": 1, "timeout_seconds": 30 },
  "max_concurrent_jobs": 1,
  "priority": "high"
}
```

---

## Tech Stack

- **React 18** (Vite)
- **Plain CSS** — no component library, no Tailwind
- **Native fetch()** — no HTTP client library
- **useState + useEffect** — no external state manager
