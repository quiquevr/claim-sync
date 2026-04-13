from data import store


def upsert(record: dict):
    """Insert or overwrite a claim record.

    Matches on string equality of the id field so both string and integer
    keys are handled without assuming type.
    """
    record_id = record["id"]

    for existing_key in list(store.claims.keys()):
        if str(existing_key) == str(record_id):
            store.claims[existing_key] = record
            return

    store.claims[record_id] = record
