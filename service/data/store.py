# Bot type definitions (keyed by type id)
bot_types = {
    "ehr": {
        "id": "ehr",
        "name": "EHR Connector",
        "description": "Pulls patient and clinical data from Electronic Health Record systems",
        "default_schedule": {"interval_minutes": 60, "retry_attempts": 3, "timeout_seconds": 300},
        "supported_sources": ["epic", "cerner", "allscripts", "athenahealth"],
        "uri": "/bot/ehr/",
        "on-create": "/patient/create",
        "on-update": "/patient/update",
    },
    "clearinghouse": {
        "id": "clearinghouse",
        "name": "Clearing House Connector",
        "description": "Retrieves claims and remittance data from healthcare clearing houses",
        "default_schedule": {"interval_minutes": 240, "retry_attempts": 2, "timeout_seconds": 600},
        "supported_sources": ["availity", "change_healthcare", "trizetto"],
        "uri": "/bot/clearinghouse/",
        "on-create": "/claim/create",
        "on-update": "/claim/update",
    },
    "payer": {
        "id": "payer",
        "name": "Payer Portal Connector",
        "description": "Fetches eligibility and authorization data from insurance payer portals",
        "default_schedule": {"interval_minutes": 120, "retry_attempts": 3, "timeout_seconds": 180},
        "supported_sources": ["unitedhealthcare", "anthem", "aetna", "cigna", "humana"],
        "uri": "/bot/payer/",
        "on-update": "/claim/update",
    },
}

# Bot instances keyed by (bot_type, account_id) tuple
bot_instances = {
    ("ehr", "acc_001"): {  # TEMP TEST
        "bot-instance-id": 1,
        "bot_type": "ehr",
        "account_id": "acc_001",
        "schedule": {
            "interval_minutes": 1,  # TEMP TEST (normally 60)
            "retry_attempts": 1,    # TEMP TEST (normally 3)
            "timeout_seconds": 30,  # TEMP TEST (normally 300)
            "start_date": 1711065600,
        },
        "max_concurrent_jobs": 1,   # TEMP TEST (normally 3)
        "priority": "high",
        "next-exec-date": 1711069200,
        "stats": {"processed": 42},
        "status": "SCHEDULED",
    },
    ("clearinghouse", "acc_002"): {
        "bot-instance-id": 2,
        "bot_type": "clearinghouse",
        "account_id": "acc_002",
        "schedule": {"interval_minutes": 240, "retry_attempts": 2, "timeout_seconds": 600, "start_date": 1711065600},
        "max_concurrent_jobs": 2,
        "priority": "normal",
        "next-exec-date": 1711080000,
        "stats": {"processed": 15},
        "status": "SCHEDULED",
    },
    ("payer", "acc_001"): {
        "bot-instance-id": 3,
        "bot_type": "payer",
        "account_id": "acc_001",
        "schedule": {"interval_minutes": 120, "retry_attempts": 3, "timeout_seconds": 180, "start_date": 1711065600},
        "max_concurrent_jobs": 5,
        "priority": "high",
        "next-exec-date": 1711072800,
        "stats": {"processed": 20},
        "status": "KILLED",
    },
}

# Auto-increment counter for bot instance IDs
_bot_instance_id_seq = 4

# Account+bot configs keyed by (account_id, bot_type) — value is a list of config objects
account_bot_configs = {
    ("acc_001", "ehr"): [
        {"settings": {"max_concurrent_jobs": 5, "priority": "high"}},
        {"settings": {"max_concurrent_jobs": 2, "priority": "normal"}},
    ],
    ("acc_001", "payer"): [
        {"settings": {"max_concurrent_jobs": 3, "priority": "high"}},
    ],
    ("acc_002", "clearinghouse"): [
        {"settings": {"max_concurrent_jobs": 1, "priority": "normal"}},
    ],
}

# Keyed by claim ID (str)
claims = {
    "claim_0001": {
        "id": "claim_0001",
        "account_id": "acc_001",
        "patient_id": 1,
        "payer_id": 101,
        "description": "Annual wellness visit",
        "date_of_service": "2024-01-15",
        "diagnosis": ["Hypertension"],
        "total_billed": 250.00,
        "ehr_status": "GENERATED",
        "clearing_house_status": "ACCEPTED",
        "payer_status": "PAID",
    },
    "claim_0002": {
        "id": "claim_0002",
        "account_id": "acc_002",
        "patient_id": 2,
        "payer_id": 202,
        "description": "Mild winter chobbyness",
        "date_of_service": "2024-03-22",
        "diagnosis": ["couch potato"],
        "total_billed": 666.66,
        "ehr_status": "GENERATED",
        "clearing_house_status": "ACCEPTED",
        "payer_status": "PENDING",
    },
    "claim_0003": {
        "id": "claim_0003",
        "account_id": "acc_001",
        "patient_id": 1,
        "payer_id": 101,
        "description": "Follow-up blood pressure check",
        "date_of_service": "2024-06-10",
        "diagnosis": ["Hypertension"],
        "total_billed": 120.00,
        "ehr_status": "GENERATED",
        "clearing_house_status": "PENDING",
        "payer_status": "PENDING",
    },
}

# Keyed by account ID (str)
accounts = {
    "acc_001": {"id": "acc_001", "name": "Sunrise Medical Group", "tier": "premium", "created_at": "2023-11-05T09:00:00Z"},
    "acc_002": {"id": "acc_002", "name": "Valley Health Clinic",  "tier": "standard", "created_at": "2024-03-22T14:30:00Z"},
    "acc_003": {"id": "acc_003", "name": "Oakwood Family Practice", "tier": "basic", "created_at": "2024-08-17T11:15:00Z"},
}

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
