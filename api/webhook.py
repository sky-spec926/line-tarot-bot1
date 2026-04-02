import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os as _os
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
configuration = Configuration(access_token=_os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler       = WebhookHandler(_os.environ["LINE_CHANNEL_SECRET"])

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

@app.route("/api/webhook", methods=["POST"])
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
        reading = get_tarot_reading(question=text, cards_text=format_cards_for_ai(cards))
        reply = f"{display}\n\n{reading}"
    else:
        reply = "🔮 占いたいことを教えてください！\n例：「仕事運を教えて」「今月の恋愛運は？」"
    with ApiClient(configuration) as api_client:
        MessagingApi(api_client).reply_message_with_http_info(
            ReplyMessageRequest(reply_token=event.reply_token, messages=[TextMessage(text=reply)])
        )
