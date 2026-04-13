from bots.observer_bot import ObserverBot
from data import claim_store

_SIMULATED_RECORDS = [
    {
        "id": "ch_claim_001",
        "account_id": "acc_001",
        "patient_id": "pat-123",
        "payer_id": "availity_001",
        "status": "ACCEPTED",
        "remittance_amount": 450.00,
        "processed_date": "2024-03-22",
    },
    {
        "id": "ch_claim_002",
        "account_id": "acc_001",
        "patient_id": "pat-456",
        "payer_id": "change_healthcare_001",
        "status": "REJECTED",
        "remittance_amount": 0.00,
        "processed_date": "2024-03-22",
    },
    {
        "id": "ch_claim_003",
        "account_id": "acc_002",
        "patient_id": "pat-789",
        "payer_id": "trizetto_001",
        "status": "PENDING",
        "remittance_amount": 0.00,
        "processed_date": "2024-03-22",
    },
]


def _map_ch_claim(record: dict) -> dict:
    return {
        "id":                    record["id"],
        "account_id":            record["account_id"],
        "patient_id":            record["patient_id"],
        "payer_id":              record["payer_id"],
        "clearing_house_status": record["status"],
        "total_billed":          record["remittance_amount"],
        "date_of_service":       record["processed_date"],
        "description":           "Imported from clearing house",
        "diagnosis":             [],
        "ehr_status":            "GENERATED",
        "payer_status":          "PENDING",
    }


class ClearingHouseBot(ObserverBot):

    def execute(self):
        print("[BotScheduler] ClearingHouseBot | execute START | using hardcoded simulated data", flush=True)
        records = _SIMULATED_RECORDS
        print(f"[BotScheduler] ClearingHouseBot | execute FETCHED | record_count={len(records)}", flush=True)
        for record in records:
            self.on_new_record(record)

    def on_new_record(self, record: dict):
        mapped = _map_ch_claim(record)
        print(f"[BotScheduler] ClearingHouseBot | on_new_record | claim_id={mapped['id']} status={record['status']}", flush=True)
        claim_store.upsert(mapped)

    def on_updated_record(self, record: dict):
        mapped = _map_ch_claim(record)
        claim_store.upsert(mapped)
