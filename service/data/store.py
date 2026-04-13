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
