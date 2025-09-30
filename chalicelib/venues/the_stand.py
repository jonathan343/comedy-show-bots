import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
from .base import VenueBot, Show
from ..llm_extractor import LLMExtractor


class TheStandBot(VenueBot):
    """Venue bot for The Stand NYC using LLM-based extraction."""

    def __init__(self):
        super().__init__("The Stand NYC")
        self.shows_url = "https://thestandnyc.com/shows"
        self.llm_extractor = LLMExtractor()
        self._cache: Optional[List[Dict]] = None
        self.headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

    def get_venue_identifier(self) -> str:
        return "the_stand_nyc"

    def fetch_lineup(self, date: str = "today") -> List[Show]:
        """
        Fetch The Stand NYC lineup for a given date.

        Args:
            date: Date string in format used by the service (e.g., "2025-09-29")

        Returns:
            List of Show objects for the specified date
        """
        # Lazy load and cache all shows on first call
        if self._cache is None:
            self._load_and_cache_shows()

        # Filter cached shows by date
        return self._filter_shows_by_date(date)

    def _load_and_cache_shows(self):
        """Fetch HTML, preprocess it, extract shows with LLM, and cache results."""
        try:
            # Fetch the shows page
            response = requests.get(self.shows_url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # Preprocess HTML with BeautifulSoup
            cleaned_html = self._preprocess_html(response.text)

            # Extract shows using LLM
            self._cache = self.llm_extractor.extract_shows(cleaned_html, self.name)

            print(f"Cached {len(self._cache)} shows from {self.name}")

        except Exception as e:
            print(f"Error loading shows from {self.name}: {e}")
            self._cache = []

    def _preprocess_html(self, html: str) -> str:
        """
        Clean HTML to keep only relevant show information.

        Removes navigation, footer, scripts, styles while preserving show cards.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove unnecessary elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Try to find main content area (adjust selectors based on actual HTML structure)
        # If specific container exists, extract only that
        main_content = soup.find("main") or soup.find("div", class_="shows") or soup

        return str(main_content)

    def _filter_shows_by_date(self, date: str) -> List[Show]:
        """
        Filter cached shows by date and convert to Show objects.

        Args:
            date: Date string to filter by (YYYY-MM-DD format or "today")

        Returns:
            List of Show objects for the specified date
        """
        if not self._cache:
            return []

        # Handle "today" date
        if date == "today":
            date = datetime.now().strftime("%Y-%m-%d")

        shows = []
        for show_data in self._cache:
            if show_data.get("date") == date:
                # Build time_and_venue string
                time = show_data.get("time", "")
                venue_location = show_data.get("venue_location", "")

                if venue_location:
                    time_and_venue = f"{time} - {self.name} ({venue_location})"
                else:
                    time_and_venue = f"{time} - {self.name}"

                shows.append(
                    Show(
                        time_and_venue=time_and_venue,
                        comedians=show_data.get("comedians", []),
                        date=date,
                        raw_data={
                            "venue": self.name,
                            "show_url": show_data.get("show_url", ""),
                        },
                    )
                )

        return shows