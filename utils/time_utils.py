import datetime
import pytz

def get_japan_time():
    japan_timezone = pytz.timezone("Asia/Tokyo")
    return datetime.datetime.now(japan_timezone).strftime("%Y-%m-%d %H:%M:%S")