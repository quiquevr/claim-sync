"""Unit tests for the scheduling engine."""

import threading
from concurrent.futures import Future, ThreadPoolExecutor
from unittest.mock import MagicMock, call, patch

import pytest

from bots.bot_factory import BotFactory
from bots.clearinghouse_bot import ClearingHouseBot
from bots.ehr_bot import EHRBot
from bots.master_of_puppets import BotScheduleEntry, MasterOfPuppets
from bots.payer_bot import PayerBot
from bots.scheduler_worker import SchedulerWorker
from data import claim_store, patient_store, store


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_entry(**kwargs):
    defaults = dict(
        bot_type="ehr",
        account_id="acc_001",
        schedule={"interval_minutes": 60, "retry_attempts": 3, "timeout_seconds": 30},
        max_concurrent_jobs=2,
        priority="normal",
        started_timestamp=0.0,
    )
    defaults.update(kwargs)
    return BotScheduleEntry(**defaults)


# ---------------------------------------------------------------------------
# BotFactory
# ---------------------------------------------------------------------------

class TestBotFactory:

    def test_raises_for_unknown_type(self):
        with pytest.raises(ValueError, match="Unknown bot type"):
            BotFactory().provideByType("unicorn")

    def test_returns_ehr_bot_for_ehr(self):
        bot = BotFactory().provideByType("ehr")
        assert isinstance(bot, EHRBot)

    def test_returns_clearinghouse_bot_for_clearinghouse(self):
        bot = BotFactory().provideByType("clearinghouse")
        assert isinstance(bot, ClearingHouseBot)

    def test_returns_payer_bot_for_payer(self):
        bot = BotFactory().provideByType("payer")
        assert isinstance(bot, PayerBot)


# ---------------------------------------------------------------------------
# EHRBot
# ---------------------------------------------------------------------------

class TestEHRBot:

    def test_on_new_record_maps_and_upserts(self):
        resource = {"id": "pat-123", "gender": "male", "birthDate": "1990-01-01"}
        with patch.object(patient_store, "upsert") as mock_upsert:
            EHRBot().on_new_record(resource)
        mock_upsert.assert_called_once_with(
            {"id": "pat-123", "gender": "male", "dob": "1990-01-01"}
        )

    def test_on_new_record_defaults_for_missing_fields(self):
        resource = {"id": "pat-456"}
        with patch.object(patient_store, "upsert") as mock_upsert:
            EHRBot().on_new_record(resource)
        mock_upsert.assert_called_once_with(
            {"id": "pat-456", "gender": "unknown", "dob": ""}
        )

    def test_on_updated_record_maps_and_upserts(self):
        resource = {"id": "pat-789", "gender": "female", "birthDate": "1985-06-15"}
        with patch.object(patient_store, "upsert") as mock_upsert:
            EHRBot().on_updated_record(resource)
        mock_upsert.assert_called_once_with(
            {"id": "pat-789", "gender": "female", "dob": "1985-06-15"}
        )

    def test_execute_iterates_bundle_entries(self):
        fake_bundle = {
            "entry": [
                {"resource": {"id": "pat-001", "gender": "male", "birthDate": "1980-01-01"}},
                {"resource": {"id": "pat-002", "gender": "female", "birthDate": "1992-07-20"}},
            ]
        }
        mock_response = MagicMock()
        mock_response.json.return_value = fake_bundle

        bot = EHRBot()
        with patch("bots.ehr_bot.requests.get", return_value=mock_response) as mock_get, \
             patch.object(bot, "on_new_record") as mock_on_new:
            bot.execute()

        mock_get.assert_called_once_with("http://hapi.fhir.org/baseR4/Patient")
        assert mock_on_new.call_count == 2
        mock_on_new.assert_any_call({"id": "pat-001", "gender": "male", "birthDate": "1980-01-01"})
        mock_on_new.assert_any_call({"id": "pat-002", "gender": "female", "birthDate": "1992-07-20"})


# ---------------------------------------------------------------------------
# SchedulerWorker
# ---------------------------------------------------------------------------

