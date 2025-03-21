# LINEユーザー名を取得
def get_user_name(user_id):
    try:
        profile = line_bot_api.get_profile(user_id)
        return profile.display_name
    except Exception as e:
        print(f"❌ ユーザー名取得エラー: {e}")
        return "不明"