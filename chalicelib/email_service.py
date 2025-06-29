import boto3
from typing import Dict, List
from datetime import datetime


class EmailService:
    def __init__(self, region_name: str = "us-east-1"):
        self.ses = boto3.client("ses", region_name=region_name)

    def send_email(
        self,
        subject: str,
        body: str,
        to_address: str,
        from_address: str,
        html_body: str = None,
    ):
        """Send email with optional HTML body."""
        message_body = {"Text": {"Data": body}}
        if html_body:
            message_body["Html"] = {"Data": html_body}

        response = self.ses.send_email(
            Source=from_address,
            Destination={"ToAddresses": [to_address]},
            Message={
                "Subject": {"Data": subject},
                "Body": message_body,
            },
        )
        return response

    def format_comedy_alert_html(
        self, results: Dict[str, Dict[str, List[str]]], venue_name: str = "Comedy Venue"
    ) -> str:
        """Format comedy show results into HTML email."""
        if not any(results.values()):
            return self._get_no_shows_html(venue_name)

        html_parts = [
            f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #ff6b6b; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                    .date-section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #ff6b6b; background-color: #f8f9fa; }}
                    .date-title {{ font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px; }}
                    .show {{ margin: 10px 0; padding: 10px; background-color: white; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .venue {{ font-weight: bold; color: #ff6b6b; }}
                    .comedians {{ margin-top: 5px; }}
                    .comedian {{ display: inline-block; background-color: #e9ecef; padding: 3px 8px; margin: 2px; border-radius: 12px; font-size: 12px; }}
                    .no-shows {{ text-align: center; color: #666; font-style: italic; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🎭 {venue_name} Comedy Alert!</h1>
                    <p>Your favorite comedians are performing soon!</p>
                </div>
            """
        ]

        for date, shows in results.items():
            if shows:
                formatted_date = self._format_date_display(date)
                html_parts.append('<div class="date-section">')
                html_parts.append(f'<div class="date-title">📅 {formatted_date}</div>')

                for venue, comedians in shows.items():
                    html_parts.append('<div class="show">')
                    html_parts.append(f'<div class="venue">🎪 {venue}</div>')
                    html_parts.append('<div class="comedians">')
                    for comedian in comedians:
                        html_parts.append(
                            f'<span class="comedian">⭐ {comedian}</span>'
                        )
                    html_parts.append("</div></div>")

                html_parts.append("</div>")

        html_parts.append("""
                <div style="margin-top: 30px; text-align: center; color: #666; font-size: 12px;">
                    <p>Sent by your Comedy Show Bot 🤖</p>
                </div>
            </body>
            </html>
        """)

        return "".join(html_parts)

    def format_comedy_alert_text(
        self, results: Dict[str, Dict[str, List[str]]], venue_name: str = "Comedy Venue"
    ) -> str:
        """Format comedy show results into plain text email."""
        if not any(results.values()):
            return f"No shows found with your favorite comedians at {venue_name} in the next 7 days."

        text_parts = [
            f"{venue_name} Comedy Alert - Your favorite comedians are performing!\n"
        ]
        text_parts.append("=" * 60 + "\n")

        for date, shows in results.items():
            if shows:
                formatted_date = self._format_date_display(date)
                text_parts.append(f"\n📅 {formatted_date}\n")
                text_parts.append("-" * 30 + "\n")

                for venue, comedians in shows.items():
                    text_parts.append(f"🎪 {venue}\n")
                    for comedian in comedians:
                        text_parts.append(f"  ⭐ {comedian}\n")
                    text_parts.append("\n")

        text_parts.append("\nSent by your Comedy Show Bot 🤖")
        return "".join(text_parts)

    def _get_no_shows_html(self, venue_name: str) -> str:
        """HTML template for when no shows are found."""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; text-align: center; }}
                .header {{ background-color: #6c757d; color: white; padding: 20px; border-radius: 8px; }}
                .message {{ margin: 20px 0; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎭 {venue_name} Comedy Alert</h1>
                <p>No shows with your favorite comedians found</p>
            </div>
            <div class="message">
                <p>No shows found with your favorite comedians at {venue_name} in the next 7 days.</p>
                <p>Keep checking back - new shows are added regularly! 🎪</p>
            </div>
            <div style="margin-top: 30px; color: #666; font-size: 12px;">
                <p>Sent by your Comedy Show Bot 🤖</p>
            </div>
        </body>
        </html>
        """

    def _format_date_display(self, date_str: str) -> str:
        """Format date string for display."""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%A, %B %d, %Y")
        except ValueError:
            return date_str
