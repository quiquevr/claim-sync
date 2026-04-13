from bots.observer_bot import ObserverBot
from data import claim_store

_SIMULATED_RECORDS = [
    {
        "id": "pay_auth_001",
        "account_id": "acc_001",
        "patient_id": "pat-123",
        "payer_id": "unitedhealthcare_001",
        "eligibility_status": "ELIGIBLE",
        "authorization_code": "AUTH_UC_88821",
        "authorization_date": "2024-03-20",
        "expiry_date": "2024-06-20",
    },
    {
        "id": "pay_auth_002",
        "account_id": "acc_001",
        "patient_id": "pat-456",
        "payer_id": "anthem_001",
        "eligibility_status": "INELIGIBLE",
        "authorization_code": None,
        "authorization_date": "2024-03-21",
        "expiry_date": None,
    },
    {
        "id": "pay_auth_003",
        "account_id": "acc_002",
        "patient_id": "pat-789",
        "payer_id": "cigna_001",
        "eligibility_status": "PENDING",
        "authorization_code": None,
        "authorization_date": "2024-03-22",
        "expiry_date": None,
    },
]


def _map_payer_record(record: dict) -> dict:
    return {
        "id":                    record["id"],
        "account_id":            record["account_id"],
        "patient_id":            record["patient_id"],
        "payer_id":              record["payer_id"],
        "payer_status":          record["eligibility_status"],
        "description":           f"Auth {record['authorization_code']} expires {record['expiry_date']}",
        "diagnosis":             [],
        "ehr_status":            "GENERATED",
        "clearing_house_status": "ACCEPTED",
        "total_billed":          0.00,
        "date_of_service":       record["authorization_date"],
    }


class PayerBot(ObserverBot):

    def execute(self):
        print("[BotScheduler] PayerBot | execute START | using hardcoded simulated data", flush=True)
        records = _SIMULATED_RECORDS
        print(f"[BotScheduler] PayerBot | execute FETCHED | record_count={len(records)}", flush=True)
        for record in records:
            self.on_new_record(record)

    def on_new_record(self, record: dict):
        mapped = _map_payer_record(record)
        print(f"[BotScheduler] PayerBot | on_new_record | auth_id={mapped['id']} eligibility={record['eligibility_status']}", flush=True)
        claim_store.upsert(mapped)

    def on_updated_record(self, record: dict):
        mapped = _map_payer_record(record)
        claim_store.upsert(mapped)
