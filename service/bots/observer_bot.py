from abc import ABC, abstractmethod


class ObserverBot(ABC):

    @abstractmethod
    def execute(self):
        """Fetch data from the external source and dispatch to on_new_record / on_updated_record."""

    @abstractmethod
    def on_new_record(self, record):
        """Handle a newly discovered record."""

    @abstractmethod
    def on_updated_record(self, record):
        """Handle a record that has changed since last seen."""
