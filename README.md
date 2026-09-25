# Web Production Crew

CrewAI と Serper API を使った、Web制作向けの自律型AIエージェントです。

リサーチ → コンテンツ設計 → PHP/CSS/JS 実装 → QAレビュー を順に実行し、`output/` に成果物を保存します。

## エージェント構成

| 役割 | 担当 |
|------|------|
| Webリサーチャー | Serper で市場・競合・デザイントレンドを調査 |
| コンテンツストラテジスト | サイト構成・コピー・CTAを設計 |
| フロントエンド開発者 | `index.php` / `style.css` / `org-top.js` を実装 |
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

任意:

- `OPENAI_MODEL_NAME` … 例: `gpt-4o-mini`（未設定時は CrewAI / OpenAI のデフォルト）

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

実行後、`output/` に次が出力されます。

| ファイル | 内容 |
|----------|------|
| `research.md` | 調査レポート |
| `strategy.md` | サイト構成ブリーフ |
| `index.php` | マークアップ |
| `style.css` | スタイル |
| `org-top.js` | インタラクション |
| `images/` | プレースホルダ SVG（`mv.svg` など）。本番画像は差し替え前提 |
| `review.md` | QAレビュー要約 |

## 画像について

実写真は生成しません。起動時に `output/images/` へ簡易 SVG プレースホルダを置き、マークアップはそれらを参照します。差し替え時は同名ファイルを実アセットに置き換えてください。

## ライセンス

MIT（詳細は [LICENSE](LICENSE)）
