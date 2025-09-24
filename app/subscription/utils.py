from datetime import datetime, timezone

def format_timestamp_to_date_time(timestamp):
    return datetime.fromtimestamp(timestamp).astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M%z")