import logging
import threading
from concurrent.futures import ThreadPoolExecutor

from bots.bot_factory import BotFactory

logger = logging.getLogger(__name__)


class SchedulerWorker:

    def __init__(self, single_schedule, executor: ThreadPoolExecutor):
        self.single_schedule = single_schedule
        self._stop_event = threading.Event()
        self._executor = executor

    def fire_bot(self):
        bot_type = self.single_schedule.bot_type
        account_id = self.single_schedule.account_id
        bot = BotFactory().provideByType(bot_type)
        retry_attempts = self.single_schedule.schedule.get("retry_attempts", 1)
        timeout_seconds = self.single_schedule.schedule.get("timeout_seconds", 300)

        print(f"[BotScheduler] SchedulerWorker | fire_bot START | type={bot_type} account={account_id}", flush=True)  # TEMP TEST

        last_exc = None
        for attempt in range(retry_attempts):
            try:
                future = self._executor.submit(bot.execute)
                future.result(timeout=timeout_seconds)
                print(f"[BotScheduler] SchedulerWorker | fire_bot SUCCESS | type={bot_type} account={account_id}", flush=True)  # TEMP TEST
                return
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "fire_bot attempt %d/%d failed for %s/%s: %s",
                    attempt + 1,
                    retry_attempts,
                    bot_type,
                    account_id,
                    exc,
                )
                print(f"[BotScheduler] SchedulerWorker | fire_bot RETRY {attempt + 1}/{retry_attempts} | type={bot_type} error={exc}", flush=True)  # TEMP TEST

        print(f"[BotScheduler] SchedulerWorker | fire_bot FAILED (all retries exhausted) | type={bot_type} error={last_exc}", flush=True)  # TEMP TEST
        raise last_exc

    def loop(self):
        bot_type = self.single_schedule.bot_type
        account_id = self.single_schedule.account_id
        interval_minutes = self.single_schedule.schedule.get("interval_minutes", 60)
        interval_seconds = interval_minutes * 60  # TEMP TEST: interval_minutes=1 in store gives a 60-second cycle
        while not self._stop_event.is_set():
            print(f"[BotScheduler] SchedulerWorker | loop TICK | type={bot_type} account={account_id} next_in={interval_minutes}min", flush=True)  # TEMP TEST
            self.fire_bot()
            self._stop_event.wait(timeout=interval_seconds)
        print(f"[BotScheduler] SchedulerWorker | loop CANCELLED | type={bot_type} account={account_id}", flush=True)  # TEMP TEST

    def cancel(self):
        self._stop_event.set()
