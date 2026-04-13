# PatientService — Architecture

## Overview

A simple REST API built with **Python + Flask** that simulates a patient management service. There is no database — all data is stored in **in-memory Python dictionaries** to simulate DB behavior during development.

---

## Tech Stack

- **Language:** Python 3
- **Framework:** Flask
- **Database:** None (hardcoded in-memory data store)

---

## Project Structure

```
patient-service/
├── app.py               # Flask app entry point
├── routes/
│   └── patient.py       # All /patient routes
├── data/
│   └── store.py         # In-memory fake DB (dicts + lists)
└── requirements.txt
```

---

## Data Models

### Patient
```json
{
  "id": 123,
  "gender": "male | female",
  "dob": "mm-dd-yyyy"
}
```

### Condition
```json
{
  "id": 123,
  "condition": "<desc>",
  "diagnosis_code": 123,
  "diagnosis_start_date": "mm-dd-yyyy",
  "diagnosis_end_date": "mm-dd-yyyy"
}
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/patient/create` | Create a new patient |
| PUT | `/patient/update` | Update an existing patient |
| GET | `/patient/list` | List all patients |
| GET | `/patient/<id>` | Get a single patient by ID |
| GET | `/patient/<id>/conditions` | Get all conditions for a patient |

---

## In-Memory Data Store (`data/store.py`)

All "database" access is simulated via module-level dictionaries. No persistence between restarts.

```python
# Keyed by patient ID (int)
patients = {
    1: {"id": 1, "gender": "female", "dob": "03-15-1990"},
    2: {"id": 2, "gender": "male",   "dob": "07-22-1985"},
}

# Keyed by patient ID, value is a list of conditions
conditions = {
    1: [
        {
            "id": 101,
            "condition": "Hypertension",
            "diagnosis_code": 401,
            "diagnosis_start_date": "01-10-2020",
            "diagnosis_end_date": None,
        }
    ],
    2: [],
}
```

---

## Key Implementation Notes

- All route handlers import directly from `data/store.py` — no ORM, no session, no queries.
- IDs are auto-incremented using `max(patients.keys()) + 1` on create.
- Return `404` JSON if a patient ID is not found.
- All responses are JSON (`flask.jsonify`).
- The store module is the single source of truth — treat it exactly as you would a DB layer so it's easy to swap in a real DB later.
