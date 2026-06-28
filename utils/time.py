import re
from datetime import timedelta
from typing import Optional


def parse_duration(duration: str) -> Optional[timedelta]:
    """Convierte una cadena como 1d2h30m en un timedelta."""
    pattern = re.compile(r"^(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?$")
    match = pattern.match(duration.strip().lower())

    if not match:
        return None

    days = int(match.group(1) or 0)
    hours = int(match.group(2) or 0)
    minutes = int(match.group(3) or 0)

    if days == 0 and hours == 0 and minutes == 0:
        return None

    return timedelta(days=days, hours=hours, minutes=minutes)
