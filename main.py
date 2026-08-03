"""
Web制作向け自律型AIエージェント
CrewAI + Serper API でリサーチからHTML実装までを一気通貫で実行する。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool


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
        ),
        verbose=True,
        allow_delegation=False,
    )

    web_developer = Agent(
        role="フロントエンド開発者",
        goal=(
            "モダンでレスポンシブな単一HTMLファイル"
            "（埋め込みCSS/JS含む）を実装する"
        ),
        backstory=(
            "セマンティックHTML、アクセシビリティ、モバイルファーストを重視する"
            "フロントエンドエンジニア。外部依存を最小限にし、"
            "そのままブラウザで開ける完成度の高いページを書く。"
        ),
        verbose=True,
        allow_delegation=False,
    )

    qa_reviewer = Agent(
        role="QAレビュアー",
        goal="成果物の構成・コピー・HTML品質をレビューし、最終版を確定する",
        backstory=(
            "Web制作の品質管理担当。"
            "情報の抜け、アクセシビリティ、レスポンシブ対応、"
            "CTAの明確さを厳しくチェックする。"
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
            "4. 推奨カラー・タイポグラフィ・レイアウト方針\n"
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
            "2. セクション構成（ヒーロー〜フッター）\n"
            "3. 各セクションの見出し・本文案・CTA文言\n"
            "4. 開発者向け実装メモ（レイアウト、インタラクション）\n"
            "日本語で書くこと。"
        ),
        expected_output="実装可能なサイト構成ブリーフ（日本語）",
        agent=content_strategist,
        context=[research_task],
    )

    html_path = output_dir / "index.html"
    develop_task = Task(
        description=(
            "サイト構成ブリーフに基づき、完成度の高い単一HTMLを実装せよ。\n"
            "要件:\n"
            "- 1ファイルにHTML/CSS/JSをまとめる\n"
            "- モバイルファーストのレスポンシブ対応\n"
            "- セマンティックなタグと適切な見出し階層\n"
            "- ヒーロー、特徴、実績/信頼、CTA、フッターを含める\n"
            "- 外部CDN依存は最小限（Google Fonts程度まで可）\n"
            "- 出力はHTMLコードのみ（説明文やMarkdownフェンス禁止）\n"
            f"- 最終成果物は {html_path} に保存できる完成コードとする"
        ),
        expected_output="完成したHTMLソースコード（<!DOCTYPE html> から始まる）",
        agent=web_developer,
        context=[strategy_task],
        output_file=str(html_path),
    )

    review_task = Task(
        description=(
            "生成されたHTMLをレビューし、必要なら改善点を反映した最終判定を出せ。\n"
            "チェック項目:\n"
            "- 構成とメッセージの一貫性\n"
            "- レスポンシブと可読性\n"
            "- CTAの明確さ\n"
            "- HTMLの妥当性（閉じタグ、見出し階層など）\n"
            "最終出力は短いレビュー要約（日本語）とする。"
        ),
        expected_output="日本語の最終レビュー要約（合格/要改善と具体的コメント）",
        agent=qa_reviewer,
        context=[develop_task],
        output_file=str(output_dir / "review.md"),
    )

    return Crew(
        agents=[researcher, content_strategist, web_developer, qa_reviewer],
        tasks=[research_task, strategy_task, develop_task, review_task],
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

    print(f"テーマ: {topic}")
    print("CrewAI エージェントを起動します...\n")

    crew = build_crew(topic, output_dir)
    result = crew.kickoff()

    print("\n===== 完了 =====")
    print(result)
    print(f"\n成果物ディレクトリ: {output_dir}")


if __name__ == "__main__":
    main()
