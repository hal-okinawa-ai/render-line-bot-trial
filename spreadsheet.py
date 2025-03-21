import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from config import SHEET_ID, SHEET_NAME, GOOGLE_SERVICE_ACCOUNT

def connect_sheet():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
                 "https://www.googleapis.com/auth/drive"]
        creds_dict = json.loads(GOOGLE_SERVICE_ACCOUNT)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        return client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    except Exception as e:
        print(f"❌ Sheets接続エラー: {e}")
        return None

def update_spreadsheet(user_id, referral_code, referred_by):
    sheet = connect_sheet()
    if not sheet:
        return
    try:
        referred_count = len(sheet.findall(referred_by))
        sheet.append_row([user_id, referral_code, referred_by, referred_count])
        print(f"✅ Sheetsに記録: {user_id}")
    except Exception as e:
        print(f"❌ Sheets書き込みエラー: {e}")