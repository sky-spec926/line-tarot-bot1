# 🔮 LINE AI タロット占いBot

Claude API × LINE Messaging API で動くタロット占いBot。
Vercel にデプロイするだけで誰でも使えます。

---

## ファイル構成

```
line-tarot-bot/
├── api/
│   └── webhook.py     ← Vercel Serverless Function（メイン）
├── lib/
│   ├── tarot.py       ← タロットカード78枚 + 引くロジック
│   └── ai.py          ← Claude API 連携
├── vercel.json        ← Vercel デプロイ設定
├── requirements.txt   ← Python依存パッケージ
└── .env.example       ← 環境変数テンプレート
```

---

## デプロイ手順

### ① 必要なアカウント・APIキーを準備

| 必要なもの | 取得場所 |
|---|---|
| LINE Channel Access Token | [LINE Developers](https://developers.line.biz/) |
| LINE Channel Secret | 同上 |
| Anthropic API Key | [console.anthropic.com](https://console.anthropic.com/) |

---

### ② GitHub にアップロード

```bash
# リポジトリを作成してpush
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/あなたのユーザー名/line-tarot-bot.git
git push -u origin main
```

---

### ③ Vercel にデプロイ

1. [vercel.com](https://vercel.com) にアクセスしてGitHubアカウントでログイン
2. 「New Project」→ GitHubリポジトリを選択してインポート
3. **Environment Variables（環境変数）** に以下を設定：

```
LINE_CHANNEL_ACCESS_TOKEN = xxxxxxxxxxxxxxxxxxxxxx
LINE_CHANNEL_SECRET       = xxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY         = sk-ant-xxxxxxxxxxxxxxxxxx
```

4. 「Deploy」ボタンを押す
5. デプロイ完了後、表示されるURLをコピー
   例：`https://line-tarot-bot-xxx.vercel.app`

---

### ④ LINE Webhook URL を設定

1. [LINE Developers コンソール](https://developers.line.biz/) を開く
2. チャネル → Messaging API 設定 → Webhook URL に入力：

```
https://line-tarot-bot-xxx.vercel.app/api/webhook
```

3. 「Verify」ボタンで成功を確認 ✅
4. 「Webhookの利用」をオン

---

### ⑤ 動作確認

LINEで公式アカウントに「タロット」と送信 → ウェルカムメッセージが返ってきたら完成！

---

## 使い方（ユーザー向け）

| 送るメッセージ | 動作 |
|---|---|
| 「タロット」「はじめる」 | ウェルカムメッセージを表示 |
| 「ヘルプ」「使い方」 | 使い方を表示 |
| 質問文（5文字以上） | タロット占いを実行 |

---

## ⚠️ 注意事項

- Vercel 無料プランの**タイムアウトは10秒**です。Claude APIの応答が遅い場合は稀にエラーになることがあります。有料プラン（Pro: $20/月）にするとタイムアウトが60秒に延びます。
- API利用コストの目安：1回の占い ≈ 約0.3円（Claude API料金）

---

## マネタイズ（次のステップ）

- **無料期間**：まず友達を増やす（最初の3ヶ月）
- **有料プラン**：月30回以上は¥500/月（Stripeで決済リンク発行）
- **単発課金**：詳細鑑定（10枚ケルト十字）¥300
- **デイリー配信**：LINE公式の「リッチメニュー」で毎朝の運勢を有料提供
