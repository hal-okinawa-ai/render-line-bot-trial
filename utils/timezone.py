from datetime import datetime, timezone, timedelta

def get_japan_time():
    JST = timezone(timedelta(hours=+9))
    return datetime.now(JST)