class TestSchedulerWorker:

    def _make_worker(self, entry=None, executor=None):
        return SchedulerWorker(
            single_schedule=entry or _make_entry(),
            executor=executor or MagicMock(spec=ThreadPoolExecutor),
        )

    def test_fire_bot_submits_execute_to_executor(self):
        executor = MagicMock(spec=ThreadPoolExecutor)
        future = MagicMock(spec=Future)
        future.result.return_value = None
        executor.submit.return_value = future

        worker = self._make_worker(executor=executor)
        mock_bot = MagicMock()

        with patch("bots.scheduler_worker.BotFactory") as MockFactory:
            MockFactory.return_value.provideByType.return_value = mock_bot
            worker.fire_bot()

        executor.submit.assert_called_once_with(mock_bot.execute)
        future.result.assert_called_once_with(timeout=30)

    def test_fire_bot_retries_on_failure(self):
        entry = _make_entry(schedule={"interval_minutes": 60, "retry_attempts": 3, "timeout_seconds": 30})
        executor = MagicMock(spec=ThreadPoolExecutor)
        future = MagicMock(spec=Future)
        future.result.side_effect = RuntimeError("boom")
        executor.submit.return_value = future

        worker = self._make_worker(entry=entry, executor=executor)
        mock_bot = MagicMock()

        with patch("bots.scheduler_worker.BotFactory") as MockFactory:
            MockFactory.return_value.provideByType.return_value = mock_bot
            with pytest.raises(RuntimeError, match="boom"):
                worker.fire_bot()

        assert executor.submit.call_count == 3

    def test_fire_bot_raises_after_exhausting_retries(self):
        entry = _make_entry(schedule={"interval_minutes": 60, "retry_attempts": 2, "timeout_seconds": 30})
        executor = MagicMock(spec=ThreadPoolExecutor)
        future = MagicMock(spec=Future)
        future.result.side_effect = ValueError("exhausted")
        executor.submit.return_value = future

        worker = self._make_worker(entry=entry, executor=executor)

        with patch("bots.scheduler_worker.BotFactory") as MockFactory:
            MockFactory.return_value.provideByType.return_value = MagicMock()
            with pytest.raises(ValueError, match="exhausted"):
                worker.fire_bot()

        assert executor.submit.call_count == 2

    def test_cancel_sets_stop_event(self):
        worker = self._make_worker()
        assert not worker._stop_event.is_set()
        worker.cancel()
        assert worker._stop_event.is_set()

    def test_loop_exits_immediately_when_cancelled(self):
        """If _stop_event is already set before loop() starts, it exits without calling fire_bot."""
        worker = self._make_worker()
        worker.cancel()  # pre-set stop event — while condition is False from the start

        with patch.object(worker, "fire_bot") as mock_fire:
            worker.loop()

        mock_fire.assert_not_called()


# ---------------------------------------------------------------------------
# MasterOfPuppets
# ---------------------------------------------------------------------------

