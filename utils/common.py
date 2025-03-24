import random
import string
from datetime import datetime
import pytz

def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def get_japan_time():
    tz = pytz.timezone('Asia/Tokyo')
    return datetime.now(tz)