import logging

import requests

from bots.observer_bot import ObserverBot
from data import patient_store

logger = logging.getLogger(__name__)

FHIR_PATIENT_URL = "http://hapi.fhir.org/baseR4/Patient"


def _map_fhir_patient(resource: dict) -> dict:
    return {
        "id": resource.get("id"),
        "gender": resource.get("gender", "unknown"),
        "dob": resource.get("birthDate", ""),
    }


class EHRBot(ObserverBot):

    def execute(self):
        print("[BotScheduler] EHRBot | execute START | fetching from FHIR", flush=True)  # TEMP TEST
        response = requests.get(FHIR_PATIENT_URL)
        response.raise_for_status()
        bundle = response.json()
        entries = bundle.get("entry", [])
        print(f"[BotScheduler] EHRBot | execute FETCHED | record_count={len(entries)}", flush=True)  # TEMP TEST
        for entry in entries:
            self.on_new_record(entry["resource"])

    def on_new_record(self, resource: dict):
        mapped = _map_fhir_patient(resource)
        print(f"[BotScheduler] EHRBot | on_new_record | patient_id={mapped['id']} gender={mapped['gender']} dob={mapped['dob']}", flush=True)  # TEMP TEST
        patient_store.upsert(mapped)

    def on_updated_record(self, resource: dict):
        mapped = _map_fhir_patient(resource)
        print(f"[BotScheduler] EHRBot | on_updated_record | patient_id={mapped['id']}", flush=True)  # TEMP TEST
        patient_store.upsert(mapped)
