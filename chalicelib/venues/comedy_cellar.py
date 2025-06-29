import requests
from bs4 import BeautifulSoup
from typing import List
from .base import VenueBot, Show


class ComedyCellarBot(VenueBot):
    def __init__(self):
        super().__init__("Comedy Cellar")
        self.base_url = "https://www.comedycellar.com/lineup/api/"
        self.headers = {
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.comedycellar.com",
            "referer": "https://www.comedycellar.com/new-york-line-up/",
            "user-agent": "Mozilla/5.0",
        }

    def get_venue_identifier(self) -> str:
        return "comedy_cellar"

    def fetch_lineup(self, date: str = "today") -> List[Show]:
        """Fetch the Comedy Cellar lineup for a given date."""
        data = {
            "action": "cc_get_shows",
            "json": f'{{"date":"{date}","venue":"newyork","type":"lineup"}}',
        }

        response = requests.post(self.base_url, headers=self.headers, data=data)
        response.raise_for_status()
        html = response.json()["show"]["html"]

        soup = BeautifulSoup(html, "html.parser")
        shows = []

        for show_section in soup.select(".set-header"):
            show_info = show_section.find("h2")
            time_and_venue = show_info.get_text(strip=True).replace("show", "").strip()

            comedians = []
            for lineup in show_section.find_next_sibling("div").select(".set-content"):
                name_tag = lineup.find("span", class_="name")
                name = name_tag.get_text(strip=True) if name_tag else "Unknown"
                comedians.append(name)

            shows.append(
                Show(
                    time_and_venue=time_and_venue,
                    comedians=comedians,
                    date=date,
                    raw_data={"venue": self.name},
                )
            )

        return shows
