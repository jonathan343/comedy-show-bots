from typing import Dict, List
from .venues import VenueBot
from .email_service import EmailService
from .utils import get_next_days
from .config import Config


class ComedyBotService:
    """Main service for coordinating comedy show checking and notifications."""

    def __init__(self, venues: List[VenueBot], email_service: EmailService):
        self.venues = venues
        self.email_service = email_service
        self.favorite_comedians = Config.get_favorite_comedians()
        self.email_config = Config.get_email_config()

    def check_all_venues(self) -> Dict[str, Dict[str, Dict[str, List[str]]]]:
        """Check all venues for favorite comedians in the next 7 days."""
        all_results = {}
        dates = get_next_days(21)

        for venue in self.venues:
            venue_results = {}
            for date in dates:
                try:
                    shows = venue.fetch_lineup(date)
                    matches = venue.find_favorite_comedians(
                        shows, self.favorite_comedians
                    )
                    if matches:
                        venue_results[date] = matches
                except Exception as e:
                    print(f"Error fetching {venue.name} lineup for {date}: {e}")
                    continue

            if venue_results:
                all_results[venue.name] = venue_results

        return all_results

    def send_comedy_alerts(self, results: Dict[str, Dict[str, Dict[str, List[str]]]]):
        """Send email alerts for all venues with matches."""
        if not results:
            self._send_no_shows_email()
            return

        for venue_name, venue_results in results.items():
            self._send_venue_alert(venue_name, venue_results)

    def _send_venue_alert(
        self, venue_name: str, results: Dict[str, Dict[str, List[str]]]
    ):
        """Send alert for a specific venue."""
        subject = f"{venue_name} Comedy Alert - Your Favorite Comedians!"

        html_body = self.email_service.format_comedy_alert_html(results, venue_name)
        text_body = self.email_service.format_comedy_alert_text(results, venue_name)

        try:
            response = self.email_service.send_email(
                subject=subject,
                body=text_body,
                html_body=html_body,
                to_address=self.email_config["to"],
                from_address=self.email_config["from"],
            )
            print(f"Email sent for {venue_name}: {response.get('MessageId', 'No ID')}")
        except Exception as e:
            print(f"Failed to send email for {venue_name}: {e}")

    def _send_no_shows_email(self):
        """Send email when no shows are found at any venue."""
        subject = "Comedy Alert - No Shows This Week"
        text_body = "No shows found with your favorite comedians at any venue in the next 7 days."
        html_body = """
        <html>
        <body style="font-family: Arial, sans-serif; text-align: center; margin: 20px;">
            <h2>🎭 Comedy Alert</h2>
            <p>No shows found with your favorite comedians at any venue in the next 7 days.</p>
            <p>Keep checking back - new shows are added regularly! 🎪</p>
            <p style="margin-top: 30px; color: #666; font-size: 12px;">Sent by your Comedy Show Bot 🤖</p>
        </body>
        </html>
        """

        try:
            response = self.email_service.send_email(
                subject=subject,
                body=text_body,
                html_body=html_body,
                to_address=self.email_config["to"],
                from_address=self.email_config["from"],
            )
            print(f"No shows email sent: {response.get('MessageId', 'No ID')}")
        except Exception as e:
            print(f"Failed to send no shows email: {e}")
