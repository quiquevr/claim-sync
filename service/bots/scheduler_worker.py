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
        bot = BotFactory().provideByType(self.single_schedule.bot_type)
        retry_attempts = self.single_schedule.schedule.get("retry_attempts", 1)
        timeout_seconds = self.single_schedule.schedule.get("timeout_seconds", 300)

        last_exc = None
        for attempt in range(retry_attempts):
            try:
                future = self._executor.submit(bot.execute)
                future.result(timeout=timeout_seconds)
                return
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "fire_bot attempt %d/%d failed for %s/%s: %s",
                    attempt + 1,
                    retry_attempts,
                    self.single_schedule.bot_type,
                    self.single_schedule.account_id,
                    exc,
                )

        raise last_exc

    def loop(self):
        interval_seconds = self.single_schedule.schedule.get("interval_minutes", 60) * 60
        while not self._stop_event.is_set():
            self.fire_bot()
            self._stop_event.wait(timeout=interval_seconds)

    def cancel(self):
        self._stop_event.set()
