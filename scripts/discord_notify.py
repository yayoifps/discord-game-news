"""Discord Webhookへembed形式でニュースを送信する。"""

import time

import requests

CHUNK_SIZE = 10  # 1メッセージあたりの最大embed数(Discordの上限)
SEND_INTERVAL_SEC = 1.5  # メッセージ間の送信間隔(レート制限対策)
TIMEOUT = 10


def _build_embed(article: dict) -> dict:
    return {
        "title": article["title"][:256],
        "url": article["link"],
        "description": article["summary"][:4096],
        "color": article["color"],
        "footer": {"text": f"{article['category_label']} ・ {article['source']}"},
    }


def send_articles(webhook_url: str, articles: list, dry_run: bool = False) -> list:
    """articlesを10件ずつのメッセージに分けてWebhookへ送信する。

    実際にDiscordへの送信(またはdry-run)が成功した記事のリストを返す。
    呼び出し側はこの戻り値だけを「送信済み」として記録すること。
    """
    sent_ok = []
    for i in range(0, len(articles), CHUNK_SIZE):
        chunk = articles[i : i + CHUNK_SIZE]
        payload = {
            "username": "ゲーム業界ニュース",
            "embeds": [_build_embed(a) for a in chunk],
        }

        if dry_run:
            print(f"[dry-run] {len(chunk)}件のembedを送信予定:")
            for a in chunk:
                print(f"  - [{a['category_label']}/{a['source']}] {a['title']}")
            sent_ok.extend(chunk)
            continue

        try:
            resp = requests.post(webhook_url, json=payload, timeout=TIMEOUT)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Discordへの送信に失敗しました: {e}")
            continue

        sent_ok.extend(chunk)

        if i + CHUNK_SIZE < len(articles):
            time.sleep(SEND_INTERVAL_SEC)

    return sent_ok