class TestMasterOfPuppets:

    def _make_mop(self):
        executor = MagicMock(spec=ThreadPoolExecutor)
        executor.submit.return_value = MagicMock(spec=Future)
        return MasterOfPuppets(executor=executor), executor

    def test_schedule_creates_entry_and_worker(self):
        mop, _ = self._make_mop()
        with patch("bots.master_of_puppets.threading.Thread") as MockThread:
            MockThread.return_value = MagicMock()
            mop.schedule("ehr", "acc_001")

        key = ("ehr", "acc_001")
        assert key in mop.schedule_entries
        assert key in mop.workers
        assert isinstance(mop.schedule_entries[key], BotScheduleEntry)
        assert isinstance(mop.workers[key], SchedulerWorker)

    def test_schedule_cancels_existing_worker_before_replacing(self):
        mop, _ = self._make_mop()
        key = ("ehr", "acc_001")

        with patch("bots.master_of_puppets.threading.Thread") as MockThread:
            MockThread.return_value = MagicMock()
            mop.schedule("ehr", "acc_001")
            first_worker = mop.workers[key]
            first_worker.cancel = MagicMock()

            mop.schedule("ehr", "acc_001")

        first_worker.cancel.assert_called_once()

    def test_cancel_all_calls_cancel_on_all_workers_and_clears(self):
        mop, _ = self._make_mop()

        with patch("bots.master_of_puppets.threading.Thread") as MockThread:
            MockThread.return_value = MagicMock()
            mop.schedule("ehr", "acc_001")
            mop.schedule("ehr", "acc_002")

        workers = list(mop.workers.values())
        for w in workers:
            w.cancel = MagicMock()

        mop.cancel_all()

        for w in workers:
            w.cancel.assert_called_once()
        assert len(mop.workers) == 0

    def test_restart_all_snapshots_and_calls_schedule_for_each(self):
        mop, _ = self._make_mop()

        with patch("bots.master_of_puppets.threading.Thread") as MockThread:
            MockThread.return_value = MagicMock()
            mop.schedule("ehr", "acc_001")
            mop.schedule("ehr", "acc_002")

        with patch.object(mop, "schedule") as mock_schedule, \
             patch("bots.master_of_puppets.threading.Thread") as MockThread:
            MockThread.return_value = MagicMock()
            mop.restart_all()

        assert mock_schedule.call_count == 2
        mock_schedule.assert_any_call("ehr", "acc_001")
        mock_schedule.assert_any_call("ehr", "acc_002")


# ---------------------------------------------------------------------------
# patient_store.upsert
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# ClearingHouseBot
# ---------------------------------------------------------------------------

class TestClearingHouseBot:

    def test_execute_calls_on_new_record_exactly_3_times(self):
        bot = ClearingHouseBot()
        with patch.object(bot, "on_new_record") as mock_on_new:
            bot.execute()
        assert mock_on_new.call_count == 3

    def test_on_new_record_maps_correctly_and_calls_upsert(self):
        record = {
            "id": "ch_claim_001",
            "account_id": "acc_001",
            "patient_id": "pat-123",
            "payer_id": "availity_001",
            "status": "ACCEPTED",
            "remittance_amount": 450.00,
            "processed_date": "2024-03-22",
        }
        with patch.object(claim_store, "upsert") as mock_upsert:
            ClearingHouseBot().on_new_record(record)
        mock_upsert.assert_called_once_with({
            "id": "ch_claim_001",
            "account_id": "acc_001",
            "patient_id": "pat-123",
            "payer_id": "availity_001",
            "clearing_house_status": "ACCEPTED",
            "total_billed": 450.00,
            "date_of_service": "2024-03-22",
            "description": "Imported from clearing house",
            "diagnosis": [],
            "ehr_status": "GENERATED",
            "payer_status": "PENDING",
        })

    def test_on_new_record_always_sets_ehr_and_payer_status(self):
        record = {
            "id": "ch_claim_002",
            "account_id": "acc_001",
            "patient_id": "pat-456",
            "payer_id": "change_healthcare_001",
            "status": "REJECTED",
            "remittance_amount": 0.00,
            "processed_date": "2024-03-22",
        }
        with patch.object(claim_store, "upsert") as mock_upsert:
            ClearingHouseBot().on_new_record(record)
        mapped = mock_upsert.call_args[0][0]
        assert mapped["ehr_status"] == "GENERATED"
        assert mapped["payer_status"] == "PENDING"

    def test_on_updated_record_maps_and_calls_upsert(self):
        record = {
            "id": "ch_claim_003",
            "account_id": "acc_002",
            "patient_id": "pat-789",
            "payer_id": "trizetto_001",
            "status": "PENDING",
            "remittance_amount": 0.00,
            "processed_date": "2024-03-22",
        }
        with patch.object(claim_store, "upsert") as mock_upsert:
            ClearingHouseBot().on_updated_record(record)
        mock_upsert.assert_called_once_with({
            "id": "ch_claim_003",
            "account_id": "acc_002",
            "patient_id": "pat-789",
            "payer_id": "trizetto_001",
            "clearing_house_status": "PENDING",
            "total_billed": 0.00,
            "date_of_service": "2024-03-22",
            "description": "Imported from clearing house",
            "diagnosis": [],
            "ehr_status": "GENERATED",
            "payer_status": "PENDING",
        })


