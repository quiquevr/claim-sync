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
        response = requests.get(FHIR_PATIENT_URL)
        response.raise_for_status()
        bundle = response.json()
        for entry in bundle.get("entry", []):
            self.on_new_record(entry["resource"])

    def on_new_record(self, resource: dict):
        mapped = _map_fhir_patient(resource)
        patient_store.upsert(mapped)

    def on_updated_record(self, resource: dict):
        mapped = _map_fhir_patient(resource)
        patient_store.upsert(mapped)
