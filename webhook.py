"""
LINE AI タロット占いBot
Vercel Serverless Function エントリーポイント
"""
import sys
import os

# lib/ を import パスに追加（Vercel serverless 対策）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError

from lib.tarot import draw_three_cards, format_cards_for_display, format_cards_for_ai
from lib.ai import get_tarot_reading

# ── 初期化 ────────────────────────────────────────────────────────
app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET       = os.environ["LINE_CHANNEL_SECRET"]

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler       = WebhookHandler(LINE_CHANNEL_SECRET)

# ── ウェルカムメッセージ ──────────────────────────────────────────
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

1. 占いたい内容を送るだけ！
   例：「転職すべき？」「彼との関係は？」

2. ルナが3枚のカードを引き、
   過去・現在・未来を読み解きます。

【コマンド一覧】
・「タロット」「はじめる」→ ウェルカムメッセージ
・「ヘルプ」「使い方」    → この説明

何でも気軽に話しかけてください 🌙"""

MIN_QUESTION_LENGTH = 5  # この文字数以上を「質問」とみなす


# ── Webhook エンドポイント ─────────────────────────────────────────
@app.route("/api/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body      = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


# ── メッセージイベント処理 ────────────────────────────────────────
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    user_text = event.message.text.strip()

    # コマンド判定
    if user_text in ["タロット", "占い", "はじめる", "スタート", "start", "hello", "こんにちは"]:
        reply_text = WELCOME_MESSAGE

    elif user_text in ["ヘルプ", "使い方", "help", "?"]:
        reply_text = HELP_MESSAGE

    elif len(user_text) >= MIN_QUESTION_LENGTH:
        # ── タロットリーディング実行 ──
        cards = draw_three_cards()

        card_display = format_cards_for_display(cards)
        cards_for_ai = format_cards_for_ai(cards)

        reading = get_tarot_reading(question=user_text, cards_text=cards_for_ai)

        reply_text = f"{card_display}\n\n{reading}"

    else:
        reply_text = (
            "🔮 占いたいことを教えてください！\n"
            "例：「仕事運を教えて」「今月の恋愛運は？」\n\n"
            "「ヘルプ」と送ると使い方を確認できます。"
        )

    # LINE へ返信
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)],
            )
        )


# ── ローカル開発用 ────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(port=8000, debug=True)
