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
