# Web Production Crew

CrewAI と Serper API を使った、Web制作向けの自律型AIエージェントです。

リサーチ → コンテンツ設計 → HTML実装 → QAレビュー を順に実行し、`output/` に成果物を保存します。

## エージェント構成

| 役割 | 担当 |
|------|------|
| Webリサーチャー | Serper で市場・競合・デザイントレンドを調査 |
| コンテンツストラテジスト | サイト構成・コピー・CTAを設計 |
| フロントエンド開発者 | 単一HTML（埋め込みCSS/JS）を実装 |
| QAレビュアー | 品質チェックと最終レビュー |

## セットアップ

```bash
# Python 3.10+ 推奨
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`.env.example` をコピーして `.env` を作成し、APIキーを設定します。

```bash
cp .env.example .env
```

必要キー:

- `OPENAI_API_KEY` … [OpenAI](https://platform.openai.com/api-keys)
- `SERPER_API_KEY` … [Serper](https://serper.dev)

## 実行

```bash
source .venv/bin/activate
python main.py
```

テーマを指定する場合:

```bash
python main.py "ヨガスタジオ向けランディングページ"
```

## 成果物

- `output/index.html` … 生成されたWebページ
- `output/review.md` … QAレビュー要約

## ライセンス

MIT
