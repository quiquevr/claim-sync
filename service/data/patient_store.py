from data import store


def upsert(record: dict):
    """Insert or overwrite a patient record.

    Matches on string equality of the id field so both string and integer
    keys are handled without assuming type.
    """
    record_id = record["id"]

    # Check existing keys with string equality so "1" matches 1 and vice-versa
    for existing_key in list(store.patients.keys()):
        if str(existing_key) == str(record_id):
            store.patients[existing_key] = record
            return

    # New record — store under its native id type
    store.patients[record_id] = record
