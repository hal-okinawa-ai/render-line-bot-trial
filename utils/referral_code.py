# referral_code.py

import random
import string

def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))