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

def update_spreadsheet(user_id, referral_code, referred_by, display_name, inviter_name):
    sheet = connect_sheet()

    if sheet is None:
        print("❌ スプレッドシート接続エラー")
        return

    referred_count = len(sheet.findall(referred_by))
    sheet.append_row([user_id, referral_code, referred_by, referred_count, display_name, inviter_name])
    print(f"✅ {user_id} ({display_name}) をスプレッドシートに記録（紹介者: {inviter_name}）")