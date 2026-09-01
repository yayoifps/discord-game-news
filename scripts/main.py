"""ゲーム業界ニュースをRSSから収集し、Discordに配信するメインスクリプト。

使い方:
    python main.py            # 収集して実際にDiscordへ送信
    python main.py --dry-run  # 送信はせず、内容をコンソールに表示するだけ
"""

import html
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import requests

from discord_notify import send_articles
from sources import FEEDS
from translate import translate_to_ja

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sent_articles.json"
# Discordの1メッセージあたりembed上限(10件)に合わせて、1回の配信件数もこれに揃える
MAX_ARTICLES_PER_RUN = 10
SUMMARY_MAX_LEN = 120
RETENTION_DAYS = 30
REQUEST_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (compatible; GameNewsBot/1.0)"

OG_IMAGE_PATTERNS = [
    re.compile(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"'),
    re.compile(r'<meta[^>]+content="([^"]+)"[^>]+property="og:image"'),
]


def load_sent() -> dict:
    if not DATA_FILE.exists():
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_sent(sent: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(sent, f, ensure_ascii=False, indent=2, sort_keys=True)


def prune_old(sent: dict) -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    pruned = {}
    for url, sent_at in sent.items():
        try:
            ts = datetime.fromisoformat(sent_at)
        except ValueError:
            continue
        if ts >= cutoff:
            pruned[url] = sent_at
    return pruned


def clean_text(raw: str) -> str:
    text = re.sub(r"<[^>]+>", "", raw or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def summarize(raw: str, max_len: int = SUMMARY_MAX_LEN) -> str:
    text = clean_text(raw)
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "…"


def fetch_feed_entries(feed_def: dict) -> list:
    try:
        resp = requests.get(
            feed_def["url"],
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        parsed = feedparser.parse(resp.content)
    except Exception as e:
        print(f"[警告] {feed_def['name']} の取得に失敗しました: {e}")
        return []
    return parsed.entries


def collect_new_articles(sent: dict) -> list:
    candidates = []
    for feed_def in FEEDS:
        for entry in fetch_feed_entries(feed_def):
            link = entry.get("link")
            if not link or link in sent:
                continue
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            candidates.append((published, feed_def, entry))

    candidates.sort(key=lambda c: c[0] or time.gmtime(0), reverse=True)
    return candidates[:MAX_ARTICLES_PER_RUN]


def extract_image_url(entry: dict) -> str:
    """記事のサムネイル画像URLを取得する。見つからなければ空文字列。"""
    media_thumbnail = entry.get("media_thumbnail")
    if media_thumbnail and media_thumbnail[0].get("url"):
        return media_thumbnail[0]["url"]

    for m in entry.get("media_content", []):
        m_type = m.get("type", "")
        if m.get("url") and (not m_type or m_type.startswith("image")):
            return m["url"]

    for link in entry.get("links", []):
        if link.get("rel") == "enclosure" and link.get("type", "").startswith("image"):
            return link.get("href", "")

    # 本文HTML(summary)に埋め込まれたimgタグから拾う(AUTOMATON等)
    match = re.search(r'<img[^>]+src="([^"]+)"', entry.get("summary", "") or "")
    if match:
        return match.group(1)

    return ""


def fetch_og_image(url: str) -> str:
    """RSSに画像が無い場合のフォールバック: 記事ページのOGP画像(og:image)を取得する。

    取得できなければ(通信失敗・見つからない等)空文字列を返し、処理は継続する。
    """
    if not url:
        return ""
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException:
        return ""

    for pattern in OG_IMAGE_PATTERNS:
        match = pattern.search(resp.text)
        if match:
            return match.group(1)
    return ""


def build_article(feed_def: dict, entry: dict) -> dict:
    title = clean_text(entry.get("title", "(タイトルなし)"))
    summary = summarize(entry.get("summary", "") or entry.get("description", ""))
    image_url = extract_image_url(entry) or fetch_og_image(entry.get("link", ""))

    if feed_def["lang"] == "en":
        title = translate_to_ja(title)
        if summary:
            summary = translate_to_ja(summary)

    return {
        "title": title,
        "summary": summary,  # RSSに概要が無いソースでは空文字列になりうる
        "link": entry.get("link", ""),
        "source": feed_def["name"],
        "category": feed_def["category"],
        "image_url": image_url,
    }


def main():
    dry_run = "--dry-run" in sys.argv

    sent = prune_old(load_sent())
    candidates = collect_new_articles(sent)

    if not candidates:
        print("新着記事はありませんでした。")
        return

    articles = [build_article(feed_def, entry) for _, feed_def, entry in candidates]

    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not dry_run and not webhook_url:
        print("環境変数 DISCORD_WEBHOOK_URL が設定されていません。", file=sys.stderr)
        sys.exit(1)

    sent_ok_articles = send_articles(webhook_url, articles, dry_run=dry_run)

    if not dry_run:
        now_iso = datetime.now(timezone.utc).isoformat()
        for a in sent_ok_articles:
            sent[a["link"]] = now_iso
        save_sent(sent)

    print(f"{len(sent_ok_articles)}/{len(articles)}件のニュースを配信しました。")


if __name__ == "__main__":
    main()
