from datetime import datetime
from utils.timezone import get_japan_time
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

def connect_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds_dict = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.getenv("SHEET_ID")).worksheet(os.getenv("SHEET_NAME", "紹介データ"))
    return sheet

def update_spreadsheet(user_id, referral_code, referred_by_id, display_name, inviter_name, now_japan_time):
    sheet = connect_sheet()
    if sheet is None:
        print("❌ スプレッドシートの接続に失敗しました。")
        return

    referred_count = len(sheet.findall(referred_by_id)) if referred_by_id else 0
    
    sheet.append_row([
        user_id,
        referral_code,
        referred_by_id,
        display_name,
        inviter_name,
        referred_count,
        now_japan_time.strftime('%Y-%m-%d %H:%M:%S')  # ← datetimeを文字列に変換
    ])