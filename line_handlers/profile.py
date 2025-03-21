from linebot.exceptions import LineBotApiError

def get_user_name(user_id, line_bot_api):
    if not user_id:
        print("❌ 無効な user_idです。")
        return "ゲスト"

    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except LineBotApiError as e:
        print(f"❌ 表示名取得エラー: {e}")
        return "ゲスト"