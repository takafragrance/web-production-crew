"""
Web制作向け自律型AIエージェント
CrewAI + Serper API でリサーチから HTML/CSS/JS 実装までを一気通貫で実行する。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool

# Figmaデザイン実装向けコーディング規約（エージェント共通）
CODING_REQUIREMENTS = """
【ファイル構成】
- HTML: index.php
- CSS: style.css
- JavaScript: org-top.js
- 画像: すべて images/ 配下を参照（例: ./images/mv.webp）
- プロジェクトに header.php / footer.php や css/ js/ 分割がある場合も、クラス名・要件は本規約に準拠

【レスポンシブ】
- PC・モバイル・メニューを統合したレスポンシブで実装する
- ブレイクポイントは range syntax: @media (width <= 768px)
- メディアクエリ内のサイズは可能な限り vw に変換する（固定 px のまま残さない）

【CSS】
- :root で --main-color / --accent-color / --section-padding / インナー幅などを定義し統一管理
- インナー幅: PC 1140px / スマホ 89.3333vw
- .section__inner（または同等）は width + margin: 0 auto で中央配置
- Flexbox / CSS Grid を適材適所で使用
- 主要画像（.main-view__img img 等）は width: 100% や aspect-ratio でアスペクト比を維持
- 命名は BEM（Block__Element--modifier）
- インデントは4スペース
- [class*=""] 等の共通化は積極利用。共通CSSは header / footer / section ごとに分け、サイト全体へ無差別適用しない

【HTML 共通構造】
header.org-header > .org-header__inner
main.l-main
  .main-view > h1.main-view__img > img / .main-view__txt
  section.section-wrapper--* > .section-inner--* > .ttl-box（h2.section-ttl / p.section-sub-ttl）+ 本文
footer.org-footer > .org-footer__inner
セクションごとに modifier でスタイルを制御する。

【JavaScript（org-top.js）】
- const / let のみ（var 禁止）
- IIFE または同等のレキシカル環境でグローバル汚染を防ぐ
- インデントは2スペース
- 見た目の制御は CSS クラスの付け外し。JS から style を多用しない
- innerHTML の無闇な使用禁止。textContent / classList / createElement を使う
- DOM 取得時は null チェック
- インライン <script> / onclick 等のインラインイベント禁止。addEventListener で設定
- HTML 内へのインライン script は禁止し、処理は org-top.js に集約

