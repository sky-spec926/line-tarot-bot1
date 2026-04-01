"""
Claude API を使ったタロット占いロジック
"""
import os
import anthropic

# Anthropic クライアント（起動時に一度だけ初期化）
_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


# ── 占い師のペルソナ ──────────────────────────────────────────────
SYSTEM_PROMPT = """あなたは「星詠みのルナ」という名のベテランタロット占い師です。

【キャラクター設定】
・温かく包容力のある語り口で、相談者に寄り添います
・スピリチュアルな表現を自然に使いつつ、具体的なアドバイスも届けます
・絵文字を適度に使い、LINEらしい親しみやすいメッセージを作ります
・ネガティブなカードも「乗り越えるためのメッセージ」として伝えます

【返答ルール】
・必ず日本語で返答する
・全体400文字以内に収める
・希望を感じさせる言葉で締めくくる"""


def get_tarot_reading(question: str, cards_text: str) -> str:
    """
    Claude にタロットリーディングを依頼する

    Args:
        question:   ユーザーの質問
        cards_text: format_cards_for_ai() で生成したカード情報

    Returns:
        占い結果テキスト
    """
    user_prompt = f"""【相談内容】
{question}

【引いたカード（過去・現在・未来）】
{cards_text}

上記のカードをもとに、以下の形式でリーディングしてください：

🔮 今日のリーディング
（3枚の流れを踏まえた具体的なメッセージを200文字程度で）

✨ ルナからのアドバイス
（行動につながる前向きな一言を100文字程度で）"""

    client = get_client()
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=700,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text
