import os
from typing import List


class Config:
    """Configuration settings for the comedy show bot."""

    FAVORITE_COMEDIANS = [
        "Andrew Schulz",
        "Shane Gillis",
        "Kam Patterson",
        "Mark Normand",
        "Hasan Minhaj",
        "Ari Matti",
        "Ralph Barbosa",
        "Chris Distefano",
        "Marcello Hernandez",
        "Chris Rock",
        "Larry David",
        "Adam Sandler",
        "Ari Shaffir",
        "Sam Morril",
        "Tom Segura",
        "John Mulaney",
        "Matt Rife",
    ]

    EMAIL_TO = os.environ.get("EMAIL_TO", "jonathangee09@gmail.com")
    EMAIL_FROM = os.environ.get("EMAIL_FROM", "comedy-alerts@jonathangaytan.com")
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

    @classmethod
    def get_favorite_comedians(cls) -> List[str]:
        """Get list of favorite comedians."""
        return cls.FAVORITE_COMEDIANS

    @classmethod
    def get_email_config(cls) -> dict:
        """Get email configuration."""
        return {"to": cls.EMAIL_TO, "from": cls.EMAIL_FROM, "region": cls.AWS_REGION}
