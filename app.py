import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
from tarot import draw_three_cards, format_cards_for_display, format_cards_for_ai
from ai import get_tarot_reading

app = Flask(__name__)

configuration = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler       = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])

WELCOME_MESSAGE = """🔮 星詠みのルナのタロット占いへようこそ！

カードがあなたの未来を静かに語りかけます。

【使い方】
気になっていることを送ってください。

例：
・「仕事運を教えてほしい」
・「恋愛はどうなる？」
・「今月乗り越えるべきことは？」

思いのままに話しかけてみてください ✨"""

HELP_MESSAGE = """📖 使い方

占いたい内容を送るだけ！
例：「転職すべき？」「彼との関係は？」

ルナが3枚のカードを引き、
過去・現在・未来を読み解きます。

【コマンド】
「タロット」「はじめる」→ ウェルカムメッセージ
「ヘルプ」「使い方」　 → この説明 🌙"""

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    text = event.message.text.strip()
    if text in ["タロット", "占い", "はじめる", "スタート", "start", "hello", "こんにちは"]:
        reply = WELCOME_MESSAGE
    elif text in ["ヘルプ", "使い方", "help", "?"]:
        reply = HELP_MESSAGE
    elif len(text) >= 5:
        cards = draw_three_cards()
        display = format_cards_for_display(cards)
        reading = get_tarot_reading(
            question=text,
            cards_text=format_cards_for_ai(cards)
        )
        reply = f"{display}\n\n{reading}"
    else:
        reply = "🔮 占いたいことを教えてください！\n例：「仕事運を教えて」「今月の恋愛運は？」"

    with ApiClient(configuration) as api_client:
        MessagingApi(api_client).reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply)]
            )
        )
from fastapi import FastAPI, Request, HTTPException
import httpx
import os
import hmac
import hashlib
import base64
import json

app = FastAPI()

# 環境変数
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
DIFY_API_KEY = os.getenv("DIFY_API_KEY")
DIFY_API_URL = os.getenv("DIFY_API_URL")


# LINE署名検証
def verify_signature(body, signature):
    hash = hmac.new(
        LINE_CHANNEL_SECRET.encode('utf-8'),
        body,
        hashlib.sha256
    ).digest()
    expected_signature = base64.b64encode(hash).decode()

    return hmac.compare_digest(expected_signature, signature)


# Difyに送信
async def send_to_dify(user_id, message):
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": {},
        "query": message,
        "response_mode": "blocking",
        "user": user_id
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(DIFY_API_URL, headers=headers, json=payload)
        data = response.json()

    return data.get("answer", "すみません、うまく占えませんでした。")


# LINEに返信
async def reply_to_line(reply_token, text):
    url = "https://api.line.me/v2/bot/message/reply"

    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        await client.post(url, headers=headers, json=body)


# Webhook
@app.post("/callback")
async def callback(request: Request):
    body = await request.body()
    signature = request.headers.get("X-Line-Signature")

    # 署名チェック
    if not verify_signature(body, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    data = json.loads(body)

    events = data.get("events", [])

    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_id = event["source"]["userId"]
            reply_token = event["replyToken"]
            user_message = event["message"]["text"]

            # Difyに送信
            ai_response = await send_to_dify(user_id, user_message)

            # LINEに返信
            await reply_to_line(reply_token, ai_response)

    return {"status": "ok"}
if __name__ == "__main__":
    app.run(port=8000, debug=True)
