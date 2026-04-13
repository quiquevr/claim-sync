import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Dict

from bots.scheduler_worker import SchedulerWorker
from data import store


@dataclass
class BotScheduleEntry:
    bot_type: str
    account_id: str
    schedule: dict
    max_concurrent_jobs: int
    priority: str
    started_timestamp: float


class MasterOfPuppets:

    def __init__(self, executor: ThreadPoolExecutor):
        self._executor = executor
        self.schedule_entries: Dict[tuple, BotScheduleEntry] = {}
        self.workers: Dict[tuple, SchedulerWorker] = {}
        self._lock = threading.Lock()

    def schedule(self, bot_type: str, account_id: str):
        import time

        key = (bot_type, account_id)
        instance = store.bot_instances.get(key, {})

        entry = BotScheduleEntry(
            bot_type=bot_type,
            account_id=account_id,
            schedule=instance.get("schedule", {}),
            max_concurrent_jobs=instance.get("max_concurrent_jobs", 1),
            priority=instance.get("priority", "normal"),
            started_timestamp=time.time(),
        )

        worker = SchedulerWorker(single_schedule=entry, executor=self._executor)

        with self._lock:
            existing = self.workers.get(key)
            if existing is not None:
                existing.cancel()

            self.schedule_entries[key] = entry
            self.workers[key] = worker

        self._executor.submit(worker.fire_bot)

        loop_thread = threading.Thread(target=worker.loop, daemon=True)
        loop_thread.start()

    def cancel(self, bot_type: str, account_id: str):
        key = (bot_type, account_id)
        with self._lock:
            worker = self.workers.get(key)
            if worker is not None:
                worker.cancel()
                del self.workers[key]

    def cancel_all(self):
        with self._lock:
            for worker in self.workers.values():
                worker.cancel()
            self.workers.clear()

    def restart_all(self):
        with self._lock:
            entries_snapshot = list(self.schedule_entries.items())

        for key, _ in entries_snapshot:
            bot_type, account_id = key
            self.schedule(bot_type, account_id)