# ---------------------------------------------------------------------------
# PayerBot
# ---------------------------------------------------------------------------

class TestPayerBot:

    def test_execute_calls_on_new_record_exactly_3_times(self):
        bot = PayerBot()
        with patch.object(bot, "on_new_record") as mock_on_new:
            bot.execute()
        assert mock_on_new.call_count == 3

    def test_on_new_record_maps_correctly_and_calls_upsert(self):
        record = {
            "id": "pay_auth_001",
            "account_id": "acc_001",
            "patient_id": "pat-123",
            "payer_id": "unitedhealthcare_001",
            "eligibility_status": "ELIGIBLE",
            "authorization_code": "AUTH_UC_88821",
            "authorization_date": "2024-03-20",
            "expiry_date": "2024-06-20",
        }
        with patch.object(claim_store, "upsert") as mock_upsert:
            PayerBot().on_new_record(record)
        mock_upsert.assert_called_once_with({
            "id": "pay_auth_001",
            "account_id": "acc_001",
            "patient_id": "pat-123",
            "payer_id": "unitedhealthcare_001",
            "payer_status": "ELIGIBLE",
            "description": "Auth AUTH_UC_88821 expires 2024-06-20",
            "diagnosis": [],
            "ehr_status": "GENERATED",
            "clearing_house_status": "ACCEPTED",
            "total_billed": 0.00,
            "date_of_service": "2024-03-20",
        })

    def test_on_new_record_description_when_authorization_code_is_null(self):
        record = {
            "id": "pay_auth_002",
            "account_id": "acc_001",
            "patient_id": "pat-456",
            "payer_id": "anthem_001",
            "eligibility_status": "INELIGIBLE",
            "authorization_code": None,
            "authorization_date": "2024-03-21",
            "expiry_date": None,
        }
        with patch.object(claim_store, "upsert") as mock_upsert:
            PayerBot().on_new_record(record)
        mapped = mock_upsert.call_args[0][0]
        assert mapped["description"] == "Auth None expires None"

    def test_on_updated_record_maps_and_calls_upsert(self):
        record = {
            "id": "pay_auth_003",
            "account_id": "acc_002",
            "patient_id": "pat-789",
            "payer_id": "cigna_001",
            "eligibility_status": "PENDING",
            "authorization_code": None,
            "authorization_date": "2024-03-22",
            "expiry_date": None,
        }
        with patch.object(claim_store, "upsert") as mock_upsert:
            PayerBot().on_updated_record(record)
        mock_upsert.assert_called_once_with({
            "id": "pay_auth_003",
            "account_id": "acc_002",
            "patient_id": "pat-789",
            "payer_id": "cigna_001",
            "payer_status": "PENDING",
            "description": "Auth None expires None",
            "diagnosis": [],
            "ehr_status": "GENERATED",
            "clearing_house_status": "ACCEPTED",
            "total_billed": 0.00,
            "date_of_service": "2024-03-22",
        })


# ---------------------------------------------------------------------------
# patient_store.upsert
# ---------------------------------------------------------------------------

class TestPatientStoreUpsert:

    def test_inserts_new_record_when_id_missing(self):
        patient_store.upsert({"id": "pat-new", "gender": "female", "dob": "2000-01-01"})
        assert store.patients.get("pat-new") == {"id": "pat-new", "gender": "female", "dob": "2000-01-01"}

    def test_overwrites_existing_record_on_string_equality(self):
        # id "1" matches existing integer key 1
        patient_store.upsert({"id": "1", "gender": "male", "dob": "1990-01-01"})
        assert store.patients[1]["gender"] == "male"

    def test_handles_integer_and_string_keys_without_error(self):
        # Integer key already present (1, 2); string key new
        patient_store.upsert({"id": 1, "gender": "other", "dob": "1970-01-01"})  # update via int
        patient_store.upsert({"id": "pat-str", "gender": "female", "dob": "1995-05-05"})  # insert string
        assert store.patients[1]["gender"] == "other"
        assert store.patients["pat-str"]["gender"] == "female"