【禁止・品質】
- 独自のデザイン改変や不要機能追加をしない（ブリーフ／Figma指示を正とする）
- プレースホルダ（TODO / lorem / xxx）やダミー実装を残さない
- 秘密情報を埋め込まない
- フレームワーク・ビルドツールの導入はしない
""".strip()


def load_config() -> None:
    """環境変数を読み込み、必須キーの有無を検証する。"""
    load_dotenv()

    missing = [
        key
        for key in ("OPENAI_API_KEY", "SERPER_API_KEY")
        if not os.getenv(key) or os.getenv(key, "").startswith("your_")
    ]
    if missing:
        print(
            "エラー: 次の環境変数を .env に設定してください:\n"
            + "\n".join(f"  - {key}" for key in missing)
        )
        sys.exit(1)


def build_crew(topic: str, output_dir: Path) -> Crew:
    """Web制作クルーを組み立てる。"""
    search_tool = SerperDevTool()
    images_dir = output_dir / "images"
    images_dir.mkdir(exist_ok=True)

    php_path = output_dir / "index.php"
    css_path = output_dir / "style.css"
    js_path = output_dir / "org-top.js"

    researcher = Agent(
        role="Webリサーチャー",
        goal=(
            f"「{topic}」向けのWebサイトに必要な市場動向・競合・"
            "デザイントレンド・ユーザーニーズを調査する"
        ),
        backstory=(
            "デジタルマーケティングとUXリサーチの専門家。"
            "最新のWebトレンドと競合サイトを素早く把握し、"
            "制作チームがすぐ使える調査メモにまとめる。"
        ),
        tools=[search_tool],
        verbose=True,
        allow_delegation=False,
    )

    content_strategist = Agent(
        role="コンテンツストラテジスト",
        goal=(
            f"「{topic}」のサイト構成・ページ構成・コピー案を設計し、"
            "開発者が実装しやすいブリーフを作る"
        ),
        backstory=(
            "ブランドストーリーと情報設計に強いコンテンツ専門家。"
            "リサーチ結果を、見出し・セクション・CTAが明確な"
            "実装可能なサイト構成に落とし込む。"
            "HTMLは org-header / main-view / section-wrapper / org-footer の"
            "共通構造を前提にブリーフを書く。"
        ),
        verbose=True,
        allow_delegation=False,
    )

    web_developer = Agent(
        role="フロントエンド開発者",
        goal=(
            "コーディング規約に従い、レスポンシブな "
            "index.php / style.css / org-top.js を実装する"
        ),
        backstory=(
            "セマンティックHTML、BEM、CSS変数、モバイル対応を徹底する"
            "フロントエンドエンジニア。PHP拡張子でもマークアップはHTMLとして書き、"
            "CSS/JSは外部ファイルに分離する。インラインscript・インラインイベントは使わない。"
        ),
        verbose=True,
        allow_delegation=False,
    )

    qa_reviewer = Agent(
        role="QAレビュアー",
        goal=(
            "成果物の構成・コピー・コーディング規約準拠をレビューし、"
            "最終判定を出す"
        ),
        backstory=(
            "Web制作の品質管理担当。"
            "BEM・レスポンシブ・CSS変数・JS安全要件・ファイル構成を"
            "厳しくチェックする。"
        ),
        verbose=True,
        allow_delegation=False,
    )

    research_task = Task(
        description=(
            f"「{topic}」のWebサイト制作に向けて調査せよ。\n"
            "含める内容:\n"
            "1. ターゲットユーザーとニーズ\n"
            "2. 競合・類似サイトの特徴（検索結果から）\n"
            "3. 2024〜2026年のデザイン/UXトレンド\n"
            "4. 推奨カラー・タイポグラフィ・レイアウト方針"
            "（--main-color / --accent-color に落とせる粒度）\n"
            "5. 必須コンテンツ要素のリスト\n"
            "日本語で簡潔にまとめること。"
        ),
        expected_output="日本語の調査レポート（箇条書き中心、実装に使える粒度）",
        agent=researcher,
    )

    strategy_task = Task(
        description=(
            f"「{topic}」向けランディングページのサイト構成を作成せよ。\n"
            "含める内容:\n"
            "1. ページ目的と主要メッセージ\n"
            "2. セクション構成（ヒーロー〜フッター）。"
            "共通HTML構造（org-header / main-view / section-wrapper--"
            "modifier / org-footer）に沿って書く\n"
            "3. 各セクションの見出し・本文案・CTA文言\n"
            "4. 推奨CSS変数（色・余白）と画像ファイル名案（images/ 配下）\n"
            "5. 開発者向け実装メモ（レイアウト、メニュー、インタラクション）\n"
            "日本語で書くこと。"
        ),
        expected_output="実装可能なサイト構成ブリーフ（日本語）",
        agent=content_strategist,
        context=[research_task],
    )

    develop_php_task = Task(
        description=(
            "サイト構成ブリーフに基づき index.php を実装せよ。\n"
            f"{CODING_REQUIREMENTS}\n\n"
            "追加要件:\n"
            "- style.css と org-top.js を link / script で外部参照する"
            "（インライン style / script / イベント禁止）\n"
            "- 画像パスは ./images/ 配下\n"
            "- セマンティックなタグと適切な見出し階層\n"
            "- ヒーロー、特徴、実績/信頼、CTA、フッターを含める\n"
            "- 出力は PHP/HTML コードのみ（説明文や Markdown フェンス禁止）\n"
            f"- 最終成果物は {php_path} に保存する完成コードとする"
        ),
        expected_output="完成した index.php ソース（<!DOCTYPE html> または同等のマークアップから始まる）",
        agent=web_developer,
        context=[strategy_task],
        output_file=str(php_path),
    )

    develop_css_task = Task(
        description=(
            "index.php のマークアップに合わせた style.css を実装せよ。\n"
            f"{CODING_REQUIREMENTS}\n\n"
            "追加要件:\n"
            "- :root に --main-color / --accent-color / --section-padding /"
            " インナー幅（PC 1140px・SP 89.3333vw）を定義\n"
            "- .org-header / .org-footer / .section-wrapper 系の共通スタイルを"
            " パートごとに分けて記述\n"
            "- PC→SP は @media (width <= 768px) と vw 変換\n"
            "- インデントは4スペース\n"
            "- 出力は CSS コードのみ（説明文や Markdown フェンス禁止）\n"
            f"- 最終成果物は {css_path} に保存する完成コードとする"
        ),
        expected_output="完成した style.css ソース",
        agent=web_developer,
        context=[strategy_task, develop_php_task],
        output_file=str(css_path),
    )

    develop_js_task = Task(
        description=(
            "index.php に対応する org-top.js を実装せよ。\n"
            f"{CODING_REQUIREMENTS}\n\n"
            "追加要件:\n"
            "- モバイルメニュー開閉など、ブリーフで必要なインタラクションを実装\n"
            "- IIFE 内で記述し、addEventListener + classList で制御\n"
            "- インデントは2スペース\n"
            "- 不要なら最小限の安全な初期化のみでも可（空ファイルやダミー禁止）\n"
            "- 出力は JavaScript コードのみ（説明文や Markdown フェンス禁止）\n"
            f"- 最終成果物は {js_path} に保存する完成コードとする"
        ),
        expected_output="完成した org-top.js ソース",
        agent=web_developer,
        context=[strategy_task, develop_php_task],
        output_file=str(js_path),
    )

    review_task = Task(
        description=(
            "生成された index.php / style.css / org-top.js をレビューし、"
            "最終判定を出せ。\n"
            f"コーディング規約:\n{CODING_REQUIREMENTS}\n\n"
            "チェック項目:\n"
            "- ファイル構成と外部参照（インライン script/イベントが無いこと）\n"
            "- BEM・共通HTML構造・CSS変数・インナー幅\n"
            "- レスポンシブ（width <= 768px と vw）\n"
            "- JS の安全性（IIFE、nullチェック、innerHTML乱用なし）\n"
            "- 構成とメッセージの一貫性、CTAの明確さ\n"
            "最終出力は短いレビュー要約（日本語）とする。"
        ),
        expected_output="日本語の最終レビュー要約（合格/要改善と具体的コメント）",
        agent=qa_reviewer,
        context=[develop_php_task, develop_css_task, develop_js_task],
        output_file=str(output_dir / "review.md"),
    )

    return Crew(
        agents=[researcher, content_strategist, web_developer, qa_reviewer],
        tasks=[
            research_task,
            strategy_task,
            develop_php_task,
            develop_css_task,
            develop_js_task,
            review_task,
        ],
        process=Process.sequential,
        verbose=True,
    )


def main() -> None:
    load_config()

    topic = (
        " ".join(sys.argv[1:]).strip()
        if len(sys.argv) > 1
        else "地元の小さなカフェ向けコーポレートサイト"
    )

    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "images").mkdir(exist_ok=True)

    print(f"テーマ: {topic}")
    print("CrewAI エージェントを起動します...\n")

    crew = build_crew(topic, output_dir)
    result = crew.kickoff()

    print("\n===== 完了 =====")
    print(result)
    print(f"\n成果物ディレクトリ: {output_dir}")
    print("  - index.php / style.css / org-top.js / images/ / review.md")


if __name__ == "__main__":
    main()
