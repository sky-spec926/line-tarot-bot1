"""
タロットカードデータとカード引きロジック
"""
import random

# ── 大アルカナ（22枚）──────────────────────────────────────────
MAJOR_ARCANA = [
    "愚者", "魔術師", "女教皇", "女帝", "皇帝",
    "教皇", "恋人", "戦車", "力", "隠者",
    "運命の輪", "正義", "吊られた男", "死神", "節制",
    "悪魔", "塔", "星", "月", "太陽", "審判", "世界",
]

# ── 小アルカナ（56枚）──────────────────────────────────────────
SUITS = ["ワンド", "カップ", "ソード", "ペンタクル"]
RANKS = ["エース", "2", "3", "4", "5", "6", "7", "8", "9", "10",
         "ペイジ", "ナイト", "クイーン", "キング"]

MINOR_ARCANA = [f"{suit}の{rank}" for suit in SUITS for rank in RANKS]

# 全78枚
ALL_CARDS = MAJOR_ARCANA + MINOR_ARCANA


def draw_three_cards() -> dict:
    """
    過去・現在・未来の3枚を引く
    Returns:
        {
            "past":    {"name": "愚者", "orientation": "正位置"},
            "present": {"name": "星",   "orientation": "逆位置"},
            "future":  {"name": "太陽", "orientation": "正位置"},
        }
    """
    cards = random.sample(ALL_CARDS, 3)
    positions = ["past", "present", "future"]
    return {
        pos: {
            "name": card,
            "orientation": random.choice(["正位置", "逆位置"])
        }
        for pos, card in zip(positions, cards)
    }


def format_cards_for_display(cards: dict) -> str:
    """LINEメッセージ用のカード表示テキストを生成"""
    pos_labels = {"past": "過去", "present": "現在", "future": "未来"}
    lines = ["🃏 引いたカード"]
    for pos, label in pos_labels.items():
        c = cards[pos]
        lines.append(f"  {label}：{c['name']}（{c['orientation']}）")
    return "\n".join(lines)


def format_cards_for_ai(cards: dict) -> str:
    """AIプロンプト用のカード情報を生成"""
    pos_labels = {"past": "過去", "present": "現在", "future": "未来"}
    lines = []
    for pos, label in pos_labels.items():
        c = cards[pos]
        lines.append(f"・{label}：{c['name']}（{c['orientation']}）")
    return "\n".join(lines)
