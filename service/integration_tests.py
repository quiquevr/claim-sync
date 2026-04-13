"""
Integration tests for all service endpoints.

Run against a live server:
    python integration_tests.py                      # defaults to http://localhost:5000
    python integration_tests.py http://localhost:8080

Each test function receives a requests.Session and the base URL.
A PASS/FAIL summary is printed at the end; exits with code 1 if any test failed.
"""

import sys
import json
import requests

BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:5000"

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"

results = []


def test(name, fn, session):
    try:
        fn(session)
        results.append((True, name))
        print(f"  {PASS}  {name}")
    except AssertionError as e:
        results.append((False, name))
        print(f"  {FAIL}  {name}")
        print(f"         {e}")


def assert_status(r, expected):
    assert r.status_code == expected, (
        f"Expected HTTP {expected}, got {r.status_code}. Body: {r.text[:200]}"
    )


def assert_keys(obj, *keys):
    for k in keys:
        assert k in obj, f"Missing key '{k}' in {list(obj.keys())}"


# ===========================================================================
# PatientService
# ===========================================================================

def test_patient_list(s):
    r = s.get(f"{BASE_URL}/patient/list")
    assert_status(r, 200)
    data = r.json()
    assert isinstance(data, list), "Expected a list"
    assert len(data) >= 2, "Expected at least 2 seeded patients"


def test_patient_get_found(s):
    r = s.get(f"{BASE_URL}/patient/1")
    assert_status(r, 200)
    assert_keys(r.json(), "id", "gender", "dob")


def test_patient_get_not_found(s):
    r = s.get(f"{BASE_URL}/patient/999999")
    assert_status(r, 404)
    assert "error" in r.json()


def test_patient_create(s):
    r = s.post(f"{BASE_URL}/patient/create", json={"gender": "female", "dob": "01-01-2000"})
    assert_status(r, 201)
    body = r.json()
    assert_keys(body, "id", "gender", "dob")
    assert body["gender"] == "female"


def test_patient_create_missing_fields(s):
    r = s.post(f"{BASE_URL}/patient/create", json={"gender": "male"})
    assert_status(r, 400)
    assert "error" in r.json()


def test_patient_update(s):
    r = s.put(f"{BASE_URL}/patient/update", json={"id": 1, "gender": "male"})
    assert_status(r, 200)
    assert r.json()["gender"] == "male"


def test_patient_update_missing_id(s):
    r = s.put(f"{BASE_URL}/patient/update", json={"gender": "male"})
    assert_status(r, 400)
    assert "error" in r.json()


def test_patient_update_not_found(s):
    r = s.put(f"{BASE_URL}/patient/update", json={"id": 999999, "gender": "male"})
    assert_status(r, 404)
    assert "error" in r.json()


def test_patient_conditions_found(s):
    r = s.get(f"{BASE_URL}/patient/1/conditions")
    assert_status(r, 200)
    assert isinstance(r.json(), list)


def test_patient_conditions_not_found(s):
    r = s.get(f"{BASE_URL}/patient/999999/conditions")
    assert_status(r, 404)
    assert "error" in r.json()


# ===========================================================================
# AccountService
# ===========================================================================

def test_account_list(s):
    r = s.get(f"{BASE_URL}/account/list")
    assert_status(r, 200)
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 3, "Expected at least 3 seeded accounts"


def test_account_get_found(s):
    r = s.get(f"{BASE_URL}/account/acc_001")
    assert_status(r, 200)
    assert_keys(r.json(), "id", "name", "tier", "created_at")


def test_account_get_not_found(s):
    r = s.get(f"{BASE_URL}/account/acc_does_not_exist")
    assert_status(r, 404)
    assert "error" in r.json()


def test_account_bot_config_found(s):
    r = s.get(f"{BASE_URL}/account/acc_001/bot/ehr/config")
    assert_status(r, 200)
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert_keys(data[0], "settings")


def test_account_bot_config_empty(s):
    # Valid account + valid bot type but no config seeded → empty list, not 404
    r = s.get(f"{BASE_URL}/account/acc_003/bot/ehr/config")
    assert_status(r, 200)
    assert r.json() == []


def test_account_bot_config_bad_account(s):
    r = s.get(f"{BASE_URL}/account/acc_nope/bot/ehr/config")
    assert_status(r, 404)
    assert "error" in r.json()


def test_account_bot_config_bad_type(s):
    r = s.get(f"{BASE_URL}/account/acc_001/bot/unknown_type/config")
    assert_status(r, 404)
    assert "error" in r.json()


# ===========================================================================
# ClaimService
# ===========================================================================

def test_claim_list(s):
    r = s.get(f"{BASE_URL}/claim/list")
    assert_status(r, 200)
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 3, "Expected at least 3 seeded claims"


def test_claim_get_found(s):
    r = s.get(f"{BASE_URL}/claim/claim_0001")
    assert_status(r, 200)
    assert_keys(r.json(), "id", "account_id", "patient_id", "payer_id",
                "description", "date_of_service", "diagnosis", "total_billed",
                "ehr_status", "clearing_house_status", "payer_status")


