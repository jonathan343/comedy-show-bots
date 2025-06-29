from abc import ABC, abstractmethod
from typing import List, Dict, Any


class Show:
    def __init__(self, time_and_venue: str, comedians: List[str], date: str, raw_data: Dict[str, Any] = None):
        self.time_and_venue = time_and_venue
        self.comedians = comedians
        self.date = date
        self.raw_data = raw_data or {}

    def __repr__(self):
        return f"Show(date={self.date}, venue={self.time_and_venue}, comedians={self.comedians})"


class VenueBot(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def fetch_lineup(self, date: str) -> List[Show]:
        """Fetch lineup for a specific date."""
        pass

    @abstractmethod
    def get_venue_identifier(self) -> str:
        """Return a unique identifier for this venue."""
        pass

    def find_favorite_comedians(self, shows: List[Show], favorite_comedians: List[str]) -> Dict[str, List[str]]:
        """Find shows with favorite comedians."""
        results = {}
        for show in shows:
            for comedian in show.comedians:
                if comedian in favorite_comedians:
                    results.setdefault(show.time_and_venue, []).append(comedian)
        return results