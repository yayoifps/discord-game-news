"""Discord Webhookへ、カテゴリごとにまとめたembedを1メッセージで送信する。"""

import requests

from sources import CATEGORY_COLOR, CATEGORY_LABEL

# 1embedのdescription上限は4096文字、1メッセージの全embed合計は6000文字(Discordの仕様)。
# カテゴリは最大3つなので、1embedあたりの目安上限を1700文字にして合計6000文字に収まるようにする。
EMBED_DESC_LIMIT = 1700
CATEGORY_ORDER = ["japan", "overseas", "security"]
TIMEOUT = 10


def _build_category_embed(category: str, articles: list) -> dict:
    lines = []
    included = 0
    for a in articles:
        parts = [f"**[{a['title']}]({a['link']})**"]
        if a["summary"]:
            parts.append(a["summary"])
        parts.append(f"*出典: {a['source']}*")
        entry = "\n".join(parts)
        candidate_len = sum(len(x) for x in lines) + len(entry) + len(lines) * 2
        if lines and candidate_len > EMBED_DESC_LIMIT:
            break
        lines.append(entry)
        included += 1

    remaining = len(articles) - included
    description = "\n\n".join(lines)
    if remaining > 0:
        description += f"\n\n*(他 {remaining} 件は省略)*"

    return {
        "title": f"{CATEGORY_LABEL[category]}ニュース",
        "description": description[:4096],
        "color": CATEGORY_COLOR[category],
    }


def send_articles(webhook_url: str, articles: list, dry_run: bool = False) -> list:
    """全articlesをカテゴリごとのembedにまとめ、1メッセージとしてWebhookへ送信する。

    実際にDiscordへの送信(またはdry-run)が成功した記事のリストを返す。
    呼び出し側はこの戻り値だけを「送信済み」として記録すること。
    """
    if not articles:
        return []

    grouped: dict[str, list] = {}
    for a in articles:
        grouped.setdefault(a["category"], []).append(a)

    embeds = [
        _build_category_embed(cat, grouped[cat])
        for cat in CATEGORY_ORDER
        if cat in grouped
    ]

    payload = {
        "username": "ゲーム業界ニュース",
        "embeds": embeds,
    }

    if dry_run:
        print("[dry-run] 1メッセージにまとめて送信予定:")
        for e in embeds:
            print(f"\n=== {e['title']} ===")
            print(e["description"])
        return articles

    try:
        resp = requests.post(webhook_url, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"Discordへの送信に失敗しました: {e}")
        return []

    return articles
