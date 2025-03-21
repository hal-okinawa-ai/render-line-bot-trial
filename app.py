from flask import Flask, request, jsonify
from linebot import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FollowEvent
from config import LINE_CHANNEL_SECRET
from line_handlers.follow import handle_follow
from line_handlers.message import handle_message
from database import init_db

app = Flask(__name__)
app.config["DEBUG"] = True
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400
    return "OK", 200

@handler.add(FollowEvent)
def handle_follow_event(event):
    handle_follow(event)

@handler.add(MessageEvent, message=TextMessage)
def handle_message_event(event):
    handle_message(event)

@app.route("/")
def home():
    return jsonify({"message": "LINE Bot is running."})

@app.route("/favicon.ico")
def favicon():
    return "", 204

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))