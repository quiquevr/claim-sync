# Joyful Claim Sync — Service

A Flask REST API simulating a healthcare claim sync platform. All data is stored in-memory (no database). The service includes a scheduling engine that runs bots to pull data from external sources (EHR, clearing house, payer portals).

---

## Project Structure

```
service/
├── app.py                   # Flask entry point
├── requirements.txt
├── routes/
│   ├── patient.py           # /patient endpoints
│   ├── account.py           # /account endpoints
│   ├── claim.py             # /claim endpoints
│   └── bot.py               # /bot and /puppet endpoints
├── data/
│   ├── store.py             # In-memory data store (seed data)
│   ├── patient_store.py     # Patient upsert logic
│   └── claim_store.py       # Claim upsert logic
├── bots/
│   ├── observer_bot.py      # Abstract base class
│   ├── ehr_bot.py           # Pulls FHIR patient data
│   ├── clearinghouse_bot.py # Simulates clearing house claim data
│   ├── payer_bot.py         # Simulates payer eligibility data
│   ├── bot_factory.py       # Returns the right bot for a given type
│   ├── scheduler_worker.py  # Per-bot retry + interval loop
│   └── master_of_puppets.py # Manages all active workers
└── tests/
    ├── conftest.py
    └── test_schedule_engine.py
```

---

## Setup

### 1. Create and activate a virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the server

```bash
python app.py
```

The server starts at **http://localhost:5000**.

### 4. Run tests

```bash
python -m pytest tests/ -v
```

---

## API Reference

### PatientService

| Method | Endpoint | Description | Example curl |
|--------|----------|-------------|--------------|
| GET | `/patient/list` | List all patients | `curl http://localhost:5000/patient/list` |
| GET | `/patient/<id>` | Get patient by ID | `curl http://localhost:5000/patient/1` |
| POST | `/patient/create` | Create a new patient | `curl -X POST http://localhost:5000/patient/create -H "Content-Type: application/json" -d '{"gender":"female","dob":"05-10-1992"}'` |
| PUT | `/patient/update` | Update an existing patient | `curl -X PUT http://localhost:5000/patient/update -H "Content-Type: application/json" -d '{"id":1,"gender":"male"}'` |
| GET | `/patient/<id>/conditions` | List conditions for a patient | `curl http://localhost:5000/patient/1/conditions` |

---

### AccountService

| Method | Endpoint | Description | Example curl |
|--------|----------|-------------|--------------|
| GET | `/account/list` | List all accounts | `curl http://localhost:5000/account/list` |
| GET | `/account/<id>` | Get account by ID | `curl http://localhost:5000/account/acc_001` |
| GET | `/account/<id>/bot/<type>/config` | Get bot configs for an account+type | `curl http://localhost:5000/account/acc_001/bot/ehr/config` |

---

### ClaimService

| Method | Endpoint | Description | Example curl |
|--------|----------|-------------|--------------|
| GET | `/claim/list` | List all claims | `curl http://localhost:5000/claim/list` |
| GET | `/claim/<id>` | Get claim by ID | `curl http://localhost:5000/claim/claim_0001` |
| PUT | `/claim/<id>/update` | Update claim status fields | `curl -X PUT http://localhost:5000/claim/claim_0001/update -H "Content-Type: application/json" -d '{"payer_status":"PAID","ehr_status":"SENT","clearing_house_status":"ACCEPTED"}'` |

> Only `ehr_status`, `clearing_house_status`, and `payer_status` are updatable. Any other field returns 400.

---

### BotService

| Method | Endpoint | Description | Example curl |
|--------|----------|-------------|--------------|
| GET | `/bot/types` | List all registered bot types | `curl http://localhost:5000/bot/types` |
| GET | `/bot/<type>/account/list` | List bot instances for a type | `curl http://localhost:5000/bot/ehr/account/list` |
| GET | `/bot/<type>/account/<id>/status` | Get status of a bot instance | `curl http://localhost:5000/bot/ehr/account/acc_001/status` |
| PUT | `/bot/<type>/account/<id>/schedule` | Create or update a bot schedule | `curl -X PUT http://localhost:5000/bot/ehr/account/acc_001/schedule -H "Content-Type: application/json" -d '{"schedule":{"interval_minutes":1,"retry_attempts":1,"timeout_seconds":30},"max_concurrent_jobs":1,"priority":"high"}'` |
| POST | `/bot/<type>/account/<id>/kill` | Kill a running bot instance | `curl -X POST http://localhost:5000/bot/ehr/account/acc_001/kill` |
| POST | `/puppet/master-of/start-all` | Schedule all registered bot instances | `curl -X POST http://localhost:5000/puppet/master-of/start-all` |
| POST | `/puppet/master-of/kill-em-all` | Kill all running bot instances | `curl -X POST http://localhost:5000/puppet/master-of/kill-em-all` |

Valid bot types: `ehr`, `clearinghouse`, `payer`.

---

## Seeded Data

The store is pre-populated with the following IDs for testing:

| Type | IDs |
|------|-----|
| Accounts | `acc_001`, `acc_002`, `acc_003` |
| Patients | `1`, `2` |
| Claims | `claim_0001`, `claim_0002`, `claim_0003` |
| Bot instances | `(ehr, acc_001)`, `(clearinghouse, acc_002)`, `(payer, acc_001)` |
