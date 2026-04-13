from bots.ehr_bot import EHRBot
from bots.observer_bot import ObserverBot


class BotFactory:

    def provideByType(self, bot_type: str) -> ObserverBot:
        if bot_type == "ehr":
            return EHRBot()
        raise ValueError(f"Unknown bot type: {bot_type!r}")
