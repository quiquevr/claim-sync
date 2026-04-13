import pytest
from data import store


_ORIGINAL_PATIENTS = {
    1: {"id": 1, "gender": "female", "dob": "03-15-1990"},
    2: {"id": 2, "gender": "male",   "dob": "07-22-1985"},
}

_ORIGINAL_CLAIMS = {
    k: dict(v) for k, v in store.claims.items()
}


@pytest.fixture(autouse=True)
def reset_store():
    store.patients = {k: dict(v) for k, v in _ORIGINAL_PATIENTS.items()}
    store.claims = {k: dict(v) for k, v in _ORIGINAL_CLAIMS.items()}
    yield
    store.patients = {k: dict(v) for k, v in _ORIGINAL_PATIENTS.items()}
    store.claims = {k: dict(v) for k, v in _ORIGINAL_CLAIMS.items()}
