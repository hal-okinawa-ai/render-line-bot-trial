import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timezone, timedelta

def get_japan_time():
    return (datetime.now(timezone.utc) + timedelta(hours=9)).strftime('%Y-%m-%d %H:%M:%S')

def connect_sheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
    
    service_account_info = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    creds_dict = json.loads(service_account_info)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet_id = os.getenv("SHEET_ID")
    sheet_name = os.getenv("SHEET_NAME", "紹介データ")
    
    return client.open_by_key(sheet_id).worksheet(sheet_name)

def update_spreadsheet(user_id, referral_code, referred_by_id, display_name, inviter_name, referred_count):
    sheet = connect_sheet()
    now_japan_time = get_japan_time()
    sheet.append_row([
        user_id, referral_code, referred_by_id, display_name, inviter_name, referred_count, now_japan_time
    ])