def test_claim_get_not_found(s):
    r = s.get(f"{BASE_URL}/claim/claim_9999")
    assert_status(r, 404)
    assert "error" in r.json()


def test_claim_update_status_fields(s):
    r = s.put(f"{BASE_URL}/claim/claim_0002/update",
              json={"payer_status": "PAID", "ehr_status": "SENT"})
    assert_status(r, 200)
    body = r.json()
    assert body["payer_status"] == "PAID"
    assert body["ehr_status"] == "SENT"


def test_claim_update_disallowed_field(s):
    r = s.put(f"{BASE_URL}/claim/claim_0001/update",
              json={"total_billed": 0.01})
    assert_status(r, 400)
    assert "error" in r.json()


def test_claim_update_not_found(s):
    r = s.put(f"{BASE_URL}/claim/claim_9999/update",
              json={"payer_status": "PAID"})
    assert_status(r, 404)
    assert "error" in r.json()


# ===========================================================================
# BotService
# ===========================================================================

def test_bot_types(s):
    r = s.get(f"{BASE_URL}/bot/types")
    assert_status(r, 200)
    data = r.json()
    assert isinstance(data, list)
    ids = {b["id"] for b in data}
    assert ids == {"ehr", "clearinghouse", "payer"}


def test_bot_account_list_found(s):
    r = s.get(f"{BASE_URL}/bot/ehr/account/list")
    assert_status(r, 200)
    assert isinstance(r.json(), list)


def test_bot_account_list_unknown_type(s):
    r = s.get(f"{BASE_URL}/bot/unknown_type/account/list")
    assert_status(r, 404)
    assert "error" in r.json()


def test_bot_schedule_create(s):
    payload = {
        "schedule": {"interval_minutes": 30, "retry_attempts": 1, "timeout_seconds": 120, "start_date": 9999999},
        "max_concurrent_jobs": 2,
        "priority": "normal",
    }
    r = s.put(f"{BASE_URL}/bot/clearinghouse/account/acc_003/schedule", json=payload)
    assert_status(r, 200)
    body = r.json()
    assert_keys(body, "bot-instance-id", "next-exec-date")
    assert body["next-exec-date"] is not None


def test_bot_schedule_update_existing(s):
    payload = {
        "schedule": {"interval_minutes": 60, "retry_attempts": 3, "timeout_seconds": 300, "start_date": 1711065600},
        "max_concurrent_jobs": 5,
        "priority": "high",
    }
    r = s.put(f"{BASE_URL}/bot/ehr/account/acc_001/schedule", json=payload)
    assert_status(r, 200)
    body = r.json()
    assert_keys(body, "bot-instance-id", "next-exec-date")


def test_bot_schedule_unknown_type(s):
    r = s.put(f"{BASE_URL}/bot/nope/account/acc_001/schedule", json={})
    assert_status(r, 404)


def test_bot_status_found(s):
    r = s.get(f"{BASE_URL}/bot/ehr/account/acc_001/status")
    assert_status(r, 200)
    body = r.json()
    assert_keys(body, "bot-instance-id", "next-exec-date", "stats", "status")
    assert body["status"] == "SCHEDULED"


def test_bot_status_not_found(s):
    r = s.get(f"{BASE_URL}/bot/ehr/account/acc_no_such/status")
    assert_status(r, 404)
    assert "error" in r.json()


def test_bot_status_unknown_type(s):
    r = s.get(f"{BASE_URL}/bot/nope/account/acc_001/status")
    assert_status(r, 404)


def test_bot_kill_found(s):
    # Schedule first so the instance is in SCHEDULED state, then kill
    s.put(f"{BASE_URL}/bot/payer/account/acc_002/schedule",
          json={"schedule": {"interval_minutes": 60}, "max_concurrent_jobs": 1, "priority": "normal"})
    r = s.post(f"{BASE_URL}/bot/payer/account/acc_002/kill")
    assert_status(r, 200)
    body = r.json()
    assert_keys(body, "bot-instance-id", "next-exec-date")
    assert body["next-exec-date"] is None


def test_bot_kill_not_found(s):
    r = s.post(f"{BASE_URL}/bot/ehr/account/acc_no_such/kill")
    assert_status(r, 404)
    assert "error" in r.json()


def test_bot_kill_unknown_type(s):
    r = s.post(f"{BASE_URL}/bot/nope/account/acc_001/kill")
    assert_status(r, 404)


def test_puppet_kill_em_all(s):
    r = s.post(f"{BASE_URL}/puppet/master-of/kill-em-all")
    assert_status(r, 200)
    body = r.json()
    assert_keys(body, "affected")
    assert isinstance(body["affected"], int)
    # Verify all instances are now KILLED
    for bt in ["ehr", "clearinghouse", "payer"]:
        instances_r = s.get(f"{BASE_URL}/bot/{bt}/account/list")
        for inst in instances_r.json():
            assert inst["status"] == "KILLED", (
                f"Expected KILLED after kill-em-all, got {inst['status']} for {bt}/{inst['account_id']}"
            )


