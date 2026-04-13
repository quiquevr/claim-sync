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
