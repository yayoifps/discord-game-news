"""Discord Webhookへ、記事ごとのembed(サムネイル付き)を1メッセージにまとめて送信する。"""

import requests

from sources import CATEGORY_COLOR, CATEGORY_LABEL

MAX_EMBEDS = 10  # Discordの1メッセージあたりembed上限
TIMEOUT = 10


def _build_embed(article: dict) -> dict:
    embed = {
        "title": article["title"][:256],
        "url": article["link"],
        "color": CATEGORY_COLOR[article["category"]],
        "footer": {"text": f"{CATEGORY_LABEL[article['category']]} ・ {article['source']}"},
    }
    if article["summary"]:
        embed["description"] = article["summary"][:4096]
    if article.get("image_url"):
        embed["thumbnail"] = {"url": article["image_url"]}
    return embed


def send_articles(webhook_url: str, articles: list, dry_run: bool = False) -> list:
    """articlesを記事ごとのembedにまとめ、1メッセージとしてWebhookへ送信する。

    実際にDiscordへの送信(またはdry-run)が成功した記事のリストを返す。
    呼び出し側はこの戻り値だけを「送信済み」として記録すること。
    """
    if not articles:
        return []

    articles = articles[:MAX_EMBEDS]
    payload = {
        "username": "ゲーム業界ニュース",
        "embeds": [_build_embed(a) for a in articles],
    }

    if dry_run:
        print("[dry-run] 1メッセージにまとめて送信予定:")
        for a in articles:
            img = " [画像あり]" if a.get("image_url") else ""
            print(f"  - [{CATEGORY_LABEL[a['category']]}/{a['source']}] {a['title']}{img}")
        return articles

    try:
        resp = requests.post(webhook_url, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Discordへの送信に失敗しました: {e}")
        return []

    return articles