def test_puppet_start_all(s):
    r = s.post(f"{BASE_URL}/puppet/master-of/start-all")
    assert_status(r, 200)
    body = r.json()
    assert_keys(body, "affected")
    assert isinstance(body["affected"], int)
    # Verify all instances are now SCHEDULED
    for bt in ["ehr", "clearinghouse", "payer"]:
        instances_r = s.get(f"{BASE_URL}/bot/{bt}/account/list")
        for inst in instances_r.json():
            assert inst["status"] == "SCHEDULED", (
                f"Expected SCHEDULED after start-all, got {inst['status']} for {bt}/{inst['account_id']}"
            )


# ===========================================================================
# Runner
# ===========================================================================

ALL_TESTS = [
    # Patient
    ("GET  /patient/list                          ", test_patient_list),
    ("GET  /patient/1  (found)                   ", test_patient_get_found),
    ("GET  /patient/999999  (not found)           ", test_patient_get_not_found),
    ("POST /patient/create  (success)             ", test_patient_create),
    ("POST /patient/create  (missing fields)      ", test_patient_create_missing_fields),
    ("PUT  /patient/update  (success)             ", test_patient_update),
    ("PUT  /patient/update  (missing id)          ", test_patient_update_missing_id),
    ("PUT  /patient/update  (not found)           ", test_patient_update_not_found),
    ("GET  /patient/1/conditions  (found)         ", test_patient_conditions_found),
    ("GET  /patient/999999/conditions  (not found)", test_patient_conditions_not_found),
    # Account
    ("GET  /account/list                          ", test_account_list),
    ("GET  /account/acc_001  (found)              ", test_account_get_found),
    ("GET  /account/acc_nope  (not found)         ", test_account_get_not_found),
    ("GET  /account/acc_001/bot/ehr/config        ", test_account_bot_config_found),
    ("GET  /account/acc_003/bot/ehr/config (empty)", test_account_bot_config_empty),
    ("GET  /account/acc_nope/bot/ehr/config       ", test_account_bot_config_bad_account),
    ("GET  /account/acc_001/bot/nope/config       ", test_account_bot_config_bad_type),
    # Claim
    ("GET  /claim/list                            ", test_claim_list),
    ("GET  /claim/claim_0001  (found)             ", test_claim_get_found),
    ("GET  /claim/claim_9999  (not found)         ", test_claim_get_not_found),
    ("PUT  /claim/claim_0002/update  (allowed)    ", test_claim_update_status_fields),
    ("PUT  /claim/claim_0001/update  (disallowed) ", test_claim_update_disallowed_field),
    ("PUT  /claim/claim_9999/update  (not found)  ", test_claim_update_not_found),
    # Bot
    ("GET  /bot/types                             ", test_bot_types),
    ("GET  /bot/ehr/account/list                  ", test_bot_account_list_found),
    ("GET  /bot/unknown/account/list              ", test_bot_account_list_unknown_type),
    ("PUT  /bot/clearinghouse/acc_003/schedule    ", test_bot_schedule_create),
    ("PUT  /bot/ehr/acc_001/schedule  (update)    ", test_bot_schedule_update_existing),
    ("PUT  /bot/nope/acc_001/schedule             ", test_bot_schedule_unknown_type),
    ("GET  /bot/ehr/acc_001/status  (found)       ", test_bot_status_found),
    ("GET  /bot/ehr/acc_no_such/status (not found)", test_bot_status_not_found),
    ("GET  /bot/nope/acc_001/status               ", test_bot_status_unknown_type),
    ("POST /bot/payer/acc_002/kill                ", test_bot_kill_found),
    ("POST /bot/ehr/acc_no_such/kill  (not found) ", test_bot_kill_not_found),
    ("POST /bot/nope/acc_001/kill                 ", test_bot_kill_unknown_type),
    ("POST /puppet/master-of/kill-em-all          ", test_puppet_kill_em_all),
    ("POST /puppet/master-of/start-all            ", test_puppet_start_all),
]


def main():
    session = requests.Session()

    print(f"\nRunning integration tests against {BASE_URL}\n")

    print("── PatientService ─────────────────────────────────────────")
    for name, fn in ALL_TESTS[:10]:
        test(name, fn, session)

    print("\n── AccountService ─────────────────────────────────────────")
    for name, fn in ALL_TESTS[10:17]:
        test(name, fn, session)

    print("\n── ClaimService ───────────────────────────────────────────")
    for name, fn in ALL_TESTS[17:23]:
        test(name, fn, session)

    print("\n── BotService ─────────────────────────────────────────────")
    for name, fn in ALL_TESTS[23:]:
        test(name, fn, session)

    passed = sum(1 for ok, _ in results if ok)
    failed = sum(1 for ok, _ in results if not ok)
    total = len(results)

    print(f"\n{'─'*59}")
    print(f"  {passed}/{total} passed", end="")
    if failed:
        print(f"   ({failed} failed)")
        for ok, name in results:
            if not ok:
                print(f"    {FAIL}  {name.strip()}")
    else:
        print("  — all green")
    print()

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
