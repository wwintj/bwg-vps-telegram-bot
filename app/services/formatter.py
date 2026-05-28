import datetime
import pytz
from app.config import TIMEZONE


def format_bytes(value) -> str:
    if not value:
        return "0.00 B"

    value = float(value)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024.0:
            return f"{value:.2f} {unit}"
        value /= 1024.0

    return f"{value:.2f} PB"


def format_timestamp(timestamp) -> str:
    if not timestamp:
        return "N/A"

    try:
        timezone = pytz.timezone(TIMEZONE)
        dt = datetime.datetime.fromtimestamp(int(timestamp), tz=timezone)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "N/A"


def mask_api_key(api_key: str) -> str:
    if not api_key or len(api_key) < 10:
        return "***"

    return f"{api_key[:4]}********{api_key[-4:]}"
