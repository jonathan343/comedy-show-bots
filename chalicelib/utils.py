from datetime import datetime, timedelta
from typing import List


def get_next_days(days: int = 7) -> List[str]:
    """
    Returns the next N days (including today) in 'YYYY-MM-DD' format.

    Args:
        days (int): Number of days to return. Defaults to 7.

    Returns:
        List[str]: List of date strings.
    """
    today = datetime.today()
    return [(today + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
