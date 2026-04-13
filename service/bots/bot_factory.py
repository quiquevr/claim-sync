from bots.clearinghouse_bot import ClearingHouseBot
from bots.ehr_bot import EHRBot
from bots.observer_bot import ObserverBot
from bots.payer_bot import PayerBot


class BotFactory:

    def provideByType(self, bot_type: str) -> ObserverBot:
        if bot_type == "ehr":
            return EHRBot()
        if bot_type == "clearinghouse":
            return ClearingHouseBot()
        if bot_type == "payer":
            return PayerBot()
        raise ValueError(f"Unknown bot type: {bot_type!r}")
