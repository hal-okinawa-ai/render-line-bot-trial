from linebot import LineBotApi
from config import LINE_ACCESS_TOKEN

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

def get_user_name(user_id):
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except Exception as e:
        print(f"❌ 表示名取得エラー: {e}")
        return None